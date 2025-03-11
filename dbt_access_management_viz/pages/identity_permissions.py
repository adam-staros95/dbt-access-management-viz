import streamlit as st

from dbt_access_management_viz.service.redshift_service import get_redshift_service

redshift_service = get_redshift_service()

st.write("List of all identities:")
permission_tables = redshift_service.get_all_identities()
st.dataframe(data=permission_tables)


identity_name = st.selectbox(
    "Select an identity to get assigned permissions",
    options=[""] + list(permission_tables["identity_name"]),
)

if identity_name:
    per_identity_permissions = redshift_service.get_all_permissions_for_identity(
        identity_name=identity_name
    )
    st.dataframe(per_identity_permissions)
