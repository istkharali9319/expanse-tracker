from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str
    date: date
    description: Optional[str] = None


class ExpenseUpdate(BaseModel):
    title: str
    amount: float
    category: str
    date: date
    description: Optional[str] = None


class ExpenseOut(BaseModel):
    id: int
    user_id: int
    title: str
    amount: float
    category: str
    date: date
    description: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
