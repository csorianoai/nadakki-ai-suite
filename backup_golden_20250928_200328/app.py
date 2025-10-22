from flask import Flask, request, jsonify
from flask_cors import CORS
import json, random, time
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to Nadakki AI Suite", "status": "operational"})

@app.route("/api/v1/health")
def health():
    return jsonify({"status": "healthy", "agent_count": 12, "version": "3.0.0"})

@app.route("/api/v1/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    profile = data.get("profile", {})
    score = 75 + random.randint(-15, 20)
    return jsonify({
        "success": True,
        "data": {
            "risk_score": score,
            "recommendation": "APROBADO" if score > 70 else "RECHAZADO",
            "confidence": 90
        }
    })

@app.route("/api/v1/login", methods=["POST"])
def login():
    data = request.get_json()
    users = {"admin": "nadakki2025", "demo": "demo123"}
    username = data.get("username")
    password = data.get("password")
    
    if username in users and users[username] == password:
        return jsonify({
            "success": True,
            "data": {"token": f"token_{username}", "user": {"username": username}}
        })
    return jsonify({"success": False, "error": "Invalid credentials"}), 401

@app.route("/api/v1/similarity/compare", methods=["POST"])
def similarity():
    score = random.uniform(0.6, 0.9)
    return jsonify({
        "success": True,
        "similarity_analysis": {
            "similarity_score": round(score, 3),
            "risk_level": "low" if score < 0.7 else "medium",
            "decision": "LOW_RISK",
            "requires_human_review": False
        }
    })

if __name__ == "__main__":
    print("🚀 Nadakki Backend iniciando...")
    print("🌐 Servidor: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
