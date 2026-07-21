import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class ContactInquiry(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=120)
    company: str = Field(default="", max_length=200)
    email: str = Field(min_length=1, max_length=254)
    message: str = Field(min_length=1, max_length=5_000)
    website: str = Field(default="", max_length=500)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_RE.match(value):
            raise ValueError("invalid email address")
        return value
