from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Inquiry(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    message: str = Field(..., min_length=10, max_length=2000)
    source: Optional[str] = Field('website', description='Lead source')

class Project(BaseModel):
    title: str
    category: str
    location: Optional[str] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
