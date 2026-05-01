from parkingapp import create_app
from zoneinfo import ZoneInfo

flask_app = create_app()


#resources 1: add residents, resource 2: add and modifiy guest cards, resource 3: add SMS user, resource 4: add fined and locked





if __name__ == "__main__":
    flask_app.run(debug = True)