from celery import shared_task
from django.utils import timezone
from habits.models import Habit
from .services import send_telegram_message


@shared_task
def send_habit_reminders():
    now = timezone.localtime()
    current_time = now.time().replace(second=0, microsecond=0)

    habits = Habit.objects.select_related('user').filter(time__hour=current_time.hour, time__minute=current_time.minute)

    for habit in habits:
        if habit.user.telegram_chat_id:
            send_telegram_message(
                habit.user.telegram_chat_id,
                f'Напоминание: {habit.action} в {habit.time.strftime("%H:%M")} ({habit.place})'
            )