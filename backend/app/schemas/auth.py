import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


class _EmailIn(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def _lower(cls, v: str) -> str:
        return v.lower()


class SignupIn(_EmailIn):
    org_name: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=10, max_length=128)


class LoginIn(_EmailIn):
    password: str = Field(max_length=128)


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    user_id: uuid.UUID
    org_id: uuid.UUID
