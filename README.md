# Balitech Survey System

A modern, multi-user survey and feedback system, built with Flask, PostgreSQL, and deployable to Render.

## 🎯 Features

- **User Authentication**: Secure registration and login with password hashing
- **Feedback Submission**: Users can submit responses/comments for overall or topic-specific questions
- **Admin Dashboard**: Manage menu items, questions, and view feedback reports
- **REST API**: JSON-based API endpoints for data exchange
- **Multi-role Support**: User and Admin roles with role-based access control
- **Production Ready**: Configured for deployment on Render with managed PostgreSQL

## 🏗️ System Architecture

### Three-Layer Architecture

1. **Client (Frontend)**
   - HTML/CSS/JavaScript with Bootstrap
   - Forms for registration, login, and feedback submission
   - Admin dashboard for CRUD operations
   - Dynamic UI updates via Fetch API

2. **Middleware (Flask Backend)**
   - RESTful API endpoints returning JSON
   - User authentication and session management
   - CRUD operations for menu items, questions, and feedback
   - Business logic and validation

3. **Database (PostgreSQL)**
   - Users table (authentication)
   - MenuItems table (restaurant menu)
   - Questions table (dynamic questions per item/overall)
   - Feedback table (user responses and comments)

### Database Schema

```
Users
├── id (PK)
├── username
├── email
├── password_hash
├── role (user/admin)
└── created_at

MenuItems (topics)
├── id (PK)
├── item_name
├── description
└── created_at

Questions
├── id (PK)
├── question_text
├── menu_item_id (FK, nullable for overall)
└── created_at

Feedback (responses)
├── id (PK)
├── user_id (FK)
├── question_id (FK)
├── menu_item_id (FK, nullable)
├── comment (free-text response)
└── created_at
```

## 📋 Project Structure

```
Balitech feedback system/
├── app.py                 # Flask app factory and initialization
├── models.py             # SQLAlchemy models
├── config.py             # Configuration management
├── requirements.txt      # Python dependencies
├── Procfile             # Render deployment config
├── .gitignore           # Git ignore rules
├── init_db_postgres.py  # Database initialization script
├── README.md            # This file
├── routes/
│   ├── auth.py         # Login/Register routes
│   ├── feedback.py      # User feedback routes
│   └── admin.py        # Admin CRUD routes
└── templates/
    ├── base.html       # Base template
    ├── login.html      # Login page
    ├── register.html   # Registration page
    ├── dashboard.html  # User feedback dashboard
    └── admin_dashboard.html  # Admin dashboard
```

## 🚀 Setup Instructions

### Local Development

#### Prerequisites
- Python 3.8+
- PostgreSQL 12+ (running locally or accessible)
- Git

#### 1. Clone Repository
```bash
git clone <repository-url>
cd "Balitech feedback system"
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=postgresql://username:password@localhost:5432/balitech_db
```

#### 5. Create PostgreSQL Database
```bash
createdb balitech_db
```

#### 6. Initialize Database
```bash
python init_db_postgres.py
```

Test credentials will be printed to the console.

#### 7. Run Flask App
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

### Test Credentials (After init_db_postgres.py)
- **Admin**: username=`admin`, password=`admin123`
- **User**: username=`customer1`, password=`password123`

## 🌐 API Endpoints

### Authentication Routes
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/logout` - User logout

### Feedback Routes (User)
- `GET /feedback/dashboard` - Main feedback page
- `GET /feedback/api/menu_items` - Get all menu items (JSON)
- `GET /feedback/api/questions/<item_id>` - Get questions for item (JSON)
- `POST /feedback/api/submit_feedback` - Submit feedback (JSON)

### Admin Routes
- `GET /admin/dashboard` - Admin dashboard page
- `GET /admin/api/menu_items` - List all menu items (JSON)
- `POST /admin/api/menu_items` - Create menu item (JSON)
- `PUT /admin/api/menu_items/<id>` - Update menu item (JSON)
- `DELETE /admin/api/menu_items/<id>` - Delete menu item
- `GET /admin/api/questions` - List all questions (JSON)
- `POST /admin/api/questions` - Create question (JSON)
- `PUT /admin/api/questions/<id>` - Update question (JSON)
- `DELETE /admin/api/questions/<id>` - Delete question
- `GET /admin/api/feedback_reports` - Get all feedback (JSON)

## 🚢 Deployment on Render

### Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Initial commit: Balitech Feedback System"
git push origin main
```

### Step 2: Create Render Account
1. Visit [render.com](https://render.com)
2. Sign up and connect your GitHub account

### Step 3: Create PostgreSQL Database
1. In Render dashboard, click "New +"
2. Select "PostgreSQL"
3. Fill in details:
   - Name: `balitech-db`
   - Region: Choose closest to you
4. Create database
5. Copy the `DATABASE_URL` from the database details page

### Step 4: Deploy Web Service
1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Fill in details:
   - Name: `balitech-feedback`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt && python init_db_postgres.py`
   - Start Command: `gunicorn app:create_app()`
5. Click "Create Web Service"

### Step 5: Set Environment Variables
1. In Web Service settings, go to "Environment"
2. Add variables:
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: (generate a random secure key)
   - `DATABASE_URL`: (paste the URL from your PostgreSQL database)
   - `PORT`: `10000` (Render default)

### Step 6: Verify Deployment
1. Once deployed, visit your Render URL
2. Test with admin credentials from init script
3. Create new users and submit feedback

## 📝 Data Flow Examples

### User Submitting Feedback
1. User logs in → Session created
2. User selects menu item → GET `/feedback/api/menu_items`
3. User selects question → GET `/feedback/api/questions/<item_id>`
4. User rates and comments → POST `/feedback/api/submit_feedback` (JSON)
5. Flask validates, inserts into DB → Returns success JSON
6. Frontend shows "Thank You" message

### Admin Managing Menu Items
1. Admin logs in → Verified via session
2. Admin submits new item → POST `/admin/api/menu_items` (JSON)
3. Flask creates item in DB → Returns item JSON
4. Admin can view, update, delete via API
5. Questions can be linked to items

## 🔐 Security Features

- ✅ Password hashing with `werkzeug.security`
- ✅ Session-based authentication
- ✅ Role-based access control (user vs admin)
- ✅ Input validation on all endpoints
- ✅ CSRF protection ready (add Flask-WTF if needed)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ⚠️ **TODO**: Add HTTPS enforcement for production

## ✅ Requirements Compliance Matrix

### Functional Requirements

- ✅ User Authentication (Register/Login)
   - Implemented in `routes/auth.py` via `POST /auth/register` and `POST /auth/login`.
- ✅ CRUD Operations
   - Menu Items: `GET/POST/PUT/DELETE /admin/api/menu_items`.
   - Questions: `GET/POST/PUT/DELETE /admin/api/questions`.
   - Feedback: Create via `POST /feedback/api/submit_feedback`, Read via `GET /admin/api/feedback_reports`.
- ✅ Data fields based on scenario
   - `models.py` defines `users`, `menu_items`, `questions`, `feedbacks` with fields for comment/response and item/overall linking.

### Integration Requirements

- ✅ REST API (GET and POST)
   - Implemented across `/auth`, `/feedback/api/*`, and `/admin/api/*` endpoints.
- ✅ JSON data format
   - API endpoints consume and return JSON (`request.get_json()`, `jsonify(...)`).
- ✅ Client-Server Architecture explanation
   - Documented in the System Architecture and Data Flow sections of this README.
- ✅ Middleware (Flask)
   - Flask handles routing, sessions, validation, and API responses in route blueprints.
- ✅ Basic Security (validation/login)
   - Password hashing, session-based login, role checks, and input validation are implemented.
- ✅ Database Integration
   - PostgreSQL integration through SQLAlchemy models and ORM queries.

### Technical Requirements

- ✅ Flask routing
   - Blueprints: `auth_bp`, `feedback_bp`, `admin_bp`.
- ✅ Working CRUD
   - Implemented for menu items and question sets via admin APIs.
- ✅ Database connection
   - Configured through `DATABASE_URL` in `config.py` and initialized in `app.py`.
- ✅ JSON responses
   - Standardized JSON responses for API success/error paths.
- ✅ Organized code
   - Structured into app factory, models, route blueprints, templates, and setup scripts.
- ✅ Error handling
   - Route-level validation errors plus global API-aware 404/500 handlers in `app.py`.

## 🧪 Testing Locally

### Create Test Data
```bash
python init_db_postgres.py
```

### Test API with curl
```bash
# Register
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'

# Get menu items
curl http://localhost:5000/feedback/api/menu_items
```

## 🛠️ Development Tips

1. **Enable Debug Mode**: Set `FLASK_DEBUG=1` in `.env`
2. **Database Migrations**: If you modify models, recreate with `python init_db_postgres.py`
3. **Check Logs**: Use `flask run` to see request logs
4. **Test Endpoints**: Use tools like Postman or Thunder Client
5. **Frontend Changes**: Use Bootstrap classes in templates for consistency

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)
- [Render Deployment](https://render.com/docs)
- [PostgreSQL Guide](https://www.postgresql.org/docs/)

## 👥 Team Responsibilities (8-Person Team)

Based on the 3-week sprint plan:

### Backend (3-4 people)
- Flask app structure ✅
- Authentication module
- API endpoints
- Database schema and queries

### Frontend (2-3 people)
- HTML/CSS templates
- JavaScript fetch requests
- Form validation
- UI/UX improvements

### DevOps (1 person)
- Database setup
- Environment configuration
- Render deployment
- CI/CD pipeline

### QA (1-2 people)
- Manual testing
- Security testing
- Cross-browser testing
- API validation

## 📅 3-Week Development Timeline

**Week 1 (Apr 29 - May 5)**: Foundation & Database Setup
- Database schema finalization
- Flask environment setup
- Basic authentication
- Static templates

**Week 2 (May 6 - May 12)**: Core Features & Integration
- REST API endpoints
- User feedback submission
- Admin CRUD operations
- Dynamic UI updates

**Week 3 (May 13 - May 19)**: Testing & Deployment
- Error handling and validation
- Security testing
- Render deployment
- Final documentation

## 📞 Support & Troubleshooting

### Common Issues

**Database Connection Error**
```
Check DATABASE_URL format: postgresql://user:password@host:port/database
Ensure PostgreSQL is running
```

**ImportError with models**
```
Make sure you're in the project directory
Install requirements: pip install -r requirements.txt
```

**Port Already in Use**
```
flask run --port 5001
```

---

Built with ❤️ for Balitech Restaurant | Last Updated: April 30, 2026
