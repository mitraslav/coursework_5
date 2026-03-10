import pytest
from rest_framework.test import APIClient

from habits.models import Habit
from .factories import UserFactory, HabitFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    return UserFactory(password="testpass123")


@pytest.fixture
def another_user():
    return UserFactory(password="testpass123")


@pytest.fixture
def auth_client(user):
    client = APIClient()
    response = client.post(
        "/api/token/", {"email": user.email, "password": "testpass123"}
    )
    token = response.data["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    return client


@pytest.mark.django_db
def test_create_habit(auth_client):
    data = {
        "place": "Парк",
        "time": "09:00",
        "action": "Сделать зарядку",
        "is_pleasant": False,
        "periodicity": 1,
        "reward": "Кофе",
        "execution_time": 120,
        "is_public": False,
    }

    response = auth_client.post("/api/habits/", data)

    assert response.status_code == 201
    assert Habit.objects.count() == 1
    assert Habit.objects.first().action == "Сделать зарядку"


@pytest.mark.django_db
def test_cannot_set_reward_and_related_habit(auth_client, user):
    pleasant_habit = HabitFactory(user=user, is_pleasant=True, reward=None)

    data = {
        "place": "Парк",
        "time": "09:00",
        "action": "Прогулка",
        "is_pleasant": False,
        "periodicity": 1,
        "reward": "Десерт",
        "related_habit": pleasant_habit.id,
        "execution_time": 60,
        "is_public": False,
    }

    response = auth_client.post("/api/habits/", data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_execution_time_must_be_less_or_equal_120(auth_client):
    data = {
        "place": "Дом",
        "time": "07:00",
        "action": "Разминка",
        "is_pleasant": False,
        "periodicity": 1,
        "reward": "Чай",
        "execution_time": 121,
        "is_public": False,
    }

    response = auth_client.post("/api/habits/", data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_related_habit_must_be_pleasant(auth_client, user):
    not_pleasant_habit = HabitFactory(user=user, is_pleasant=False, reward="Награда")

    data = {
        "place": "Улица",
        "time": "18:00",
        "action": "Прогулка",
        "is_pleasant": False,
        "periodicity": 1,
        "related_habit": not_pleasant_habit.id,
        "execution_time": 60,
        "is_public": False,
    }

    response = auth_client.post("/api/habits/", data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_pleasant_habit_cannot_have_reward(auth_client):
    data = {
        "place": "Дом",
        "time": "20:00",
        "action": "Принять ванну",
        "is_pleasant": True,
        "periodicity": 1,
        "reward": "Свечка",
        "execution_time": 60,
        "is_public": False,
    }

    response = auth_client.post("/api/habits/", data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_pleasant_habit_cannot_have_related_habit(auth_client, user):
    pleasant_habit = HabitFactory(user=user, is_pleasant=True, reward=None)

    data = {
        "place": "Дом",
        "time": "21:00",
        "action": "Послушать музыку",
        "is_pleasant": True,
        "periodicity": 1,
        "related_habit": pleasant_habit.id,
        "execution_time": 60,
        "is_public": False,
    }

    response = auth_client.post("/api/habits/", data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_periodicity_must_be_not_more_than_7(auth_client):
    data = {
        "place": "Дом",
        "time": "10:00",
        "action": "Чтение",
        "is_pleasant": False,
        "periodicity": 8,
        "reward": "Кофе",
        "execution_time": 60,
        "is_public": False,
    }

    response = auth_client.post("/api/habits/", data)

    assert response.status_code == 400


@pytest.mark.django_db
def test_user_sees_only_own_habits(auth_client, user, another_user):
    HabitFactory(user=user, action="Моя привычка 1")
    HabitFactory(user=user, action="Моя привычка 2")
    HabitFactory(user=another_user, action="Чужая привычка")

    response = auth_client.get("/api/habits/")

    assert response.status_code == 200
    actions = [item["action"] for item in response.data["results"]]
    assert "Моя привычка 1" in actions
    assert "Моя привычка 2" in actions
    assert "Чужая привычка" not in actions


@pytest.mark.django_db
def test_public_habits_list(client, user, another_user):
    HabitFactory(user=user, is_public=True, action="Публичная 1")
    HabitFactory(user=another_user, is_public=True, action="Публичная 2")
    HabitFactory(user=another_user, is_public=False, action="Приватная")

    response = client.get("/api/habits/public/")

    assert response.status_code == 200
    actions = [item["action"] for item in response.data["results"]]
    assert "Публичная 1" in actions
    assert "Публичная 2" in actions
    assert "Приватная" not in actions


@pytest.mark.django_db
def test_user_cannot_update_another_users_habit(auth_client, another_user):
    other_habit = HabitFactory(user=another_user, action="Чужая привычка")

    response = auth_client.patch(
        f"/api/habits/{other_habit.id}/", {"action": "Изменено"}, format="json"
    )

    assert response.status_code in (403, 404)


@pytest.mark.django_db
def test_user_cannot_update_foreign_habit(auth_client, another_user):
    other_habit = HabitFactory(user=another_user, action="Чужая привычка")

    response = auth_client.patch(
        f"/api/habits/{other_habit.id}/", {"action": "Изменено"}, format="json"
    )

    assert response.status_code in (403, 404)


@pytest.mark.django_db
def test_user_cannot_delete_another_users_habit(auth_client, another_user):
    other_habit = HabitFactory(user=another_user)

    response = auth_client.delete(f"/api/habits/{other_habit.id}/")

    assert response.status_code in (403, 404)


@pytest.mark.django_db
def test_user_can_delete_own_habit(auth_client, user):
    habit = HabitFactory(user=user)

    response = auth_client.delete(f"/api/habits/{habit.id}/")

    assert response.status_code == 204
    assert not Habit.objects.filter(id=habit.id).exists()


@pytest.mark.django_db
def test_habits_pagination(auth_client, user):
    for i in range(6):
        HabitFactory(user=user, action=f"Привычка {i}")

    response = auth_client.get("/api/habits/")

    assert response.status_code == 200
    assert "results" in response.data
    assert len(response.data["results"]) == 5
