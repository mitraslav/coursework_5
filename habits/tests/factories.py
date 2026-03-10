import factory

from users.models import User
from habits.models import Habit


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@test.com")
    username = factory.Sequence(lambda n: f"user{n}")
    telegram_chat_id = factory.Sequence(lambda n: f"100000{n}")

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw_password = extracted or "testpass123"
        self.set_password(raw_password)
        if create:
            self.save()


class HabitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Habit

    user = factory.SubFactory(UserFactory)
    place = "Дом"
    time = "08:00"
    action = factory.Sequence(lambda n: f"Привычка {n}")
    is_pleasant = False
    related_habit = None
    periodicity = 1
    reward = "Шоколадка"
    execution_time = 60
    is_public = False
    last_notification_date = None
