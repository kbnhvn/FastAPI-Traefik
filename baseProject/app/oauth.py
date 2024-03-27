import jwt
import os
import datetime
from app.db import User
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, Request

# Permet la creation de token JWT lors du login de l'user

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "role": data.get("role", "user")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Permet de vérifier et valider le token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Permet de vérifier le role dans le token ou cookie

async def get_current_role(request: Request, token: str = Depends(oauth2_scheme)):
    # Essaye d'obtenir le token depuis l'en-tête 'Authorization'
    token_from_header = token

    if token_from_header:
        # Extrait le token sans le préfixe 'Bearer'
        token = token_from_header.replace("Bearer ", "")
    else:
        # Si aucun token dans l'en-tête, tente d'obtenir le token depuis le cookie
        token_from_cookie = request.cookies.get("auth_token")
        if not token_from_cookie:
            raise HTTPException(status_code=401, detail="Non autorisé")
        token = token_from_cookie

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if role != "admin":
            raise HTTPException(status_code=403, detail="Accès refusé")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    # Continue si le token est valide et le rôle est 'admin'
    return True
 

# Pour gérer le forward auth depuis Traefik

async def forward_auth(request: Request):
    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token is not valid")
    try:
        # Retrait du Bearer
        token = token.replace("Bearer ", "") if token.startswith("Bearer ") else token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role: str = payload.get("role")
        if "/admin" in request.url.path and role != "admin":
            raise HTTPException(status_code=403, detail="Admin role required")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token is not valid")
    return {"status": "Authorized"}