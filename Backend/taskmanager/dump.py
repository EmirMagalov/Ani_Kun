import os
import django
from django.core.management import call_command

# Подключаем Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "taskmanager.settings")
django.setup()

# Создаём дамп
with open("full_backup.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", "--natural-foreign", "--natural-primary", "--all", "--indent", "2", stdout=f)

print("Дамп создан в full_backup.json")