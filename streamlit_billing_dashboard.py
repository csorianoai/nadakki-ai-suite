import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="CrediCefi Billing Dashboard", layout="wide")

st.title("💳 CrediCefi Billing & Subdomain Manager")
st.caption("Fase 7 – Facturación Financiera AI en Tiempo Real")

SUMMARY_URL = "http://127.0.0.1:8000/billing/summary"
PAY_URL = "http://127.0.0.1:8000/billing/payments"

try:
  data = requests.get(SUMMARY_URL, timeout=5).json()
  st.metric("Transacciones", data["transactions"])
  st.metric("Total Facturado (USD)", data["total_billed_usd"])
  st.json(data["plan_distribution"])
except Exception as e:
  st.error(f"❌ Error al cargar datos: {e}")

st.divider()
st.subheader("⚙️ Procesar Pago Simulado")
if st.button("💵 Ejecutar Pago"):
  resp = requests.post(PAY_URL).json()
  if resp["status"]=="approved":
    st.success(f"✅ Pago aprobado {resp['transaction_id']} – ${resp['amount']}")
  else:
    st.error(f"❌ Pago rechazado {resp['transaction_id']}")
  st.rerun()

st.success(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")
