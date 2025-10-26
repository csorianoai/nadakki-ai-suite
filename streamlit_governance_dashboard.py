import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Nadakki Multi-Agent Governance", layout="wide")

st.title("🧠 Nadakki Multi-Agent Governance Dashboard")
st.caption("Fase 6 – Control total de agentes en tiempo real")

API_URL = "http://127.0.0.1:8000/governance/summary"
TOGGLE_URL = "http://127.0.0.1:8000/governance/toggle/"

def load_data():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"❌ Error al conectar con API: {e}")
        return None

data = load_data()
if data:
    usage = data.get("usage", {})
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Agentes Totales", data["total_agents"])
    c2.metric("Activos", data["active_agents"])
    c3.metric("Pausados", data["paused_agents"])
    c4.metric("Uptime", usage.get("uptime", "N/A"))

    st.subheader("📊 Uso de Recursos")
    st.progress(usage.get("cpu", 0) / 100)
    st.write(f"**CPU:** {usage['cpu']}% | **Memoria:** {usage['memory']}%")

    st.divider()
    st.subheader("⚙️ Agentes Operativos")

    for agent in data["agents"]:
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"**{agent['id']}** ({agent['category']})")
        col2.write(f"Estado: {'🟢' if agent['status']=='active' else '⏸️'} {agent['status']}")
        if col3.button(f"Alternar {agent['id']}"):
            try:
                requests.post(f"{TOGGLE_URL}{agent['id']}", timeout=3)
                st.success(f"Estado del agente '{agent['id']}' actualizado.")
                st.rerun()  # ✅ NUEVO MÉTODO COMPATIBLE
            except Exception as e:
                st.error(f"Error al alternar agente {agent['id']}: {e}")

    st.success(f"✅ Última actualización: {datetime.now().strftime('%H:%M:%S')}")
else:
    st.warning("Sin datos disponibles para mostrar.")

st.sidebar.title("Controles")
if st.sidebar.button("🔄 Recargar datos"):
    st.rerun()  # ✅ NUEVO MÉTODO ACTUAL
