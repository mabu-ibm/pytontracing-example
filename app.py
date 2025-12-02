"""
Simple Flask Web Application with OpenTelemetry Auto-Instrumentation
With custom span information for each function
"""

import os
import time
import random
from flask import Flask, jsonify

# OpenTelemetry imports for manual instrumentation
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Get tracer for custom spans
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    with tracer.start_as_current_span("home_handler") as span:
        span.set_attribute("endpoint", "/")
        span.set_attribute("handler", "home")
        span.add_event("Returning welcome message")
        
        return jsonify({
            "message": "Welcome to the traced web app!",
            "endpoints": ["/", "/health", "/api/users", "/api/orders", "/api/slow"]
        })

@app.route('/health')
def health():
    with tracer.start_as_current_span("health_check") as span:
        span.set_attribute("endpoint", "/health")
        span.set_attribute("status", "healthy")
        span.add_event("Health check performed")
        
        return jsonify({"status": "healthy", "timestamp": time.time()})

@app.route('/api/users')
def get_users():
    with tracer.start_as_current_span("get_users") as span:
        span.set_attribute("endpoint", "/api/users")
        span.set_attribute("operation", "fetch_users")
        
        # Simulate database call
        with tracer.start_as_current_span("database_query") as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "users")
            
            delay = random.uniform(0.01, 0.05)
            time.sleep(delay)
            db_span.set_attribute("db.query_time_ms", round(delay * 1000, 2))
            db_span.add_event("Users fetched from database")
        
        users = [
            {"id": 1, "name": "Alice", "email": "alice@example.com"},
            {"id": 2, "name": "Bob", "email": "bob@example.com"},
            {"id": 3, "name": "Charlie", "email": "charlie@example.com"}
        ]
        
        span.set_attribute("user.count", len(users))
        span.add_event("Users retrieved successfully", {"count": len(users)})
        
        return jsonify({"users": users, "count": len(users)})

@app.route('/api/orders')
def get_orders():
    with tracer.start_as_current_span("get_orders") as span:
        span.set_attribute("endpoint", "/api/orders")
        span.set_attribute("operation", "fetch_orders")
        
        # Simulate database call
        with tracer.start_as_current_span("database_query") as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.operation", "SELECT")
            db_span.set_attribute("db.table", "orders")
            
            delay = random.uniform(0.02, 0.08)
            time.sleep(delay)
            db_span.set_attribute("db.query_time_ms", round(delay * 1000, 2))
            db_span.add_event("Orders fetched from database")
        
        orders = [
            {"id": 101, "user_id": 1, "total": 99.99, "status": "shipped"},
            {"id": 102, "user_id": 2, "total": 149.50, "status": "pending"},
            {"id": 103, "user_id": 1, "total": 29.99, "status": "delivered"}
        ]
        
        # Calculate totals
        total_value = sum(order["total"] for order in orders)
        
        span.set_attribute("order.count", len(orders))
        span.set_attribute("order.total_value", total_value)
        span.add_event("Orders retrieved successfully", {
            "count": len(orders),
            "total_value": total_value
        })
        
        return jsonify({"orders": orders, "count": len(orders)})

@app.route('/api/slow')
def slow_endpoint():
    """Endpoint that simulates a slow response for testing traces"""
    with tracer.start_as_current_span("slow_operation") as span:
        span.set_attribute("endpoint", "/api/slow")
        span.set_attribute("operation", "slow_process")
        
        delay = random.uniform(0.5, 2.0)
        span.set_attribute("expected_delay_seconds", delay)
        span.add_event("Starting slow operation", {"delay": delay})
        
        # Simulate multiple slow steps
        with tracer.start_as_current_span("step_1_processing") as step1:
            step1.set_attribute("step", 1)
            time.sleep(delay * 0.3)
            step1.add_event("Step 1 completed")
        
        with tracer.start_as_current_span("step_2_processing") as step2:
            step2.set_attribute("step", 2)
            time.sleep(delay * 0.4)
            step2.add_event("Step 2 completed")
        
        with tracer.start_as_current_span("step_3_processing") as step3:
            step3.set_attribute("step", 3)
            time.sleep(delay * 0.3)
            step3.add_event("Step 3 completed")
        
        span.add_event("Slow operation completed")
        
        return jsonify({"message": "Slow response completed", "delay_seconds": delay})

@app.route('/api/error')
def error_endpoint():
    """Endpoint that randomly throws errors for testing error traces"""
    with tracer.start_as_current_span("error_operation") as span:
        span.set_attribute("endpoint", "/api/error")
        span.set_attribute("operation", "risky_operation")
        
        if random.random() < 0.5:
            span.set_status(Status(StatusCode.ERROR, "Random error occurred"))
            span.set_attribute("error", True)
            span.add_event("Error triggered", {"error_type": "ValueError"})
            raise ValueError("Random error occurred!")
        
        span.set_status(Status(StatusCode.OK))
        span.add_event("Operation completed without error")
        
        return jsonify({"message": "No error this time!"})

@app.errorhandler(Exception)
def handle_exception(e):
    # Get current span and record the exception
    current_span = trace.get_current_span()
    if current_span:
        current_span.record_exception(e)
        current_span.set_status(Status(StatusCode.ERROR, str(e)))
    
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

