from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    full_name: str = Field(..., min_length=1, max_length=255)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[UserOut] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6, description="New password with minimum 6 characters")


class OAuthLoginRequest(BaseModel):
    provider: str = Field(..., description="Provider name e.g. google, github")
    email: EmailStr
    full_name: Optional[str] = None
    access_token: Optional[str] = None
    id_token: Optional[str] = None
    provider_user_id: Optional[str] = None


class OAuthCallbackRequest(BaseModel):
    provider: str
    code: str
    redirect_uri: Optional[str] = None


class OAuthUrlOut(BaseModel):
    provider: str
    auth_url: str
    is_mock: bool = False
