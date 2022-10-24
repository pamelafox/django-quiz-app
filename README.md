[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&repo=pamelafox%2Fdjango-quiz-app)

# Quizzes app

An example Django app that serves quizzes and lets people know how they scored.
Quizzes and their questions are stored in a PostGreSQL database.
There is no user authentication or per-user data stored.

Try it out at:

```
https://django-example-quizsite.azurewebsites.net/quizzes/
```

## Local development

Install the requirements and Git hooks:

```
pip install -r requirements-dev.txt
pre-commit install
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

Run tests:

```
python manage.py collectstatic
coverage run --source='.' manage.py test quizzes
coverage report
```

## Deployment

This repository is set up for deployment on Azure App Service (w/PostGreSQL flexible server) using the configuration files in the `infra` folder.

1. Sign up for a [free Azure account](https://azure.microsoft.com/free/?WT.mc_id=python-79461-pamelafox)
2. Install the [Azure Dev CLI](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd?WT.mc_id=python-79461-pamelafox). (If you open this repository in Codespaces or with the VS Code Dev Containers extension, that part will be done for you.)
3. Provision and deploy all the resources:

```
azd up
```

4. To be able to access `/admin`, you'll need a Django superuser. Navigate to the Azure Portal for the App Service, select SSH, and run this command:

```
python manage.py createsuperuser
```
