"""
Large-scale data generator for Neo4j Aura
Generates 100 users and 1,000,000 transactions with shared attributes
Uses batch processing for efficiency with Faker for realistic data
"""
import requests
import random
import time
from faker import Faker
from concurrent.futures import ThreadPoolExecutor, as_completed

fake = Faker()

# Use hosted Railway URL or localhost
API_URL = input("Enter your Railway URL (or press Enter for localhost): ").strip()
if not API_URL:
    API_URL = "http://localhost:8000"
API_URL = API_URL.rstrip('/')

# Use hosted Railway URL or localhost
API_URL = input("Enter your Railway URL (or press Enter for localhost): ").strip()
if not API_URL:
    API_URL = "http://localhost:8000"
API_URL = API_URL.rstrip('/')

print(f"\n🚀 Generating data for: {API_URL}")

# Configuration
NUM_USERS = 100

# Neo4j Aura Free Tier: Max 50,000 nodes
# Aura Professional: Max 200,000 nodes
print("\n⚠️  NEO4J AURA FREE TIER LIMIT: 50,000 nodes")
print("   Your plan: 100 users + transactions = total nodes")
print("\nRecommended options:")
print("  1. Free tier safe:     49,900 transactions (50,000 total nodes)")
print("  2. Test dataset:       10,000 transactions")
print("  3. Professional tier:  1,000,000 transactions (requires upgrade)")

choice = input("\nSelect option (1/2/3) or enter custom number [default=1]: ").strip()
if choice == "" or choice == "1":
    NUM_TRANSACTIONS = 49_900  # Default: free tier safe
elif choice == "2":
    NUM_TRANSACTIONS = 10_000
elif choice == "3":
    confirm = input("⚠️  This requires Neo4j Aura Professional tier. Continue? (yes/no): ")
    if confirm.lower() == "yes":
        NUM_TRANSACTIONS = 1_000_000
    else:
        print("Cancelled.")
        exit(0)
elif choice.isdigit():
    NUM_TRANSACTIONS = int(choice)
    if NUM_TRANSACTIONS + NUM_USERS > 50_000:
        print(f"⚠️  Warning: {NUM_TRANSACTIONS + NUM_USERS:,} nodes exceeds free tier limit!")
        confirm = input("Continue anyway? (yes/no): ")
        if confirm.lower() != "yes":
            print("Cancelled.")
            exit(0)
else:
    print("Invalid option. Using default (49,900 transactions)")
    NUM_TRANSACTIONS = 49_900

BATCH_SIZE = 1000  # Process in batches
MAX_WORKERS = 20   # Parallel requests (balanced for Railway)
TIMEOUT = 30       # Increased timeout for Railway cold starts

print(f"\n📊 Configuration:")
print(f"  Users: {NUM_USERS:,}")
print(f"  Transactions: {NUM_TRANSACTIONS:,}")
print(f"  Total nodes: {NUM_USERS + NUM_TRANSACTIONS:,}")
print(f"  Batch size: {BATCH_SIZE:,}")
print(f"  Parallel workers: {MAX_WORKERS}")

# Generate user pool
def generate_users():
    """Generate 100 users with intentional shared attributes using Faker"""
    print(f"\n📊 Generating {NUM_USERS} users...")
    
    # Shared attribute pools (for relationship detection)
    shared_emails = [fake.company_email() for _ in range(30)]  # 30% share emails
    shared_phones = [fake.phone_number() for _ in range(25)]  # 25% share phones
    shared_addresses = [fake.address().replace('\n', ', ') for _ in range(20)]  # 20% share addresses
    payment_methods = ["Credit Card", "Bank Transfer", "Digital Wallet", "PayPal", "Crypto Wallet"]
    
    users = []
    for i in range(NUM_USERS):
        # 40% share attributes, 60% unique
        use_shared = i < (NUM_USERS * 0.4)
        
        user = {
            "user_id": f"user_{i+1:04d}",
            "name": fake.name(),
            "email": random.choice(shared_emails) if use_shared else fake.email(),
            "phone": random.choice(shared_phones) if use_shared else fake.phone_number(),
            "address": (random.choice(shared_addresses) if use_shared else fake.address()).replace('\n', ', '),
            "payment_method": random.choice(payment_methods)
        }
        users.append(user)
    
    return users

def generate_transactions_batch(start_idx, batch_size, user_ids):
    """Generate a batch of transactions using Faker for realistic amounts and IPs"""
    # Shared device/IP pools (for relationship detection)
    shared_devices = [f"device_{fake.uuid4()[:8]}" for _ in range(500)]  # 500 devices
    shared_ips = [fake.ipv4() for _ in range(300)]  # 300 IP addresses
    
    transactions = []
    for i in range(start_idx, min(start_idx + batch_size, NUM_TRANSACTIONS)):
        sender, receiver = random.sample(user_ids, 2)
        
        # 30% share devices/IPs (for fraud detection patterns)
        use_shared = random.random() < 0.3
        
        txn = {
            "txn_id": f"txn_{i+1:07d}",
            "sender_id": sender,
            "receiver_id": receiver,
            "amount": round(random.uniform(1, 10000), 2),
            "device_id": random.choice(shared_devices) if use_shared else f"device_{fake.uuid4()[:12]}",
            "ip_address": random.choice(shared_ips) if use_shared else fake.ipv4()
        }
        transactions.append(txn)
    
    return transactions

def send_batch(endpoint, data_batch, batch_num, total_batches):
    """Send a batch of data to the API"""
    errors = []
    success_count = 0
    
    for item in data_batch:
        try:
            response = requests.post(f"{API_URL}/{endpoint}", json=item, timeout=TIMEOUT)
            if response.status_code in (200, 201):
                success_count += 1
            else:
                errors.append(f"Status {response.status_code}: {item.get('user_id') or item.get('txn_id')}")
        except Exception as e:
            errors.append(f"Error: {str(e)}")
    
    return success_count, errors, batch_num, total_batches

def main():
    print("\n" + "="*60)
    print("  LARGE-SCALE DATA GENERATOR")
    print("  100 users + 1,000,000 transactions")
    print("="*60)
    
    # Test connection
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        health = response.json()
        print(f"\n✓ Connected to API")
        print(f"  Database: {health.get('database', 'unknown')}")
        print(f"  Current nodes: {health.get('total_nodes', 0)}")
    except Exception as e:
        print(f"\n✗ Cannot connect to API: {e}")
        print("  Make sure the server is running!")
        return
    
    start_time = time.time()
    
    # Step 1: Generate and upload users
    print(f"\n{'='*60}")
    print("STEP 1: Creating Users")
    print('='*60)
    
    users = generate_users()
    user_ids = [u["user_id"] for u in users]
    
    print(f"Uploading {len(users)} users...")
    user_success = 0
    user_errors = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = []
        for user in users:
            future = executor.submit(requests.post, f"{API_URL}/users", json=user, timeout=TIMEOUT)
            futures.append(future)
        
        for i, future in enumerate(as_completed(futures), 1):
            try:
                response = future.result()
                if response.status_code in (200, 201):
                    user_success += 1
                else:
                    user_errors.append(f"HTTP {response.status_code}: {response.text[:100]}")
                print(f"\r  Progress: {i}/{len(users)} users ({user_success} successful)", end="", flush=True)
            except Exception as e:
                user_errors.append(str(e))
    
    print(f"\n✓ Users created: {user_success}/{len(users)}")
    if user_errors:
        print(f"  Errors: {len(user_errors)}")
        print(f"  First error: {user_errors[0]}")
        if len(user_errors) > 1:
            print(f"  Last error: {user_errors[-1]}")

    
    # Step 2: Generate and upload transactions in batches
    print(f"\n{'='*60}")
    print("STEP 2: Creating Transactions")
    print('='*60)
    print(f"Total transactions: {NUM_TRANSACTIONS:,}")
    print(f"Batch size: {BATCH_SIZE:,}")
    print(f"Parallel workers: {MAX_WORKERS}")
    
    total_batches = (NUM_TRANSACTIONS + BATCH_SIZE - 1) // BATCH_SIZE
    txn_success = 0
    txn_errors = []
    
    print(f"\nProcessing {total_batches} batches...\n")
    
    batch_start_time = time.time()
    
    for batch_num in range(total_batches):
        start_idx = batch_num * BATCH_SIZE
        
        # Generate batch
        transactions = generate_transactions_batch(start_idx, BATCH_SIZE, user_ids)
        
        # Upload batch in parallel
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for txn in transactions:
                future = executor.submit(requests.post, f"{API_URL}/transactions", json=txn, timeout=TIMEOUT)
                futures.append(future)
            
            batch_success = 0
            for future in as_completed(futures):
                try:
                    response = future.result()
                    if response.status_code in (200, 201):
                        batch_success += 1
                        txn_success += 1
                except Exception as e:
                    txn_errors.append(str(e))
        
        # Progress update
        elapsed = time.time() - batch_start_time
        rate = txn_success / elapsed if elapsed > 0 else 0
        eta_seconds = (NUM_TRANSACTIONS - txn_success) / rate if rate > 0 else 0
        eta_mins = eta_seconds / 60
        
        progress_pct = (txn_success / NUM_TRANSACTIONS) * 100
        
        print(f"\r  Batch {batch_num+1}/{total_batches} | "
              f"Transactions: {txn_success:,}/{NUM_TRANSACTIONS:,} ({progress_pct:.1f}%) | "
              f"Rate: {rate:.0f}/sec | "
              f"ETA: {eta_mins:.1f} min", end="", flush=True)
        
        # Status update every 10 batches
        if (batch_num + 1) % 10 == 0:
            print()  # New line for readability
    
    print()  # Final newline
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n{'='*60}")
    print("GENERATION COMPLETE")
    print('='*60)
    print(f"✓ Users created: {user_success}/{NUM_USERS}")
    print(f"✓ Transactions created: {txn_success:,}/{NUM_TRANSACTIONS:,}")
    print(f"✓ Total time: {total_time/60:.1f} minutes")
    print(f"✓ Average rate: {txn_success/total_time:.0f} transactions/second")
    
    if txn_errors:
        print(f"\n⚠ Errors encountered: {len(txn_errors)}")
        print(f"  (Check logs for details)")
    
    # Check final database state
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        health = response.json()
        print(f"\n📊 Final Database State:")
        print(f"  Total nodes: {health.get('total_nodes', 0):,}")
        print(f"\n🌐 View graph at: {API_URL}/")
    except:
        pass
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
