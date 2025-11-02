# User & Transaction Relationship Graph System

Graph-based fraud detection system using Neo4j Aura and FastAPI, deployed on Railway.

## API Endpoints

- `POST /users` - Add user
- `POST /transactions` - Add transaction
- `GET /users` - List users
- `GET /transactions` - List transactions
- `GET /graph` - Get graph data
- `GET /relationships/user/{user_id}` - User relationships
- `GET /relationships/transaction/{txn_id}` - Transaction relationships

## Setup

### 1. Neo4j Aura Setup
1. Create account at https://console.neo4j.io/
2. Create free instance
3. Save credentials: URI, Username, Password

### 2. Local Development
```bash
git clone <repo-url>
cd User-graph
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create `.env`:
```
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
```

Run:
```bash
uvicorn backend.main:app --reload
```

### 3. Railway Deployment
1. Push code to GitHub
2. Create Railway project from GitHub repo
3. Add environment variables in Railway dashboard:
   - `NEO4J_URI`
   - `NEO4J_USER`
   - `NEO4J_PASSWORD`
4. Deploy automatically

## Relationship Detection

- **User-to-User**: SHARED_EMAIL, SHARED_PHONE, SHARED_ADDRESS, SHARED_PAYMENT_METHOD, CREDIT_TO, DEBIT_FROM
- **Transaction-to-Transaction**: SHARED_DEVICE, SHARED_IP

## Tech Stack

- FastAPI (Python 3.11)
- Neo4j Aura (Graph Database)
- Railway (Hosting)
- Docker
