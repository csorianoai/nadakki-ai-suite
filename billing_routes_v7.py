# ============================================================
# CREDICEFI BILLING ROUTES v7.0
# ============================================================
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
import random, json, os

router = APIRouter(prefix="/billing")

BILLING_FILE = "exports/billing_log.json"

# Planes
PLANS = {
  "starter": {"price": 99, "agents": 4},
  "professional": {"price": 499, "agents": 8},
  "enterprise": {"price": 899, "agents": 12},
}

# Pagos mock
async def mock_payment(amount, method="stripe"):
  status = "approved" if random.random() > 0.05 else "declined"
  return {
    "transaction_id": f"TX-{random.randint(100000,999999)}",
    "method": method,
    "status": status,
    "amount": amount,
    "timestamp": datetime.now().isoformat(),
  }

# Resumen facturación
@router.get("/summary", response_class=JSONResponse)
async def billing_summary():
  try:
    if os.path.exists(BILLING_FILE):
      with open(BILLING_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
    else:
      history = []
    total = sum(i["amount"] for i in history if i["status"]=="approved")
    return JSONResponse({
      "timestamp": datetime.now().isoformat(),
      "transactions": len(history),
      "total_billed_usd": total,
      "plan_distribution": PLANS
    })
  except Exception as e:
    return JSONResponse({"error": str(e)}, status_code=500)

# Nuevo pago
@router.post("/payments", response_class=JSONResponse)
async def process_payment():
  payment = await mock_payment(random.choice([99, 499, 899]))
  if os.path.exists(BILLING_FILE):
    with open(BILLING_FILE, "r", encoding="utf-8") as f: history = json.load(f)
  else:
    history = []
  history.append(payment)
  with open(BILLING_FILE, "w", encoding="utf-8") as f: json.dump(history, f, indent=4)
  return payment
