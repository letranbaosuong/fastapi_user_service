"""
Redis Cache Module

KHÁI NIỆM:
- Redis: In-memory cache để tránh query database nhiều lần
- TTL: Time To Live - cache tự động expire sau 5 phút
- Cache Invalidation: Tự động xóa cache khi update/delete

USE CASES:
- Cache danh sách users (tránh query DB mỗi request)
- Cache project details
- Cache thống kê (stats) - giảm tải DB

VÍ DỤ:
get_users() -> Check cache trước -> Nếu không có -> Query DB -> Lưu cache
"""

import json
import redis
from typing import Optional, Any
from functools import wraps
import hashlib

from app.core.config import settings


# Redis Connection Pool (singleton)
# VÍ DỤ: Tái sử dụng connection thay vì tạo mới mỗi lần
redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """
    Get Redis client instance (singleton pattern)

    VÍ DỤ:
    redis_conn = get_redis()
    redis_conn.set("key", "value", ex=300)

    LƯU Ý: Connection được tái sử dụng, không tạo mới mỗi lần
    """
    global redis_client

    if redis_client is None:
        try:
            redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,  # Auto decode bytes to string
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            # Test connection
            redis_client.ping()
            print(f"✅ Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except redis.ConnectionError as e:
            print(f"⚠️ Redis connection failed: {e}")
            print("⚠️ Cache disabled - running without Redis")
            redis_client = None
        except Exception as e:
            print(f"⚠️ Redis error: {e}")
            redis_client = None

    return redis_client


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate unique cache key từ function name và parameters

    VÍ DỤ:
    key = generate_cache_key("get_users", skip=0, limit=10)
    => "get_users:hash_of_params"

    LƯU Ý: Hash để tránh key quá dài
    """
    # Combine all arguments
    key_parts = [prefix]

    # Add positional args
    if args:
        key_parts.extend([str(arg) for arg in args])

    # Add keyword args (sorted for consistency)
    if kwargs:
        sorted_kwargs = sorted(kwargs.items())
        key_parts.extend([f"{k}={v}" for k, v in sorted_kwargs])

    # Create hash to keep key short
    key_string = ":".join(key_parts)
    key_hash = hashlib.md5(key_string.encode()).hexdigest()[:8]

    return f"{prefix}:{key_hash}"


def set_cache(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Lưu data vào cache với TTL

    VÍ DỤ:
    set_cache("users_list", users_data, ttl=300)
    => Cache expire sau 5 phút

    RETURN: True nếu thành công, False nếu Redis không available
    """
    redis_conn = get_redis()

    if redis_conn is None:
        return False

    try:
        ttl_seconds = ttl if ttl is not None else settings.CACHE_TTL
        # Serialize to JSON
        json_value = json.dumps(value, default=str)
        redis_conn.setex(key, ttl_seconds, json_value)
        return True
    except Exception as e:
        print(f"⚠️ Cache set error: {e}")
        return False


def get_cache(key: str) -> Optional[Any]:
    """
    Lấy data từ cache

    VÍ DỤ:
    data = get_cache("users_list")
    if data:
        return data  # Cache hit
    else:
        # Cache miss - query DB
        ...

    RETURN: Data nếu có trong cache, None nếu không có hoặc expired
    """
    redis_conn = get_redis()

    if redis_conn is None:
        return None

    try:
        json_value = redis_conn.get(key)
        if json_value:
            return json.loads(json_value)
        return None
    except Exception as e:
        print(f"⚠️ Cache get error: {e}")
        return None


def delete_cache(pattern: str) -> int:
    """
    Xóa cache theo pattern (cache invalidation)

    VÍ DỤ:
    delete_cache("users:*")
    => Xóa tất cả cache liên quan đến users

    USE CASE:
    - User được update -> Xóa cache users
    - Project được delete -> Xóa cache projects

    RETURN: Số lượng keys đã xóa
    """
    redis_conn = get_redis()

    if redis_conn is None:
        return 0

    try:
        keys = redis_conn.keys(pattern)
        if keys:
            return redis_conn.delete(*keys)
        return 0
    except Exception as e:
        print(f"⚠️ Cache delete error: {e}")
        return 0


def cache_result(prefix: str, ttl: Optional[int] = None):
    """
    Decorator để tự động cache kết quả function

    VÍ DỤ:
    @cache_result("get_users", ttl=300)
    def get_users(skip: int, limit: int):
        return db.query(User).offset(skip).limit(limit).all()

    WORKFLOW:
    1. Check cache với key = prefix + params
    2. Nếu có cache -> return cache
    3. Nếu không -> execute function -> lưu cache -> return result

    LƯU Ý: Chỉ cache nếu Redis available, nếu không vẫn chạy bình thường
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = get_cache(cache_key)
            if cached_result is not None:
                print(f"🎯 Cache HIT: {cache_key}")
                return cached_result

            # Cache miss - execute function
            print(f"💾 Cache MISS: {cache_key}")
            result = func(*args, **kwargs)

            # Save to cache (convert SQLAlchemy objects to dict if needed)
            if hasattr(result, '__iter__') and not isinstance(result, (str, dict)):
                # List of objects - convert to dict
                try:
                    cache_data = [
                        obj.__dict__ if hasattr(obj, '__dict__') else obj
                        for obj in result
                    ]
                    # Remove SQLAlchemy internal keys
                    cache_data = [
                        {k: v for k, v in item.items() if not k.startswith('_')}
                        if isinstance(item, dict) else item
                        for item in cache_data
                    ]
                    set_cache(cache_key, cache_data, ttl)
                except Exception as e:
                    print(f"⚠️ Cache serialization error: {e}")
            elif hasattr(result, '__dict__'):
                # Single object - convert to dict
                try:
                    cache_data = {
                        k: v for k, v in result.__dict__.items()
                        if not k.startswith('_')
                    }
                    set_cache(cache_key, cache_data, ttl)
                except Exception as e:
                    print(f"⚠️ Cache serialization error: {e}")
            else:
                # Primitive types or dict
                set_cache(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def invalidate_cache_on_change(patterns: list):
    """
    Decorator để tự động xóa cache khi update/delete

    VÍ DỤ:
    @invalidate_cache_on_change(["users:*", "stats:*"])
    def update_user(db, user_id, data):
        ...

    USE CASE:
    - Update user -> Xóa cache users
    - Delete project -> Xóa cache projects
    - Create activity -> Xóa cache stats

    LƯU Ý: Xóa cache SAU KHI function thành công
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Execute function first
            result = func(*args, **kwargs)

            # If successful, invalidate cache
            for pattern in patterns:
                deleted_count = delete_cache(pattern)
                if deleted_count > 0:
                    print(f"🗑️ Cache invalidated: {pattern} ({deleted_count} keys)")

            return result

        return wrapper
    return decorator


def clear_all_cache() -> bool:
    """
    Xóa toàn bộ cache (dùng cho testing hoặc debug)

    VÍ DỤ:
    clear_all_cache()
    => Xóa tất cả cache trong Redis DB

    CẢNH BÁO: Chỉ dùng trong development hoặc testing
    """
    redis_conn = get_redis()

    if redis_conn is None:
        return False

    try:
        redis_conn.flushdb()
        print("🗑️ All cache cleared")
        return True
    except Exception as e:
        print(f"⚠️ Clear cache error: {e}")
        return False
