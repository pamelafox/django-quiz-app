from .settings import *  # noqa
import os

# Configure the domain name using the environment variable
# that Azure automatically creates for us.
ALLOWED_HOSTS = [os.environ["WEBSITE_HOSTNAME"]] if "WEBSITE_HOSTNAME" in os.environ else []
CSRF_TRUSTED_ORIGINS = ["https://" + os.environ["WEBSITE_HOSTNAME"]] if "WEBSITE_HOSTNAME" in os.environ else []
DEBUG = False

# DBHOST is only the server name, not the full URL
hostname = os.environ["DBHOST"]

# Configure Postgres database; the full username for PostgreSQL flexible server is
# username (not @sever-name).
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["DBNAME"],
        "HOST": hostname + ".postgres.database.azure.com",
        "USER": os.environ["DBUSER"],
        "PASSWORD": os.environ["DBPASS"],
    }
}
