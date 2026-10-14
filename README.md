# Research Opportunity Portal

A web application where faculty members can post, view, update and manage research opportunities in one place. It has a REST API backend, a MySQL database and a simple frontend.

**GitHub Repository:** https://github.com/VoidSardar/research-opportunity-portal.git

**Author:** Abubakar Liaqat | Course: CN | Assignment 1

## Tech Stack

- **Backend:** Python, FastAPI
- **Database:** MySQL 8
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **API testing:** Postman

## Project Structure

```
research-opportunity-portal/
  backend/      FastAPI app (main.py, db.py, requirements.txt, .env.example)
  frontend/     index.html and app.js
  database/     schema.sql
  postman/      exported Postman collection
  README.md
```

## Prerequisites

- Python 3.9 or newer
- MySQL Server 8.x (running)
- Git
- Postman (for API testing)

## Setup and Run

### 1. Clone the repository

```
git clone https://github.com/VoidSardar/research-opportunity-portal.git
cd research-opportunity-portal
```

### 2. Create the database

Make sure MySQL is running, then run (Command Prompt, from the project folder):

```
mysql -u root -p < database\schema.sql
```

If `mysql` is not recognized, use the full path:

```
"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database\schema.sql
```

This creates the `research_portal` database and the `opportunities` table. The tables start empty; there is no hard-coded data.

### 3. Set up the backend

```
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a file named `.env` inside the `backend` folder (copy `.env.example`) and fill in your own MySQL password:

```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=research_portal
```

### 4. Start the backend

From the `backend` folder, with the virtual environment active:

```
uvicorn main:app --reload
```

The API runs at http://127.0.0.1:8000 and interactive docs are at http://127.0.0.1:8000/docs.

### 5. Start the frontend

Open a second terminal:

```
cd frontend
python -m http.server 5500
```

Open http://127.0.0.1:5500 in your browser.

## API Endpoints

| Method | Endpoint                 | Description                                     | Success code |
| ------ | ------------------------ | ----------------------------------------------- | ------------ |
| POST   | `/api/opportunities`     | Create an opportunity                           | 201          |
| GET    | `/api/opportunities`     | Get all opportunities                           | 200          |
| GET    | `/api/opportunities/:id` | Get one opportunity                             | 200          |
| PUT    | `/api/opportunities/:id` | Update an opportunity (partial updates allowed) | 200          |
| DELETE | `/api/opportunities/:id` | Delete an opportunity                           | 200          |

Error codes: **400** for invalid or missing data, **404** when the ID does not exist, **500** for server or database errors.

## Opportunity Fields

`id`, `title`, `description`, `research_area`, `faculty_name`, `department`, `required_skills`, `available_positions`, `application_deadline`, `status` (Open or Closed)

## Testing with Postman

1. Start the backend.
2. In Postman, click **Import** and select `postman/research-portal.postman_collection.json`.
3. Run requests 01 to 10 in order. They cover creating three opportunities, get all, get one, update, close, delete, a 404 after deletion, and a 400 for invalid data.

## Frontend Features

- View all opportunities and the full details of one
- Create, edit and delete opportunities
- Close an open opportunity with one click
- Form validation and success/error messages

## Notes

- The `.env` file is not committed to GitHub; use `backend/.env.example` as a template.
- The frontend expects the backend at `http://127.0.0.1:8000`.
