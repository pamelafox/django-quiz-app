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

This project has devcontainer support, so you can open it in Github Codespaces or local VS Code with the Dev Containers extension. If you're unable to open the devcontainer,
then it's best to first [create a Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate that.

1. Install the requirements:

```shell
pip install -r requirements.txt
```

2. Create an `.env` file using `.env.sample` as a guide. Set the value of `DBNAME` to the name of an existing database in your local PostgreSQL instance. Set the values of `DBHOST`, `DBUSER`, and `DBPASS` as appropriate for your local PostgreSQL instance. If you're in the devcontainer, copy the values from `.env.sample.devcontainer`.

3. Run the migrations:

```
python manage.py migrate
```

4. Run the local server:

```
python manage.py runserver
```

5. Navigate to "/quizzes" (since no "/" route is defined) to verify server is working.

### Admin

This app comes with the built-in Django admin.

1. Create a superuser:

```
python manage.py createsuperuser
```

2. Restart the server and navigate to "/admin"

3. Login with the superuser credentials.

### Testing

Run tests:

```
python manage.py collectstatic
coverage run --source='.' manage.py test quizzes
coverage report
```

The same tests are also run as a Github action.


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
