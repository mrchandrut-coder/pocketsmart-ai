from typing import Optional

from pydantic import BaseModel, Field, field_validator

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-zA-Z0-9_.-]+$")
    email: Optional[str] = Field(default=None, max_length=254)
    full_name: Optional[str] = Field(default=None, max_length=120)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username", "email", "full_name", mode="before")
    @classmethod
    def strip_optional_text(cls, value):
        return value.strip() if isinstance(value, str) else value

    @field_validator("password")
    @classmethod
    def enforce_bcrypt_byte_limit(cls, value):
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed bcrypt's 72-byte limit")
        return value

class UserInDB(User):
    hashed_password: str
