from fastapi import FastAPI, HTTPException, Depends
from app.db import database, User
from app.models import UserSignup, LoginData
from app.oauth import create_access_token, get_current_user, get_current_role, forward_auth, oauth2_scheme

# Utilisé pour la vérification de l'unicité de l'email
from asyncpg.exceptions import UniqueViolationError
# Pour la gestion des hash mots de passe
from passlib.context import CryptContext
# Configuration de passlib (deprecated=auto permet d'utiliser les algos les plus sécurisés)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

description= """
## User

**User is defined by :**
- First name
- Last name
- Password
- Mail (unique)
- City

**All values are required except city**

## Features

### Users
- Get all users
- Signup (create new user, verify if email already exists)
- Login (Verify if mail/password exists)

#### Tools
- Check the health and functionality of the API

"""

app = FastAPI(
    title="FastAPI, Docker, and Traefik",
    summary="This API allow you to create user et check if user exist.",
    description=description,
    contact={
        "name": "Joel LOURENCO",
        "email": "joel.lourenco.pro@gmail.com",
    },
)

# --------- Routes GET --------- #

@app.get("/users", name='Get all users', tags=['Users'])
async def getAllUsers(current_user: User = Depends(get_current_role)):
    users = await User.objects.all()
    # Convertion en dictionnaire, puis retrait du mot de passe
    users_data = [user.dict(exclude={"password"}) for user in users]
    return users_data

# ROUTE FORWARD AUTH POUR TRAEFIK (vérification du token JWT et role)
@app.get("/forward-auth")
async def forward_auth_route(request: Request, token: str = Depends(oauth2_scheme)):
    return await forward_auth(request, token)

# --------- Routes POST --------- #

@app.post("/signup", name='User Signup', tags=['Users', 'Signup'])
async def signup(user: UserSignup):
    # Vérification de la longueur du mot de passe
    if len(user.password) <8:
        raise HTTPException(status_code=422, detail="Password must have at least 8 characters")
    try:
        hashed_password = pwd_context.hash(user.password)
        new_user = await User.objects.create(firstName=user.firstName, lastName=user.lastName, city=user.city, email=user.email, password=hashed_password, active=True)
        return {"email": new_user.email, "active": new_user.active}
    except UniqueViolationError:
        # Cette exception est levée si l'email fourni est déjà utilisé
        raise HTTPException(status_code=400, detail="This email already exists")

@app.post("/login", name='User login', tags=['Users','Login'])
async def login(data: LoginData):
    user = await User.objects.get_or_none(email=data.email)
    if user and pwd_context.verify(data.password, user.password):
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=404, detail="User not found or password is incorrect")

# --------- Utilities --------- #

@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()
    # # create a dummy entry
    # await User.objects.get_or_create(email="test@test.com")

@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()

@app.get('/health', name='Health check', tags=['Tools'])
async def health_check():
    return {"status": "ok"}