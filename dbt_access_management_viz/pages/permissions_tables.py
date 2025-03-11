import streamlit as st

from dbt_access_management_viz.service.redshift_service import get_redshift_service


redshift_service = get_redshift_service()

st.write("List of all DBT Access Management permissions tables:")
permission_tables = redshift_service.get_permissions_tables()
st.dataframe(data=permission_tables)
