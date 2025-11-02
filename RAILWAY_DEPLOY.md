# Railway Deployment Checklist

## ✅ Required Environment Variables

Set these in Railway Dashboard (Project Settings → Variables):

```
NEO4J_URI=neo4j+s://85d6f157.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=0y1jZ7QGnXgOSjEZ6qk1bTLSqvtwFPiExCjEZyR6nQU
```

**Important:** Use `NEO4J_USERNAME` (not `NEO4J_USER`) to match your .env file.

## 🚀 Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add health check and fix Railway deployment"
   git push origin master
   ```

2. **Deploy on Railway**
   - Go to https://railway.app/
   - New Project → Deploy from GitHub
   - Select: PrakshaaleJain/User-graph
   - Railway will auto-detect Dockerfile and deploy

3. **Add Environment Variables**
   - Go to your Railway project
   - Settings → Variables
   - Add all three variables above
   - Redeploy if needed

4. **Test Deployment**
   - Visit: `https://your-app.up.railway.app/health`
   - Should return: `{"status":"healthy","database":"connected","total_nodes":11}`
   - Visit: `https://your-app.up.railway.app/` for the graph UI

## 🔧 Troubleshooting

### Database Connection Issues
```bash
# Test locally first
python test_neo4j_connection.py

# Check Railway logs
railway logs
```

### Frontend Not Loading
- Check Railway build logs for frontend directory
- Verify `/health` endpoint works first
- Check browser console (F12) for API errors

### Common Errors

1. **"ModuleNotFoundError"** → Check requirements.txt has all dependencies
2. **"Database disconnected"** → Check environment variables in Railway
3. **"CORS error"** → Already fixed with allow_origins=["*"]
4. **"404 Not Found"** → Frontend path issue, check Railway logs

## 📊 Health Check Endpoints

- `GET /health` - Check API and database status
- `GET /docs` - Interactive API documentation
- `GET /graph` - Get all graph data

## 🔐 Security Notes

- Never commit `.env` file to git (already in .gitignore)
- Rotate Neo4j password regularly in Aura console
- Update Railway environment variables after password change
- For production: restrict CORS to specific domains
