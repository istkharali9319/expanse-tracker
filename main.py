import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, datetime
from typing import Optional
from dotenv import load_dotenv

import models
import auth
from database import engine, get_db, SessionLocal

load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=engine)

# Create default admin user
def init_db():
    db = SessionLocal()
    try:
        auth.create_default_admin(db)
    finally:
        db.close()

init_db()

app = FastAPI(title="Expense Manager")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

CATEGORIES = ["Food", "Transport", "Entertainment", "Health", "Shopping", "Utilities", "Other"]


# ─── Helpers ────────────────────────────────────────────────────────────────

def flash(request: Request, message: str, category: str = "success"):
    if "_flash" not in request.session:
        request.session["_flash"] = []
    request.session["_flash"].append({"message": message, "category": category})


def get_flashed_messages(request: Request):
    messages = request.session.pop("_flash", [])
    return messages


# Because we're not using Starlette's SessionMiddleware (we use signed cookies),
# we manage flash messages via a simple cookie-based approach through the response.
# Instead, we'll pass flash as a query param for simplicity.

# ─── Root ────────────────────────────────────────────────────────────────────

@app.get("/")
async def root(request: Request):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
    finally:
        db.close()
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return RedirectResponse(url="/login", status_code=302)


# ─── Login ───────────────────────────────────────────────────────────────────

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: Optional[str] = None, msg: Optional[str] = None):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
    finally:
        db.close()
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {
        "request": request,
        "error": error,
        "msg": msg,
    })


@app.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
):
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user or not auth.verify_password(password, user.hashed_password):
            return RedirectResponse(
                url="/login?error=Invalid+username+or+password",
                status_code=302
            )
        cookie_value = auth.create_session_cookie(user.id)
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key=auth.SESSION_COOKIE_NAME,
            value=cookie_value,
            httponly=True,
            max_age=auth.SESSION_MAX_AGE,
            samesite="lax",
        )
        return response
    finally:
        db.close()


# ─── Logout ──────────────────────────────────────────────────────────────────

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login?msg=You+have+been+logged+out", status_code=302)
    response.delete_cookie(key=auth.SESSION_COOKIE_NAME)
    return response


# ─── Dashboard ───────────────────────────────────────────────────────────────

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        today = date.today()
        current_month = today.month
        current_year = today.year

        # Total expenses this month
        monthly_total = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user.id,
            extract("month", models.Expense.date) == current_month,
            extract("year", models.Expense.date) == current_year,
        ).scalar() or 0.0

        # Total expenses this year
        yearly_total = db.query(func.sum(models.Expense.amount)).filter(
            models.Expense.user_id == user.id,
            extract("year", models.Expense.date) == current_year,
        ).scalar() or 0.0

        # Total number of expense records
        total_count = db.query(func.count(models.Expense.id)).filter(
            models.Expense.user_id == user.id
        ).scalar() or 0

        # Recent 5 expenses
        recent_expenses = db.query(models.Expense).filter(
            models.Expense.user_id == user.id
        ).order_by(models.Expense.date.desc(), models.Expense.created_at.desc()).limit(5).all()

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "user": user,
            "monthly_total": monthly_total,
            "yearly_total": yearly_total,
            "total_count": total_count,
            "recent_expenses": recent_expenses,
            "current_month_name": today.strftime("%B"),
            "current_year": current_year,
        })
    finally:
        db.close()


# ─── Expenses List ────────────────────────────────────────────────────────────

@app.get("/expenses", response_class=HTMLResponse)
async def expenses_list(request: Request, msg: Optional[str] = None, error: Optional[str] = None):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        expenses = db.query(models.Expense).filter(
            models.Expense.user_id == user.id
        ).order_by(models.Expense.date.desc(), models.Expense.created_at.desc()).all()

        return templates.TemplateResponse("expenses/list.html", {
            "request": request,
            "user": user,
            "expenses": expenses,
            "msg": msg,
            "error": error,
        })
    finally:
        db.close()


# ─── Add Expense ──────────────────────────────────────────────────────────────

@app.get("/expenses/add", response_class=HTMLResponse)
async def add_expense_form(request: Request, error: Optional[str] = None):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        return templates.TemplateResponse("expenses/add.html", {
            "request": request,
            "user": user,
            "categories": CATEGORIES,
            "today": date.today().isoformat(),
            "error": error,
        })
    finally:
        db.close()


@app.post("/expenses/add")
async def add_expense_submit(
    request: Request,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date: str = Form(...),
    description: Optional[str] = Form(None),
):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        if category not in CATEGORIES:
            return RedirectResponse(
                url="/expenses/add?error=Invalid+category+selected",
                status_code=302,
            )

        parsed_date = datetime.strptime(expense_date, "%Y-%m-%d").date()

        expense = models.Expense(
            user_id=user.id,
            title=title.strip(),
            amount=amount,
            category=category,
            date=parsed_date,
            description=description.strip() if description else None,
        )
        db.add(expense)
        db.commit()
        return RedirectResponse(url="/expenses?msg=Expense+added+successfully", status_code=302)
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/expenses/add?error=Failed+to+add+expense",
            status_code=302,
        )
    finally:
        db.close()


# ─── Edit Expense ─────────────────────────────────────────────────────────────

@app.get("/expenses/edit/{expense_id}", response_class=HTMLResponse)
async def edit_expense_form(request: Request, expense_id: int, error: Optional[str] = None):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        expense = db.query(models.Expense).filter(
            models.Expense.id == expense_id,
            models.Expense.user_id == user.id,
        ).first()

        if not expense:
            return RedirectResponse(url="/expenses?error=Expense+not+found", status_code=302)

        return templates.TemplateResponse("expenses/edit.html", {
            "request": request,
            "user": user,
            "expense": expense,
            "categories": CATEGORIES,
            "error": error,
        })
    finally:
        db.close()


@app.post("/expenses/edit/{expense_id}")
async def edit_expense_submit(
    request: Request,
    expense_id: int,
    title: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date: str = Form(...),
    description: Optional[str] = Form(None),
):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        expense = db.query(models.Expense).filter(
            models.Expense.id == expense_id,
            models.Expense.user_id == user.id,
        ).first()

        if not expense:
            return RedirectResponse(url="/expenses?error=Expense+not+found", status_code=302)

        if category not in CATEGORIES:
            return RedirectResponse(
                url=f"/expenses/edit/{expense_id}?error=Invalid+category+selected",
                status_code=302,
            )

        parsed_date = datetime.strptime(expense_date, "%Y-%m-%d").date()

        expense.title = title.strip()
        expense.amount = amount
        expense.category = category
        expense.date = parsed_date
        expense.description = description.strip() if description else None

        db.commit()
        return RedirectResponse(url="/expenses?msg=Expense+updated+successfully", status_code=302)
    except Exception as e:
        db.rollback()
        return RedirectResponse(
            url=f"/expenses/edit/{expense_id}?error=Failed+to+update+expense",
            status_code=302,
        )
    finally:
        db.close()


# ─── Delete Expense ───────────────────────────────────────────────────────────

@app.post("/expenses/delete/{expense_id}")
async def delete_expense(request: Request, expense_id: int):
    db = SessionLocal()
    try:
        user = auth.get_current_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)

        expense = db.query(models.Expense).filter(
            models.Expense.id == expense_id,
            models.Expense.user_id == user.id,
        ).first()

        if not expense:
            return RedirectResponse(url="/expenses?error=Expense+not+found", status_code=302)

        db.delete(expense)
        db.commit()
        return RedirectResponse(url="/expenses?msg=Expense+deleted+successfully", status_code=302)
    except Exception as e:
        db.rollback()
        return RedirectResponse(url="/expenses?error=Failed+to+delete+expense", status_code=302)
    finally:
        db.close()
