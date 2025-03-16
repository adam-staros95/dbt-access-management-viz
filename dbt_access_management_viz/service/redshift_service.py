import os

import pandas as pd

from dbt_access_management_viz.repository.redshift_repository import RedshiftRepository


class RedshiftService:
    def __init__(self, redshift_repository: RedshiftRepository):
        self._redshift_repository = redshift_repository

    def _get_permissions_tables(
        self, dbt_access_management_schema_name: str = "access_management"
    ) -> pd.DataFrame:
        return self._redshift_repository.query(
            f"""SELECT
                    table_name,
                    table_schema
                FROM information_schema.tables
                WHERE table_schema = '{dbt_access_management_schema_name}'
                    AND table_name NOT LIKE 'temp_%'
                    AND table_name LIKE '%_access_management_config'"""
        )

    def get_all_identities(
        self, dbt_access_management_schema_name: str = "access_management"
    ) -> pd.DataFrame:
        all_permissions_tables = self._get_permissions_tables(
            dbt_access_management_schema_name
        )
        queries = []
        for _, row in all_permissions_tables.iterrows():
            queries.append(
                f"SELECT identity_name, identity_type FROM {row['table_schema']}.{row['table_name']}"
            )
        query = "\nUNION\n".join(queries)
        return self._redshift_repository.query(query)

    def get_all_permissions_for_identity(
        self,
        identity_name: str,
        dbt_access_management_schema_name: str = "access_management",
    ) -> pd.DataFrame:
        all_permissions_tables = self._get_permissions_tables(
            dbt_access_management_schema_name
        )
        queries = []
        for _, row in all_permissions_tables.iterrows():
            queries.append(
                f"""SELECT
                        identity_name,
                        schema_name,
                        model_name,
                        materialization,
                        '{row['table_name'].removesuffix('_access_management_config')}' as dbt_project_name
                    FROM {row['table_schema']}.{row['table_name']} WHERE identity_name = '{identity_name}'"""
            )
        query = "\nUNION\n".join(queries)
        return self._redshift_repository.query(query)

    def get_all_configured_models(
        self,
        dbt_access_management_schema_name: str = "access_management",
    ) -> pd.DataFrame:
        all_permissions_tables = self._get_permissions_tables(
            dbt_access_management_schema_name
        )
        queries = []
        for _, row in all_permissions_tables.iterrows():
            queries.append(
                f"""SELECT
                        schema_name,
                        model_name,
                        materialization
                    FROM {row['table_schema']}.{row['table_name']}"""
            )
        query = "\nUNION\n".join(queries)
        query = query + "\nORDER BY schema_name, model_name\n"
        return self._redshift_repository.query(query)

    def get_identity_assigned_to_model(
        self,
        model_name: str,
        dbt_access_management_schema_name: str = "access_management",
    ) -> pd.DataFrame:
        all_permissions_tables = self._get_permissions_tables(
            dbt_access_management_schema_name
        )
        queries = []
        for _, row in all_permissions_tables.iterrows():
            queries.append(
                f"""SELECT
                        identity_name
                    FROM {row['table_schema']}.{row['table_name']} WHERE model_name = '{model_name}'"""
            )
        query = "\nUNION\n".join(queries)
        query = query + "\nORDER BY identity_name\n"
        return self._redshift_repository.query(query)


def get_redshift_service() -> RedshiftService:
    redshift_repository = RedshiftRepository(secret_name=os.environ["SECRET_NAME"])
    return RedshiftService(redshift_repository=redshift_repository)
