import pytest
from unittest.mock import MagicMock

@pytest.fixture
def valid_signup_args():
    return {
        "username": "vian",
        "password": "verystrongpassword",
        "name_surname": "Viktor Antevski",
        "address": "ASNOM 80/20",
        "phone_number": "076433888",
        "email_address": "vantevski1@gmail.com",
        "ID_card": "34235493232"
    }

