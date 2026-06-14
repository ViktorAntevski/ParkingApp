from parkingapp.services import auth_services
from unittest.mock import patch
from parkingapp.services import auth_services

def test_sign_up_success() -> None:
    args = {"username": "vian",
            "password": "password",
            "name_surname": "Viktor Antevski",
            "address": "ASNOM 80/20",
            "phone_number": "076433888",
            "email_address": "vantevski1@gmail.com",
            "ID_card": "34235493232"
            }

    response, status = auth_services.sign_up(args)

    assert status == 201
    assert response["message"] == "A verification link has been sent to your e-mail"
    assert isinstance(response["user_id"], int)
    assert response["user_id"] > 0
    assert response["email"] == args["email_address"]



@patch("parkingapp.services.auth_services.send_email")
@patch("parkingapp.services.auth_services.db.session")
@patch("parkingapp.services.auth_services.User")
def test_sign_up_success(mock_user_class, mock_db, mock_email, valid_signup_args):

    # No existing username or email
    mock_db.execute.return_value.scalar_one_or_none.return_value = None

    # Mock user object and ID (simulate flush assigning ID)
    mock_user = mock_user_class.return_value
    mock_user.id = 1
    mock_user.email_address = valid_signup_args["email_address"]

    response, status = auth_services.sign_up(valid_signup_args)

    assert status == 201
    assert response["email"] == valid_signup_args["email_address"]
    assert response["user_id"] == 1

    mock_email.assert_called_once()
    mock_db.commit.assert_called_once()
