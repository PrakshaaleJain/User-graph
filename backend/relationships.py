from .database import db

def get_user_relationships(user_id: str):
    """
    Fetch all connections of a user, including:
    - Direct transaction relationships (Credit/Debit links)
    - Shared attribute relationships (Email, Phone, Address, Payment Method)
    - Connected users and transaction details
    """
    query = """
    MATCH (u:User {user_id: $user_id})
    OPTIONAL MATCH (u)-[r]-(connected)
    RETURN u, 
           type(r) as relationship_type, 
           labels(connected) as connected_labels,
           connected,
           r
    """
    result = db.query(query, {"user_id": user_id})
    
    relationships = {
        "user_id": user_id,
        "direct_transactions": [],
        "shared_email": [],
        "shared_phone": [],
        "shared_address": [],
        "shared_payment_method": [],
        "credit_to": [],
        "debit_from": [],
        "all_connections": []
    }
    
    for record in result:
        if not record.get("connected"):
            continue
            
        rel_type = record.get("relationship_type")
        connected = dict(record["connected"])
        labels = record.get("connected_labels", [])
        
        connection_info = {
            "relationship_type": rel_type,
            "connected": connected,
            "node_type": labels[0] if labels else "Unknown"
        }
        
        relationships["all_connections"].append(connection_info)
        
        # Categorize by relationship type
        if rel_type in ["SENT", "RECEIVED_BY"]:
            relationships["direct_transactions"].append(connection_info)
        elif rel_type == "SHARED_EMAIL":
            relationships["shared_email"].append(connection_info)
        elif rel_type == "SHARED_PHONE":
            relationships["shared_phone"].append(connection_info)
        elif rel_type == "SHARED_ADDRESS":
            relationships["shared_address"].append(connection_info)
        elif rel_type == "SHARED_PAYMENT_METHOD":
            relationships["shared_payment_method"].append(connection_info)
        elif rel_type == "CREDIT_TO":
            relationships["credit_to"].append(connection_info)
        elif rel_type == "DEBIT_FROM":
            relationships["debit_from"].append(connection_info)
    
    return relationships

def get_transaction_relationships(txn_id: str):
    """
    Fetch all connections of a transaction, including:
    - Linked users (sender and receiver)
    - Other transactions sharing device/IP
    - Transaction metadata
    """
    query = """
    MATCH (t:Transaction {txn_id: $txn_id})
    OPTIONAL MATCH (t)-[r]-(connected)
    RETURN t,
           type(r) as relationship_type,
           labels(connected) as connected_labels,
           connected,
           r
    """
    result = db.query(query, {"txn_id": txn_id})
    
    relationships = {
        "txn_id": txn_id,
        "sender": None,
        "receiver": None,
        "shared_device": [],
        "shared_ip": [],
        "all_connections": []
    }
    
    for record in result:
        if not record.get("connected"):
            # First record might just have transaction info
            if record.get("t"):
                relationships["transaction_details"] = dict(record["t"])
            continue
            
        rel_type = record.get("relationship_type")
        connected = dict(record["connected"])
        labels = record.get("connected_labels", [])
        
        connection_info = {
            "relationship_type": rel_type,
            "connected": connected,
            "node_type": labels[0] if labels else "Unknown"
        }
        
        relationships["all_connections"].append(connection_info)
        
        # Categorize by relationship type
        if rel_type == "SENT":
            relationships["sender"] = connected
        elif rel_type == "RECEIVED_BY":
            relationships["receiver"] = connected
        elif rel_type == "SHARED_DEVICE":
            relationships["shared_device"].append(connection_info)
        elif rel_type == "SHARED_IP":
            relationships["shared_ip"].append(connection_info)
    
    return relationships

