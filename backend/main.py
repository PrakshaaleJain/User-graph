from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .models import User, Transaction
from . import crud, relationships
import os

app = FastAPI(title="User & Transaction Graph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Serve frontend
frontend_path = os.path.join(os.path.dirname(__file__), '../frontend')
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
