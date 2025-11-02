"""
Simple script to add sample data via API for testing
Run after starting the server: python add_sample_data.py
"""
import requests

API_URL = "http://localhost:8000"

# Sample users with intentional shared attributes
users = [
    {"user_id": "user1", "name": "John Doe", "email": "john@example.com", "phone": "123-456-7890", "address": "123 Main St", "payment_method": "Credit Card"},
    {"user_id": "user2", "name": "Jane Smith", "email": "jane@example.com", "phone": "123-456-7890", "address": "456 Oak Ave", "payment_method": "Bank Transfer"},
    {"user_id": "user3", "name": "Bob Wilson", "email": "john@example.com", "phone": "789-012-3456", "address": "123 Main St", "payment_method": "Credit Card"},
    {"user_id": "user4", "name": "Alice Brown", "email": "alice@example.com", "phone": "555-666-7777", "address": "789 Pine Rd", "payment_method": "PayPal"},
    {"user_id": "user5", "name": "Charlie Davis", "email": "charlie@example.com", "phone": "123-456-7890", "address": "321 Elm St", "payment_method": "Credit Card"},
]

# Sample transactions with shared devices/IPs
transactions = [
    {"txn_id": "txn1", "sender_id": "user1", "receiver_id": "user2", "amount": 100.50, "device_id": "device1", "ip_address": "192.168.1.1"},
    {"txn_id": "txn2", "sender_id": "user2", "receiver_id": "user3", "amount": 250.00, "device_id": "device1", "ip_address": "192.168.1.2"},
    {"txn_id": "txn3", "sender_id": "user3", "receiver_id": "user4", "amount": 75.25, "device_id": "device2", "ip_address": "192.168.1.1"},
    {"txn_id": "txn4", "sender_id": "user4", "receiver_id": "user5", "amount": 500.00, "device_id": "device3", "ip_address": "10.0.0.1"},
    {"txn_id": "txn5", "sender_id": "user5", "receiver_id": "user1", "amount": 125.75, "device_id": "device1", "ip_address": "192.168.1.1"},
]

def add_data():
    print("Adding users...")
    for user in users:
        response = requests.post(f"{API_URL}/users", json=user)
        print(f"  {user['user_id']}: {response.status_code}")
    
    print("\nAdding transactions...")
    for txn in transactions:
        response = requests.post(f"{API_URL}/transactions", json=txn)
        print(f"  {txn['txn_id']}: {response.status_code}")
    
    print("\n✓ Sample data added! Test relationships:")
    print(f"  - {API_URL}/relationships/user/user1")
    print(f"  - {API_URL}/relationships/transaction/txn1")
    print(f"  - {API_URL}/graph")

if __name__ == "__main__":
    try:
        add_data()
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the server is running: uvicorn backend.main:app --reload")
