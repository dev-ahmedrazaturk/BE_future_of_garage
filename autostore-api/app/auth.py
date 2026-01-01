import os
from fastapi.params import Depends
import jwt
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Dict

# Secret key to decode the JWT token, this should match with the user authentication service's secret
SECRET_KEY = os.getenv("JWT_SECRET", "supersecretkey")
ALGORITHM = "HS256"

# OAuth2PasswordBearer is used to extract the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Function to decode JWT token and extract user data
def decode_access_token(token: str) -> Dict:
    try:
        # Decode the JWT token with the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # This will contain user information like user_id, username, etc.
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Dependency to extract the current user from the JWT token
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    payload = decode_access_token(token)
    return payload  # Contains user_id, username, etc.
