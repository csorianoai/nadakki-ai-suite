# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, g
from flask_cors import CORS
import os
from datetime import datetime
import asyncio
import coordinator

# Crear la aplicación Flask PRIMERO
app = Flask(__name__)
CORS(app)

# Configuración básica
@app.route('/')
def home():
    return {"status": "Nadakki Enterprise", "version": "3.1.0"}

@app.route('/health')
def health():
    return {"status": "healthy", "service": "nadakki"}

# DESPUÉS de crear app, registrar Collections
try:
    from apps.collections.api.blueprint import collections_bp
    app.register_blueprint(collections_bp)
    print("Collections Blueprint registered successfully")
except Exception as e:
    print(f"Collections error: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
