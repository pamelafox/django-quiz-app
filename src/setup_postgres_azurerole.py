import argparse
import logging

import psycopg2
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("scripts")


def assign_role_for_webapp(postgres_host, postgres_username, app_identity_name):
    if not postgres_host.endswith(".database.azure.com"):
        logger.info("This script is intended to be used with Azure Database for PostgreSQL.")
        logger.info("Please set the environment variable DBHOST to the Azure Database for PostgreSQL server hostname.")
        return

    logger.info("Authenticating to Azure Database for PostgreSQL using Azure Identity...")
    azure_credential = DefaultAzureCredential()
    token = azure_credential.get_token("https://ossrdbms-aad.database.windows.net/.default")
    conn = psycopg2.connect(
        database="postgres",  # You must connect to postgres database when assigning roles
        user=postgres_username,
        password=token.token,
        host=postgres_host,
        sslmode="require",
    )

    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"select * from pgaadauth_list_principals(false) WHERE rolname = '{app_identity_name}'")
    identities = cur.fetchall()
    if len(identities) > 0:
        logger.info(f"Found an existing PostgreSQL role for identity {app_identity_name}")
    else:
        logger.info(f"Creating a PostgreSQL role for identity {app_identity_name}")
        cur.execute(f"SELECT * FROM pgaadauth_create_principal('{app_identity_name}', false, false)")

    logger.info(f"Granting permissions to {app_identity_name}")
    # set role to azure_pg_admin
    cur.execute(f'GRANT USAGE ON SCHEMA public TO "{app_identity_name}"')
    cur.execute(f'GRANT CREATE ON SCHEMA public TO "{app_identity_name}"')
    cur.execute(f'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "{app_identity_name}"')
    cur.execute(
        f"ALTER DEFAULT PRIVILEGES IN SCHEMA public "
        f'GRANT SELECT, UPDATE, INSERT, DELETE ON TABLES TO "{app_identity_name}"'
    )

    cur.close()


if __name__ == "__main__":

    logging.basicConfig(level=logging.WARNING)
    logger.setLevel(logging.INFO)
    parser = argparse.ArgumentParser(description="Create database schema")
    parser.add_argument("--host", type=str, help="Postgres host")
    parser.add_argument("--username", type=str, help="Postgres username")
    parser.add_argument("--app-identity-name", type=str, help="Azure App Service identity name")

    args = parser.parse_args()
    if not args.host.endswith(".database.azure.com"):
        logger.info("This script is intended to be used with Azure Database for PostgreSQL, not local PostgreSQL.")
        exit(1)

    assign_role_for_webapp(args.host, args.username, args.app_identity_name)
    logger.info("Role created successfully.")
