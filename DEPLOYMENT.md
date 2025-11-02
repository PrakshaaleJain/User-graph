# Railway Deployment Checklist

## Pre-Deployment

- [ ] Create Neo4j Aura DB instance at https://console.neo4j.io/
- [ ] Note down Neo4j credentials (URI, username, password)
- [ ] Push code to GitHub repository
- [ ] Review .gitignore (ensure .env is excluded)

## Railway Setup

- [ ] Sign up/login at https://railway.app/
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select your User-graph repository
- [ ] Wait for automatic detection of Dockerfile

## Environment Variables (Railway Dashboard)

Go to Project → Variables tab and add:

```
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-actual-password
```

## Post-Deployment

- [ ] Wait for deployment to complete (check logs)
- [ ] Copy the public URL from Railway dashboard
- [ ] Test API health: `https://your-app.up.railway.app/docs`
- [ ] Generate initial data:
  ```bash
  curl -X POST "https://your-app.up.railway.app/generate-data?num_users=10&num_transactions=15"
  ```
- [ ] Verify data: `https://your-app.up.railway.app/users`
- [ ] Test relationships: `https://your-app.up.railway.app/relationships/user/user1`
- [ ] Visit frontend: `https://your-app.up.railway.app/`

## Testing Endpoints

```bash
# Replace YOUR_URL with your Railway URL
export API_URL="https://your-app.up.railway.app"

# Health check
curl $API_URL/docs

# Generate data
curl -X POST "$API_URL/generate-data?num_users=10&num_transactions=15"

# List users
curl $API_URL/users

# List transactions
curl $API_URL/transactions

# Get graph data
curl $API_URL/graph

# Get user relationships
curl $API_URL/relationships/user/user1

# Get transaction relationships
curl $API_URL/relationships/transaction/txn1
```

## Troubleshooting

### Deployment fails
- Check Railway logs: Dashboard → Deployments → View Logs
- Verify Dockerfile builds locally: `docker build -t test .`

### Database connection errors
- Verify Neo4j Aura instance is running
- Check environment variables are set correctly in Railway
- Ensure NEO4J_URI uses `neo4j+s://` (secure protocol)

### Application errors
- Check Railway logs for Python errors
- Verify all dependencies in requirements.txt
- Test locally first with same environment variables

## Final Steps

- [ ] Share public URL via email
- [ ] Test all endpoints work correctly
- [ ] Monitor Railway usage (free tier: $5/month credit)
- [ ] Monitor Neo4j Aura usage (free tier: 200K nodes)

---

**Estimated deployment time: 5-10 minutes**
