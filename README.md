# Django-stripe
use stripe api for creating subscription for customer

##  How to run the app
1. Install all dependencies using the `pip install -r requirements.txt` command (recomended : use virtualenv).
2. Start the web server using the `python manage.py runserver` command. The app will be served at http://localhost:8000/ .
3.run command `stripe listen --forward-to localhost:8000/webhooks/stripe`.
4. go to http://localhost:8000/ and pay with email.
5.subscription id and customer id has save in database.
