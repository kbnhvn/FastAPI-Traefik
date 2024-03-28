import jwt
import os
import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request

# Permet la creation de token JWT lors du login de l'user

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "role": data.get("role", "user")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Permet de vérifier et valider le token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Permet de vérifier le token ou cookie

async def get_user_authenticated(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=401, detail="Denied")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Retourne le payload pour une utilisation ultérieure
        return payload  
    except jwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail="Token not valid")