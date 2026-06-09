__________________________________ParkingApp (Initial release)_____________________________________________________________________________________



Live demo: https://skopjeparking.duckdns.org


__________________________________QUICK START______________________________________________________________________________________________________


git clone https://github.com/ViktorAntevski/ParkingApp  
cd parkingapp  
pip install -r requirements.txt  
python app.py  


____________________________________STATUS__________________________________________________________________________________________________________


- Educational project
- Deployed prototype
- Under active development


___________________________________PURPOSE_________________________________________________________________________________________________________


The purpose of the web application is to provide backend logic that simulates a parking metering system. The system is split into two authentication domains,
which provide functionality for two user groups: parking clients (hereafter “user base” or “users”) and operators.  
The authenticated users can use the following services:
-	Hourly Parking – non-resident users can use a parking spot short term by applying for a parking metering session 
-	Register a resident vehicle – residents who are eligible for a parking spot throughout the year, can register their vehicle as a resident’s vehicle in the system
-	Monthly subscription – non-resident users can subscribe for a parking spot on a monthly basis
The operators enforce the valid usage of the parking premises by “scanning” the parked vehicles’ registration plates and checking them against the data base of the system.


___________________________________FEATURES_________________________________________________________________________________________________________


- User registration and authentication
- Secure email verification using token-based links  
- Role-based access (user/parking operator)
- Parking services management and invoicing


___________________________________MODELS__________________________________________________________________________________________________________


User – stores user data after successful signup. UserMixin inherited.  Two-way Relationship with EmailVerification.
Columns “username” and “email_address” are unique and “password hash” is indexed(index).
get_id method is overridden so that it includes a prefix “user:”.   

Operator – stores operator data. User mixin is inherited.  
 get_id method is overridden so that it includes a prefix “user:” which is to be stored in session to discriminate between the two auth domains: “user:” and “operator”.
“username” is unique and “password” is indexed.  

EmailVerification – Used to temporarily store tokens and token expiry date.  
 “token” column is unique. Relationship with User.   

ActiveRegistrationPlate – Pools the active registration plates and other common columns from across all the services.  
Service-specific columns are stored in a separate table for each service. This is the table which the operator queries
to check by registration plate if the vehicle is validly parked(independent of service type).  
Relationship with HourlyParkingInvoice, MontlySub and Resident.  

HourlyParkingInvoice – Stores check_in(check-in time) and vehicle_reg_plate (foreign key of ActiveRegistrationPlate)  

MonthlySub – Stores payed for month(Boolean) and vehicle_reg_plate(foreign key of ActiveRegistrationPlate).  

Resident – Stores registration_time, identity (indentity confirmed: boolean) and vehicle_reg_plate(foregin_key_of_ActiveRegistrationPlate)  


____________________________SERVICES AND API ROUTES_________________________________________________________________________________________________


Authentication (auth_service.{service}) ---------------------    

create_user via the UserSignUp [post] route  
The user signs up with a username, password, email address and other personal data. Rules regarding the content of the required fields are enforced here.
A verification link containing a 32-bit token is sent to the provided e-mail. After submitting successfully, a toast message is displayed.
A user=User() is written in the db. A password hash is generated and stored using UserMixin methods.

verify_email via the VerifyEmail [get] route  
Accessed through the e-mail verification link provided by the flask-mail module to a pending user. Upon success, a toast message is displayed to confirm that the user
is successfully verified. User.is_verified is set to true. The verification state in the db for that user is deleted.

resend via the VerificationResend [post] route  
Sends another e-mail with a token-based link. The e-mail entered should be identical user's e-mail. A rate limit of 1 resend per minute is applied.

user_login via the UserLogin [post] route  
The user logs in using his username and password credentials using the Flask-login’s login_user. Upon successful login, a toast message is displayed.

logout_user via UserLogout [post] route  

logout_user via OperatorLogout [post] route  

User services user_service.service) ----------------------------------------------------------------------  
decorated with: [login_required, user_required, verified_required] 

hourly_parking via the HourlyParking [post] route  
Zone and plate arguments are parsed and checked against validation enforcement rules. The input is stored in the ActiveRegistrationPlate and HourlyParkingInvoice.

stop_hourly_parking via the StopHourlyParking [post] route  
Queries ActiveRegistrationPlate and HourlyParkingInvoice. Calculates the final amount to be invoiced to the user, depending on the metered hours and zone rates.
Deletes the plates from ActiveRegistrationPlate.

register_resident via the RegisterResident[post] route  
Zone and plate arguments are parsed and checked against validation enforcement rules. The input is stored in the ActiveRegistrationPlate and Resident tables.

Operator services (operator_service.service) -------------------------------------------------------------  
decorated with: [login_required, operator_required]

plate_check via the PlateCheck [post] route    
Parses the zone and plate input and queries ActiveRegistrationPlate. If found – {“message”: “OK”}, if not found: {“message”: “Fine the subject”}.

change_zone via the ChangeZone [post] route    
Changes the current working zone of the operator in the server-side session, stored under the key “operator_zone”.


___________________________TEMPLATES________________________________________________________________________________________________________________


base/auth.html - pre-login template  
base/dashboard.html - user's dashboard template - presents the user username and logout button(UserLogout route) through out the user session
base/operator_dashboard.html - operator's dashboard template - presents the operator username, "logout" button(OperatorLogout route) through out the user session
and the current working zone and "change zone" button (ChangeZone route).  

homepage.html - provides the url links to all the authentication services.   
 authentication service pages: signup.html; login.html; verify.html; operator_login.html  

decorated with:  [login_required, user_required, verified_required]   
dashboard.html - provides the url links to all the user services.  
user service pages:dashboard_hourly_parking.html; dashboard_register_residents.html; dashboard_stopparking.html; dashboard_subsmonthly.html - provide a form and submit button to
the corresponding routes.

decorated with: [login_required, operator_required]  
operator_dashboard.html - provides the url links to all the operator services.
operator service pages: operator_dashboard_inspect


__________________________TECH STACK___________________________________________________________________________________________________________________


- Backend: Python (Flask)
- Database: SQLite
- Server: Gunicorn
- Web server: Nginx
- Deployment: Ubuntu (Linux)


_____________________DEPLOYMENT OVERVIEW_______________________________________________________________________________________________________________


The application is deployed using:

- Nginx as a reverse proxy forwarding requests to Gunicorn
- Gunicorn serving the backend application
- Systemd managing the Gunicorn process
- HTTPS enabled via Let's Encrypt

Architecture:

Client -> Nginx -> Gunicorn -> App -> Database

**For further details, read deployment.md


_____________________FUTURE IMPROVEMENTS_____________________________________________________________________________________________________________


Testing

Asign unit tests
-Stress test with k6 for expected peak-hour requests rate 

Observability and maintanence

-Hook Prometheus to montior: lathency, traffic, errors and resource usage.
-Add a crone job to clean unused data (invalid tokens, inactive users and others, inactive subscriptions)

External services

-Connect the app to an external online payment service  
-Connect the app to an external biometric verification service for verification of residents' data  
-Send email notification for metering-in-progress reminders for hourly sessions and monthly subscriptions    

Analytics

-Extend the db to store analytics such as occupied lot-hours, monthly revenue per zone, monthly revenue per service and other











