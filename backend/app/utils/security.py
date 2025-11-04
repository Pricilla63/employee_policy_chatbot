from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config import get_settings

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"❌ Password verification error: {e}")
        return False

def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        print(f"❌ Password hashing error: {e}")
        raise

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    try:
        to_encode = data.copy()
        
        # Use timezone-aware datetime
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
        
    except Exception as e:
        print(f"❌ Token creation error: {e}")
        raise

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        print(f"❌ Token decoding error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected token error: {e}")
        return None

def validate_token(token: str) -> bool:
    """
    Validate if token is still valid
    """
    payload = decode_access_token(token)
    if payload is None:
        return False
    
    # Check expiration
    exp = payload.get("exp")
    if exp is None:
        return False
    
    # Convert exp to timezone-aware datetime
    exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
    return exp_datetime > datetime.now(timezone.utc)

def get_username_from_token(token: str) -> Optional[str]:
    """
    Extract username from token
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")
    return None

def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from token
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("user_id")
    return None