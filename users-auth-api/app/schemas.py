from pydantic import BaseModel, EmailStr, Field

class RegisterIn(BaseModel):
    fullname: str = Field(..., min_length=3, max_length=500)
    email: EmailStr
    password: str
    role: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    email: str
    fullname: str
    role: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_verified: bool
    is_active: bool

    class Config:
        from_attributes = True
