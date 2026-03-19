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
        if self.room_name in self.rooms:
            users = self.rooms[self.room_name]["users"]
            # удаляем пользователя из комнаты
            users.pop(self.channel_name, None)

            # если комната пустая — удаляем её полностью
            if not users:
                del self.rooms[self.room_name]
            else:
                # обновляем участников только если кто-то остался
                await self.send_participants_update()

        # отключаем канал от группы
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")
        if action == "join":
            username = data.get("username")
            episode = data.get("episode")
            if self.room_name not in self.rooms:
                self.rooms[self.room_name] = {"users": {}, "current_episode": episode}

            self.rooms[self.room_name]["users"][self.channel_name] = username
            await self.send_participants_update()

            # отправляем новичку текущую серию, если она есть
            current_episode = self.rooms[self.room_name].get("current_episode")
            if current_episode is not None:
                await self.send(text_data=json.dumps({
                    "action": "change_episode",
                    "number": current_episode
                }))


        elif action == "time_update":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "time_update",
                    "user": data["user"],
                    "time": data["time"],
                    "pause": data.get('pause')
                }
            )
        elif action == "change_episode":
            num = data["number"]
            if self.room_name in self.rooms:
                self.rooms[self.room_name]["current_episode"] = num
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "change_episode",
                    "number": num,
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
        elif action == "pause_all":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "pause_all",
                    "time": data["time"],
                    "pause":data["pause"]
                }
            )
        elif action == "play_all":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "play_all",
                    "user": data["user"],
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
        room = self.rooms.get(self.room_name, {})
        users = room.get("users", {})
        participants = list(users.values())  # только список юзернеймов
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

    async def change_episode(self, event):
        await self.send(text_data=json.dumps({
            "action": "change_episode",
            "number": event["number"],
        }))

    async def play_all(self, event):
        await self.send(text_data=json.dumps({
            "action": "play_all",
            "user": event["user"],
        }))
    async def pause_all(self,event):
        await self.send(text_data=json.dumps({
            "action": "pause_all",
            "time": event["time"],
            "pause":event["pause"]
        }))
    async def video_event(self, event):
        await self.send(text_data=json.dumps(event["event"]))
