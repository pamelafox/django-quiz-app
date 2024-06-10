from azure.identity import DefaultAzureCredential
from django.db.backends.postgresql import base


class DatabaseWrapper(base.DatabaseWrapper):
    def get_connection_params(self):
        params = super().get_connection_params()
        if params.get("host", "").endswith(".database.azure.com"):
            azure_credential = DefaultAzureCredential()
            dbpass = azure_credential.get_token("https://ossrdbms-aad.database.windows.net/.default").token
            params["password"] = dbpass
        return params
