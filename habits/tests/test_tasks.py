# habits/tests/test_tasks.py
import pytest
from unittest.mock import patch
from django.utils import timezone

from habits.tests.factories import HabitFactory, UserFactory
from telegram_bot.tasks import send_habit_reminders


@pytest.mark.django_db
@patch('telegram_bot.tasks.send_telegram_message')
def test_send_habit_reminder(mock_send_message):
    now = timezone.localtime()

    user = UserFactory(telegram_chat_id='123456789')
    habit = HabitFactory(
        user=user,
        time=now.strftime('%H:%M'),
        last_notification_date=None
    )

    send_habit_reminders()

    mock_send_message.assert_called_once()
    habit.refresh_from_db()
    assert habit.last_notification_date == timezone.localdate()
