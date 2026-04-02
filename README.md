# Expense Manager

A full-stack web application built with **Python**, **FastAPI**, and **MySQL** featuring a Bootstrap admin dashboard for managing personal expenses.

## GitHub Repository

[https://github.com/istkharali9319/pdf-link-validator.git](https://github.com/istkharali9319/pdf-link-validator.git)

---

## Features

- Login / Logout with session-based authentication
- Dashboard with monthly & yearly expense statistics
- Add, Edit, Delete expenses
- Expense categories: Food, Transport, Entertainment, Health, Shopping, Utilities, Other
- Bootstrap responsive admin UI
- Dockerized with MySQL

---

## Tech Stack

| Layer      | Technology          |
|------------|---------------------|
| Backend    | Python, FastAPI      |
| Database   | MySQL 8             |
| Frontend   | Bootstrap 5, Jinja2 |
| Auth       | Session cookies, bcrypt |
| Container  | Docker, Docker Compose |

---

## Project Structure

```
expanse-tracker/
├── main.py              # App routes & logic
├── auth.py              # Authentication helpers
├── models.py            # Database models
├── schemas.py           # Pydantic schemas
├── database.py          # DB connection
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image config
├── docker-compose.yml   # Local development setup
├── .dockerignore        # Docker ignore rules
├── static/              # CSS, JS, images
└── templates/           # HTML templates
    ├── login.html
    ├── dashboard.html
    └── expenses/
        ├── list.html
        ├── add.html
        └── edit.html
```

---

## Getting Started

### Option 1 — Run with Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/istkharali9319/pdf-link-validator.git
cd expanse-tracker

# Start app + MySQL together
docker compose up --build
```

Open **http://localhost:8000**

---

### Option 2 — Run Locally

**Requirements:** Python 3.8+, MySQL

```bash
# Clone the repository
git clone https://github.com/istkharali9319/pdf-link-validator.git
cd expanse-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt bcrypt==4.0.1

# Create .env file
cp .env.example .env
# Edit .env with your MySQL credentials

# Create database in MySQL
mysql -u root -p -e "CREATE DATABASE expense_manager;"

# Start the server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/expense_manager
SECRET_KEY=your-secret-key-here
```

> Never commit `.env` to Git. It is listed in `.gitignore`.

---

## Default Login Credentials

| Username | Password  |
|----------|-----------|
| admin    | admin123  |

> Change the password after first login in production.

---

## Docker Commands

```bash
# Build and start
docker compose up --build

# Run in background
docker compose up -d --build

# Stop containers
docker compose down

# View logs
docker logs expense_app

# Rebuild after code changes
docker compose up --build
```

---

## Deployment

This project is configured for CI/CD deployment on AWS EC2 using GitHub Actions.

- **CI/CD:** GitHub Actions
- **Registry:** Docker Hub
- **Server:** AWS EC2 (Ubuntu)

---

## License

MIT License
