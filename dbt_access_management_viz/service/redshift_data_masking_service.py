import os

import pandas as pd

from dbt_access_management_viz.repository.redshift_repository import RedshiftRepository


class RedshiftService:
    def __init__(self, redshift_repository: RedshiftRepository):
        self._redshift_repository = redshift_repository

    def _get_data_masking_tables(
        self, dbt_access_management_schema_name: str = "access_management"
    ) -> pd.DataFrame:
        return self._redshift_repository.query(
            f"""SELECT
                    table_name,
                    table_schema
                FROM information_schema.tables
                WHERE table_schema = '{dbt_access_management_schema_name}'
                    AND table_name NOT LIKE 'temp_%'
                    AND table_name LIKE '%_data_masking_config'"""
        )

    def get_all_masked_columns(
        self,
        dbt_access_management_schema_name: str = "access_management",
    ) -> pd.DataFrame:
        all_permissions_tables = self._get_data_masking_tables(
            dbt_access_management_schema_name
        )
        queries = []
        for _, row in all_permissions_tables.iterrows():
            queries.append(
                f"""SELECT
                        schema_name,
                        model_name,
                        masking_config
                    FROM {row['table_schema']}.{row['table_name']}"""
            )
        query = "\nUNION\n".join(queries)
        query = query + "\nORDER BY schema_name, model_name\n"
        return self._redshift_repository.query(query)


def get_redshift_service() -> RedshiftService:
    redshift_repository = RedshiftRepository(secret_name=os.environ["SECRET_NAME"])
    return RedshiftService(redshift_repository=redshift_repository)
