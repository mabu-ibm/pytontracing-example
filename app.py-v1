"""
Simple Flask Web Application with OpenTelemetry Auto-Instrumentation
Works with Instana, SigNoz, Jaeger, and other OTLP-compatible backends
"""

import os
import time
import random
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the traced web app!",
        "endpoints": ["/", "/health", "/api/users", "/api/orders", "/api/slow"]
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/users')
def get_users():
    # Simulate some work
    time.sleep(random.uniform(0.01, 0.05))
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
    ]
    return jsonify({"users": users, "count": len(users)})

@app.route('/api/orders')
def get_orders():
    # Simulate database call
    time.sleep(random.uniform(0.02, 0.08))
    orders = [
        {"id": 101, "user_id": 1, "total": 99.99, "status": "shipped"},
        {"id": 102, "user_id": 2, "total": 149.50, "status": "pending"},
        {"id": 103, "user_id": 1, "total": 29.99, "status": "delivered"}
    ]
    return jsonify({"orders": orders, "count": len(orders)})

@app.route('/api/slow')
def slow_endpoint():
    """Endpoint that simulates a slow response for testing traces"""
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    return jsonify({"message": "Slow response completed", "delay_seconds": delay})

@app.route('/api/error')
def error_endpoint():
    """Endpoint that randomly throws errors for testing error traces"""
    if random.random() < 0.5:
        raise ValueError("Random error occurred!")
    return jsonify({"message": "No error this time!"})

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
