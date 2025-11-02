"""Test Neo4j Aura connection"""
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USER") or os.getenv("NEO4J_USERNAME", "neo4j")
pwd = os.getenv("NEO4J_PASSWORD")

print(f"Testing connection to: {uri}")
print(f"Username: {user}")
print(f"Password: {'*' * len(pwd) if pwd else 'NOT SET'}")

try:
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        value = result.single()["test"]
        print(f"\n✓ Connection successful! Test query returned: {value}")
        
        # Check if database is empty
        count_result = session.run("MATCH (n) RETURN count(n) AS count")
        node_count = count_result.single()["count"]
        print(f"✓ Database has {node_count} nodes")
        
    driver.close()
    print("\n✓ Neo4j Aura connection is working!")
    
except Exception as e:
    print(f"\n✗ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check your .env file has correct credentials")
    print("2. Make sure URI uses neo4j+s:// (not bolt://)")
    print("3. Wait 60 seconds after creating Aura instance")
    print("4. Verify instance is running at https://console.neo4j.io")
