# Expense Manager

A full-stack web application built with **Python**, **FastAPI**, and **MySQL** featuring a Bootstrap admin dashboard for managing personal expenses.

## GitHub Repository

[https://github.com/istkharali9319/expanse-tracker](https://github.com/istkharali9319/expanse-tracker)

## Screenshots

![Login Page](static/screenshots/login.png)

---

## Live Demo

```
http://3.26.242.21:8000
```

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
| CI/CD      | GitHub Actions      |
| Registry   | Docker Hub          |
| Server     | AWS EC2 (Ubuntu 24.04) |

---

## Project Structure

```
expanse-tracker/
├── main.py                          # App routes & logic
├── auth.py                          # Authentication helpers
├── models.py                        # Database models
├── schemas.py                       # Pydantic schemas
├── database.py                      # DB connection
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker image config
├── docker-compose.yml               # Local development setup
├── docker-compose.prod.yml          # Production setup
├── .env.example                     # Environment variables example
├── .dockerignore                    # Docker ignore rules
├── .gitignore                       # Git ignore rules
├── .github/
│   └── workflows/
│       └── deploy.yml               # GitHub Actions CI/CD pipeline
├── static/                          # CSS, JS, images
└── templates/                       # HTML templates
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
git clone https://github.com/istkharali9319/expanse-tracker.git
cd expanse-tracker

# Copy env file and update credentials
cp .env.example .env

# Start app + MySQL together
docker compose up --build
```

Open **http://localhost:8000**

---

### Option 2 — Run Locally

**Requirements:** Python 3.8+, MySQL

```bash
# Clone the repository
git clone https://github.com/istkharali9319/expanse-tracker.git
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
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@db/expense_manager
SECRET_KEY=your-secret-key-here
MYSQL_ROOT_PASSWORD=your-mysql-password
MYSQL_DATABASE=expense_manager
APP_PORT=8000
DB_PORT=3306
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
# Build and start locally
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

## CI/CD Pipeline

This project uses **GitHub Actions** for automated deployment to **AWS EC2**.

### How It Works

```
Push code to main branch
        ↓
GitHub Actions triggers automatically
        ↓
Build Docker image
        ↓
Push image to Docker Hub (istkharali9319/expense-trackor)
        ↓
SSH into AWS EC2 server
        ↓
Copy docker-compose.prod.yml to EC2
        ↓
Pull latest Docker image
        ↓
Restart containers
        ↓
App live at http://3.26.242.21:8000
```

### Pipeline File

Located at [.github/workflows/deploy.yml](.github/workflows/deploy.yml)

### GitHub Secrets Required

| Secret | Description |
|--------|-------------|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token |
| `EC2_HOST` | AWS EC2 public IP address |
| `EC2_USER` | EC2 SSH username (`ubuntu`) |
| `EC2_SSH_KEY` | Contents of `.pem` private key file |

### EC2 Server Setup

- **Provider:** AWS EC2
- **OS:** Ubuntu 24.04 LTS
- **Instance:** t3.micro (Free tier)
- **Docker:** v28.2.2
- **Docker Compose:** v5.1.1

### Production .env on EC2

Create `/home/ubuntu/expense-trackor/.env` on EC2 with:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@db/expense_manager
SECRET_KEY=your-secret-key-here
MYSQL_ROOT_PASSWORD=your-mysql-password
MYSQL_DATABASE=expense_manager
APP_PORT=8000
DB_PORT=3306
```

---

## License

MIT License
