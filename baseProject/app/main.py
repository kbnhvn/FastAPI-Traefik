from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from app.db import database, User

# Pour la gestion des hash mots de passe
from passlib.context import CryptContext
# Configuration de passlib (deprecated=auto permet d'utiliser les algos les plus sécurisés)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Permet la vérification de la valeur email = type email
class UserSignup(BaseModel):
    email: EmailStr
    password: str

description= """
## User

** User is defined by : **
- First name
- Last name
- Password
- Mail (unique)
- City

** All values are required except city **

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

@app.get("/", name='Get all users', tags=['Users'])
async def read_root():
    return await User.objects.all()

# --------- Routes POST --------- #

@app.post("/signup", name='User Signup', tags=['Users', 'Signup'])
async def signup(user: UserSignup):
    # Vérification de la longueur du mot de passe
    if len(user.password) <8:
        raise HTTPException(status_code=422, detail="Password must have at least 8 characters")
    try:
        hashed_password = pwd_context.hash(user.password)
        new_user = await User.objects.create(email=user.email, password=hashed_password, active=True)
        return {"email": new_user.email, "active": new_user.active}
    except UniqueColumnsViolationError:
        # Cette exception est levée si l'email fourni est déjà utilisé
        raise HTTPException(status_code=400, detail="This email already exists")

@app.get("/login", name='User login', tags=['Users','Login'])
async def login(email: str, password: str):
    user = await User.objects.get_or_none(email=email)
    if user and pwd_context.verify(password, user.password):
        return {"message": "User logged in successfully."}
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