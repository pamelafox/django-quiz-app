[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&repo=pamelafox%2Fdjango-quiz-app)

# Quizzes app

An example Django app that serves quizzes and lets people know how they scored.
Quizzes and their questions are stored in a PostgreSQL database.
There is no user authentication or per-user data stored.

## Opening the project

This project has [Dev Container support](https://code.visualstudio.com/docs/devcontainers/containers), so it will be be setup automatically if you open it in Github Codespaces or in local VS Code with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

If you're not using one of those options for opening the project, then you'll need to:

1. Create a [Python virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments) and activate it.

2. Install the requirements:

    ```shell
    python3 -m pip install -r requirements-dev.txt
    ```

3. Install the pre-commit hooks:

    ```shell
    pre-commit install
    ```

## Local development


1. Create an `.env` file using `.env.sample` as a guide. Set the value of `DBNAME` to the name of an existing database in your local PostgreSQL instance. Set the values of `DBHOST`, `DBUSER`, and `DBPASS` as appropriate for your local PostgreSQL instance. If you're in the devcontainer, copy the values exactly from `.env.sample`.

2. Fill in a secret value for `SECRET_KEY`. You can use this command to generate an appropriate value.

    ```shell
    python -c 'import secrets; print(secrets.token_hex())'
    ```

3. Run the migrations:

    ```
    python3 manage.py migrate
    ```

4. Run the local server:

    ```
    python3 manage.py runserver
    ```

5. Navigate to "/quizzes" (since no "/" route is defined) to verify server is working.

### Admin

This app comes with the built-in Django admin interface.

1. Create a superuser:

```
python3 manage.py createsuperuser
```

2. Restart the server and navigate to "/admin"

3. Login with the superuser credentials.

### Testing

Run tests:

```
python3 manage.py collectstatic
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

### CI/CD pipeline

This project includes a Github workflow for deploying the resources to Azure
on every push to main. That workflow requires several Azure-related authentication secrets
to be stored as Github action secrets. To set that up, run:

```shell
azd pipeline config
```

## Security

It is important to secure the databases in web applications to prevent unwanted data access.
This infrastructure uses the following mechanisms to secure the PostgreSQL database:

* Azure Firewall: The database is accessible only from other Azure IPs, not from public IPs. (Note that includes other customers using Azure).
* Admin Username: Unique string generated based on subscription ID and stored in Key Vault.
* Admin Password: Randomly generated and stored in Key Vault.
* PostgreSQL Version: Latest available on Azure, version 14, which includes security improvements.

⚠️ For even more security, consider using an Azure Virtual Network to connect the Web App to the Database.
See [the Django-on-Azure project](https://github.com/tonybaloney/django-on-azure) for example infrastructure files.

### Costs

Pricing varies per region and usage, so it isn't possible to predict exact costs for your usage.

You can try the [Azure pricing calculator](https://azure.com/e/560b5f259111424daa7eb23c6848d164) for the resources:

- Azure App Service: Basic Tier with 1 CPU core, 1.75GB RAM. Pricing is hourly. [Pricing](https://azure.microsoft.com/pricing/details/app-service/linux/)
- PostgreSQL Flexible Server: Burstable Tier with 1 CPU core, 32GB storage. Pricing is hourly. [Pricing](https://azure.microsoft.com/pricing/details/postgresql/flexible-server/)
- Key Vault: Standard tier. Costs are per transaction, a few transactions are used on each deploy. [Pricing](https://azure.microsoft.com/pricing/details/key-vault/)
- Log analytics: Pay-as-you-go tier. Costs based on data ingested. [Pricing](https://azure.microsoft.com/pricing/details/monitor/)

⚠️ To avoid unnecessary costs, remember to take down your app if it's no longer in use,
either by deleting the resource group in the Portal or running `azd down`.


## Getting help

If you're working with this project and running into issues, please post in **Discussions**.
