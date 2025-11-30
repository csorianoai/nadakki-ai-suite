import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Nadakki Sentinel Cloud", layout="wide")

st.title("🚀 Nadakki Sentinel Cloud Dashboard")
st.caption("Monitoreo Power BI JSON Feed – Fase 5 Cloud")

url = "http://127.0.0.1:8000/cloud/powerbi/data"

try:
    r = requests.get(url, timeout=5)
    data = r.json()
    st.metric("Estado", data.get("status", "N/A"))
    st.metric("Versión", data.get("version", "N/A"))
    st.metric("Agentes Activos", data.get("agents", 0))
    st.metric("Fase", data.get("phase", "N/A"))
    st.json(data)
    st.success(f"Última sincronización: {datetime.now().strftime('%H:%M:%S')}")
except Exception as e:
    st.error(f"Error al conectar con API: {e}")

st.sidebar.title("Controles")
if st.sidebar.button("🔄 Actualizar"):
    st.experimental_rerun()
