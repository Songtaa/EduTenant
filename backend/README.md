# 🎓 EduTenant – Multi-Tenant School Management System

EduTenant is a scalable, multi-tenant school management backend built with **FastAPI**, using **PostgreSQL** with separate schemas per tenant. It supports features like user/role/permission management, class scheduling, attendance, grading, and more — designed for educational institutions.

## ✨ Features

- 🏫 Multi-tenant architecture (separate schema per school)
- 🔐 JWT authentication with token revocation
- 👥 Role-Based Access Control (RBAC)
- 🧑‍🏫 Admin, Teacher, Student, and Parent roles
- 📦 Container-ready with Docker support
- ⚙️ Clean project structure with Repository Pattern
- 📄 Auto-generated Swagger UI per-tenant and for global routes

---

## 🛠 Project Setup

### Requirements

- Python 3.10+
- [Poetry](https://python-poetry.org/docs/#installation)
- PostgreSQL

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/songtaa/edutenant.git
cd edutenant


### Install Dependencies

- poetry install

### Set Environment Variables 

- cp .env.example .env

### Edit .env with your preffered settings


## Run the Application

- Poetry run uvicorn app.main:app --reload

- Global Docs: http://api.edutenant.localhost:8000/docs

- Tenant Docs: http://<tenant>.edutenant.localhost:8000/docs (e.g., school_alpha)


### Make sure your /etc/hosts looks something like: 

- 127.0.0.1 api.edutenant.localhost
- 127.0.0.1 school_alpha.edutenant.localhost




