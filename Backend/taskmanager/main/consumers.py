import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SyncConsumer(AsyncWebsocketConsumer):
    rooms = {}  # ключ: room_name, значение: dict channel_name -> username

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"room_{self.room_name}"



        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # сразу отправляем всех участников
        # await self.send_participants_update()



    async def disconnect(self, close_code):
        # Убираем пользователя из комнаты
        if self.room_name in self.rooms:
            self.rooms[self.room_name].pop(self.channel_name, None)

            # Если после удаления пользователей в комнате не осталось — удаляем комнату
            if not self.rooms[self.room_name]:
                del self.rooms[self.room_name]

            # Отправляем обновлённый список участников остальным
            await self.send_participants_update()

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "join":
            username = data.get("username")
            if self.room_name not in self.rooms:
                self.rooms[self.room_name] = {}
            self.rooms[self.room_name][self.channel_name] = username
            await self.send_participants_update()
        if action == "time_update":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "time_update",
                    "user": data["user"],
                    "time": data["time"],
                    "pause": data.get('pause')
                }
            )
        elif action == 'participants':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "participants",
                    "participants":data['participants']
                }
            )
        elif action == "synchron":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "synchron",
                    "user": data["user"],
                    "time": data["time"],
                }
            )
        elif action == "message":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "user": data["user"],
                    "content": data["content"],
                }
            )
        else:
            # fallback чтобы не падать
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "video_event",
                    "event": data,
                }
            )

    # === Handlers ===

    async def time_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "time_update",
            "user": event["user"],
            "time": event["time"],
            "pause":event["pause"]
        }))

    async def send_participants_update(self):
        participants = list(self.rooms.get(self.room_name, {}).values())
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "participants_update",
                "participants": participants
            }
        )

    async def participants_update(self, event):
        await self.send(text_data=json.dumps({
            "action": "participants",
            "participants": event["participants"]
        }))

    async def synchron(self, event):
        await self.send(text_data=json.dumps({
            "action": "synchron",
            "user": event["user"],
            "time": event["time"],
        }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "action": "message",
            "user": event["user"],
            "content": event["content"],
        }))

    async def video_event(self, event):
        await self.send(text_data=json.dumps(event["event"]))
