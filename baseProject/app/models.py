from pydantic import BaseModel, EmailStr

# Définition de la structure des données pour les users

class UserSignup(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str
    city: str
    role: str = "user"