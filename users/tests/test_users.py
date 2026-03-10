import pytest
from rest_framework.test import APIClient

from users.models import User


@pytest.mark.django_db
def test_user_registration():
    client = APIClient()

    data = {
        'email': 'newuser@test.com',
        'username': 'newuser',
        'password': 'strongpass123'
    }

    response = client.post('/api/users/register/', data)

    assert response.status_code == 201
    assert User.objects.filter(email='newuser@test.com').exists()


@pytest.mark.django_db
def test_user_can_get_jwt_token():
    user = User.objects.create_user(
        email='user@test.com',
        username='user',
        password='testpass123'
    )

    client = APIClient()
    response = client.post('/api/token/', {
        'email': 'user@test.com',
        'password': 'testpass123'
    })

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data