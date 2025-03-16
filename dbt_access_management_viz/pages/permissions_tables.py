import streamlit as st

from dbt_access_management_viz.service.redshift_service import get_redshift_service


redshift_service = get_redshift_service()

st.write("List of all tables:")
permission_tables = redshift_service.get_all_configured_models()
st.dataframe(data=permission_tables)

model_name = st.selectbox(
    "Select n model to get information which identity grants access to it",
    options=[""] + list(permission_tables["model_name"]),
)

if model_name:
    identity_assigned_to_model = redshift_service.get_identity_assigned_to_model(
        model_name=model_name
    )
    st.dataframe(identity_assigned_to_model)
