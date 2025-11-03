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
    """
    Fetch nodes and edges for visualization
    Includes all relationship types: transactions, shared attributes, devices, IPs
    Ensures edges only reference nodes that exist in the result set
    """
    nodes = []
    edges = []
    node_ids = set()
    
    # Fetch users
    users_result = db.query("MATCH (u:User) RETURN u LIMIT 200")
    for record in users_result:
        user = dict(record["u"])
        user_id = user["user_id"]
        node_ids.add(user_id)
        nodes.append({
            "data": {
                "id": user_id,
                "label": user.get("name", user_id),
                "type": "user",
                **user
            }
        })
    
    # Fetch transactions
    txns_result = db.query("MATCH (t:Transaction) RETURN t LIMIT 500")
    for record in txns_result:
        txn = dict(record["t"])
        txn_id = txn["txn_id"]
        node_ids.add(txn_id)
        nodes.append({
            "data": {
                "id": txn_id,
                "label": f"${txn.get('amount', 0)}",
                "type": "transaction",
                **txn
            }
        })
    
    # Fetch all edges but only include those where both source and target exist in node_ids
    all_edges_result = db.query("""
        MATCH (n)-[r]->(m)
        RETURN DISTINCT 
            CASE WHEN 'User' IN labels(n) THEN n.user_id ELSE n.txn_id END as source_id,
            CASE WHEN 'User' IN labels(m) THEN m.user_id ELSE m.txn_id END as target_id,
            type(r) as rel_type
        LIMIT 2000
    """)
    
    for record in all_edges_result:
        source_id = record["source_id"]
        target_id = record["target_id"]
        rel_type = record["rel_type"]
        
        # Only add edge if both nodes exist
        if source_id in node_ids and target_id in node_ids:
            edges.append({
                "data": {
                    "id": f"{source_id}-{rel_type}-{target_id}",
                    "source": source_id,
                    "target": target_id,
                    "type": rel_type
                }
            })
    
    return {"nodes": nodes, "edges": edges}
