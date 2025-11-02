from .database import db

def create_user(user_data):
    query = """
    MERGE (u:User {user_id: $user_id})
    SET u.name = $name,
        u.email = $email,
        u.phone = $phone,
        u.address = $address,
        u.payment_method = $payment_method
    RETURN u
    """
    db.query(query, user_data)

    detect_user_relationships(user_data["user_id"])

def create_transaction(txn_data):
    query = """
    MERGE (t:Transaction {txn_id: $txn_id})
    SET t.amount = $amount,
        t.device_id = $device_id,
        t.ip_address = $ip_address
    WITH t
    MATCH (s:User {user_id: $sender_id}), (r:User {user_id: $receiver_id})
    MERGE (s)-[:SENT]->(t)
    MERGE (t)-[:RECEIVED_BY]->(r)
    RETURN t
    """
    db.query(query, txn_data)

    detect_transaction_relationships(txn_data["txn_id"])

def get_all_users(limit: int = 200):
    return db.query("MATCH (u:User) RETURN u LIMIT $limit", {"limit": limit})

def get_all_transactions(limit: int = 200):
    return db.query("MATCH (t:Transaction) RETURN t LIMIT $limit", {"limit": limit})


def detect_user_relationships(user_id):
    """Find users with shared attributes and create specific relationship edges."""
    
    # Email Links
    email_query = """
    MATCH (u1:User {user_id: $user_id}), (u2:User)
    WHERE u1 <> u2
      AND u1.email IS NOT NULL 
      AND u1.email = u2.email
    MERGE (u1)-[:SHARED_EMAIL]->(u2)
    """
    db.query(email_query, {"user_id": user_id})
    
    # Phone Links
    phone_query = """
    MATCH (u1:User {user_id: $user_id}), (u2:User)
    WHERE u1 <> u2
      AND u1.phone IS NOT NULL 
      AND u1.phone = u2.phone
    MERGE (u1)-[:SHARED_PHONE]->(u2)
    """
    db.query(phone_query, {"user_id": user_id})
    
    # Address Links
    address_query = """
    MATCH (u1:User {user_id: $user_id}), (u2:User)
    WHERE u1 <> u2
      AND u1.address IS NOT NULL 
      AND u1.address = u2.address
    MERGE (u1)-[:SHARED_ADDRESS]->(u2)
    """
    db.query(address_query, {"user_id": user_id})
    
    # Payment Method Links
    payment_query = """
    MATCH (u1:User {user_id: $user_id}), (u2:User)
    WHERE u1 <> u2
      AND u1.payment_method IS NOT NULL 
      AND u1.payment_method = u2.payment_method
    MERGE (u1)-[:SHARED_PAYMENT_METHOD]->(u2)
    """
    db.query(payment_query, {"user_id": user_id})
    
    # Create Credit/Debit Links (direct transaction relationships)
    credit_query = """
    MATCH (u:User {user_id: $user_id})-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(other:User)
    MERGE (u)-[:CREDIT_TO]->(other)
    """
    db.query(credit_query, {"user_id": user_id})
    
    debit_query = """
    MATCH (other:User)-[:SENT]->(t:Transaction)-[:RECEIVED_BY]->(u:User {user_id: $user_id})
    MERGE (u)-[:DEBIT_FROM]->(other)
    """
    db.query(debit_query, {"user_id": user_id})

def detect_transaction_relationships(txn_id):
    """Link transactions that share same device or IP, and create Credit/Debit links."""
    
    # Device ID Links
    device_query = """
    MATCH (t1:Transaction {txn_id: $txn_id}), (t2:Transaction)
    WHERE t1 <> t2
      AND t1.device_id IS NOT NULL 
      AND t1.device_id = t2.device_id
    MERGE (t1)-[:SHARED_DEVICE]->(t2)
    """
    db.query(device_query, {"txn_id": txn_id})
    
    # IP Address Links
    ip_query = """
    MATCH (t1:Transaction {txn_id: $txn_id}), (t2:Transaction)
    WHERE t1 <> t2
      AND t1.ip_address IS NOT NULL 
      AND t1.ip_address = t2.ip_address
    MERGE (t1)-[:SHARED_IP]->(t2)
    """
    db.query(ip_query, {"txn_id": txn_id})
    
    # Create/Update Credit and Debit Links for users involved in this transaction
    update_user_links_query = """
    MATCH (s:User)-[:SENT]->(t:Transaction {txn_id: $txn_id})-[:RECEIVED_BY]->(r:User)
    MERGE (s)-[:CREDIT_TO]->(r)
    MERGE (r)-[:DEBIT_FROM]->(s)
    """
    db.query(update_user_links_query, {"txn_id": txn_id})

def get_graph_data():
    """Get all users, transactions and their relationships for visualization"""
    nodes = []
    edges = []
    
    users_result = db.query("MATCH (u:User) RETURN u LIMIT 50")
    for record in users_result:
        user = dict(record["u"])
        nodes.append({
            "data": {
                "id": user["user_id"],
                "label": user.get("name", user["user_id"]),
                "type": "user",
                **user
            }
        })
    
    txns_result = db.query("MATCH (t:Transaction) RETURN t LIMIT 100")
    for record in txns_result:
        txn = dict(record["t"])
        nodes.append({
            "data": {
                "id": txn["txn_id"],
                "label": f"${txn.get('amount', 0)}",
                "type": "transaction",
                **txn
            }
        })
    
    sent_result = db.query("""
        MATCH (u:User)-[:SENT]->(t:Transaction)
        RETURN u.user_id as sender, t.txn_id as txn
        LIMIT 100
    """)
    for record in sent_result:
        edges.append({
            "data": {
                "id": f"{record['sender']}-sent-{record['txn']}",
                "source": record["sender"],
                "target": record["txn"],
                "type": "SENT"
            }
        })
    
    received_result = db.query("""
        MATCH (t:Transaction)-[:RECEIVED_BY]->(u:User)
        RETURN t.txn_id as txn, u.user_id as receiver
        LIMIT 100
    """)
    for record in received_result:
        edges.append({
            "data": {
                "id": f"{record['txn']}-received-{record['receiver']}",
                "source": record["txn"],
                "target": record["receiver"],
                "type": "RECEIVED_BY"
            }
        })
    
    return {"nodes": nodes, "edges": edges}
