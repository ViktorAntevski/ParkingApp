from parkingapp import create_app
from zoneinfo import ZoneInfo

flask_app = create_app()


if __name__ == "__main__":
    flask_app.run(debug = True)