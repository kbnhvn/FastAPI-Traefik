import jwt
import os
import datetime
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Request

# Permet la creation de token JWT lors du login de l'user

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "role": data.get("role", "user")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Permet de vérifier et valider le token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Email not found")
        user = await User.objects.get_or_none(email=email)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is not valid")
    return user

async def get_current_role(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="User not allowed")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is not valid")
    # True si admin
    return True

# Pour gérer le forward auth depuis Traefik

async def forward_auth(request,token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is not valid")
    
    # Récupération du path et vérification route admin
    if "/admin" in request.url.path and role != "admin":
        raise HTTPException(status_code=403, detail="Admin role required")

    return {"status": "Authorized"}