from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .models import User, Transaction
from . import crud, relationships
from .database import db
import os

app = FastAPI(title="User & Transaction Graph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint to verify API and database connectivity"""
    try:
        # Test database connection
        result = db.query("RETURN 1 AS test")
        db_status = "connected" if result else "disconnected"
        
        # Get node counts
        node_count = db.query("MATCH (n) RETURN count(n) AS count")
        total_nodes = node_count[0]["count"] if node_count else 0
        
        return {
            "status": "healthy",
            "database": db_status,
            "total_nodes": total_nodes,
            "api_version": "1.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

@app.post("/users")
def add_user(user: User):
    crud.create_user(user.dict())
    return {"message": f"User {user.user_id} added or updated."}

@app.post("/transactions")
def add_transaction(txn: Transaction):
    try:
        result = crud.create_transaction(txn.dict())
        return {"message": f"Transaction {txn.txn_id} added successfully.", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users")
def list_users():
    try:
        users = crud.get_all_users()
        return [record.get("u", record) for record in users]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions")
def list_transactions():
    try:
        transactions = crud.get_all_transactions()
        return [record.get("t", record) for record in transactions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/graph")
def get_graph():
    """Get complete graph data for visualization"""
    try:
        return crud.get_graph_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/relationships/user/{user_id}")
def get_user_relationships_endpoint(user_id: str):
    """
    Fetch all connections of a user, including:
    - Direct relationships and transactions
    - Shared attribute links (email, phone, address, payment method)
    - Credit/Debit relationships
    """
    try:
        result = relationships.get_user_relationships(user_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/relationships/transaction/{txn_id}")
def get_transaction_relationships_endpoint(txn_id: str):
    """
    Fetch all connections of a transaction, including:
    - Linked users (sender and receiver)
    - Other transactions sharing device/IP
    """
    try:
        result = relationships.get_transaction_relationships(txn_id)
        if not result:
            raise HTTPException(status_code=404, detail=f"Transaction {txn_id} not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount frontend static files
# Try multiple possible frontend locations
frontend_dirs = [
    os.path.join(os.path.dirname(__file__), '../frontend'),
    os.path.join(os.getcwd(), 'frontend'),
    '/app/frontend'  # Railway/Docker path
]

frontend_path = None
for path in frontend_dirs:
    if os.path.exists(path) and os.path.isdir(path):
        frontend_path = path
        break

if frontend_path:
    print(f"✓ Serving frontend from: {frontend_path}")
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    print("⚠ Frontend directory not found. API-only mode.")
    print(f"  Searched paths: {frontend_dirs}")
