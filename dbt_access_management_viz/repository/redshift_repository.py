from typing import Dict

import boto3
import pandas as pd
import redshift_connector


class RedshiftRepository:
    def __init__(self, secret_name: str, region_name: str = "us-west-2"):
        self.secret_name = secret_name
        self.region_name = region_name
        self.client = boto3.client("secretsmanager", region_name=self.region_name)

    def _get_secret(self) -> Dict:
        try:
            secret_value = self.client.get_secret_value(SecretId=self.secret_name)
            return eval(secret_value["SecretString"])
        except Exception as e:
            raise Exception(f"Error getting secret: {str(e)}")

    def query(self, query: str) -> pd.DataFrame:
        secret = self._get_secret()
        try:
            conn = redshift_connector.connect(
                host=secret["host"],
                database=secret["dbname"],
                user=secret["username"],
                password=secret["password"],
            )
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetch_dataframe()
        except Exception as e:
            raise Exception(f"Error querying Redshift: {str(e)}")
        finally:
            if "conn" in locals():
                conn.close()
