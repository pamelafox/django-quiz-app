# Quizzes app

An example Django app that serves quizzes and lets people know how they scored.
Quizzes and their questions are stored in a PostGreSQL database.
There is no user authentication or per-user data stored.

Try it out at:

```
https://django-example-quizsite.azurewebsites.net/quizzes/
```

## Local development

Install the requirements:

```
pip install -r requirements.txt
```

Create a local PostGreSQL database called "quizsite"
and update `.env` with the relevant database details.

Run the migrations:

```
python manage.py migrate
```

Run the local server:

```
python manage.py runserver
```

## Deployment

The app is currently hosted on Microsoft Azure. Specifically:

* Azure App Service
* Azure Database for PostGreSQL flexible server

To deploy your own instance, follow the [tutorial for Django app + PostGreSQL deployment](https://docs.microsoft.com/en-us/azure/app-service/tutorial-python-postgresql-app?tabs=django%2Cwindows%2Cvscode-aztools%2Cterminal-bash%2Cazure-portal-access%2Cvscode-aztools-deploy%2Cdeploy-instructions-azportal%2Cdeploy-instructions--zip-azcli%2Cdeploy-instructions-curl-bash) but using this app instead of the sample app.

Make sure you specify the following environment variables in the App Service configuration: `DBHOST`, `DBNAME`, `DBPASS`, `DBUSER`. The previously linked tutorial shows how to set these.