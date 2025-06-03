import redis

try:
    r = redis.Redis(host="127.0.0.1", port=6379, db=1)
    r.ping()
    print("✅ Redis connection successful")
except Exception as e:
    print("❌ Redis connection failed:", e)
