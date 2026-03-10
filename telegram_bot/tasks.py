from celery import shared_task
from django.utils import timezone

from habits.models import Habit
from .services import send_telegram_message


@shared_task
def send_habit_reminders():
    now = timezone.localtime()
    today = timezone.localdate()

    habits = Habit.objects.select_related("user").filter(
        time__hour=now.hour, time__minute=now.minute
    )

    for habit in habits:
        if not habit.user.telegram_chat_id:
            continue

        if habit.last_notification_date == today:
            continue

        send_telegram_message(
            chat_id=habit.user.telegram_chat_id,
            text=f'Напоминание: {habit.action} в {habit.time.strftime("%H:%M")}',
        )

        habit.last_notification_date = today
        habit.save(update_fields=["last_notification_date"])
