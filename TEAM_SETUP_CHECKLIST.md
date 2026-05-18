# Team Setup Checklist

Quick checklist for all 8 team members to set up the project locally and start contributing.

## ✅ Day 1: Individual Setup (Everyone)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd "Balitech feedback system"
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create .env File
Copy `.env.example` to `.env`:
```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env
```

Edit `.env` with your database URL:
```
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key-here
DATABASE_URL=postgresql://username:password@localhost:5432/balitech_db
```

### Step 5: Set Up Local PostgreSQL

**Option A: Using Docker (Easiest)**
```bash
docker run --name balitech-db \
  -e POSTGRES_USER=balitech \
  -e POSTGRES_PASSWORD=balitech123 \
  -e POSTGRES_DB=balitech_db \
  -p 5432:5432 \
  -d postgres:15
```

Update your `.env`:
```
DATABASE_URL=postgresql://balitech:balitech123@localhost:5432/balitech_db
```

**Option B: Local PostgreSQL Installation**
1. Install PostgreSQL from [postgresql.org](https://www.postgresql.org/download/)
2. Create database:
   ```bash
   createdb balitech_db
   ```
3. Update `.env` with your credentials

### Step 6: Initialize Database
```bash
python init_db_postgres.py
```

You should see:
```
✓ Tables created successfully
✓ Users created
✓ Menu items created
✓ Overall questions created
✓ Item-specific questions created
✓ Sample feedback created

DATABASE INITIALIZATION COMPLETE!

Test Credentials:
  Admin User:
    Username: admin
    Password: admin123

  Test User:
    Username: customer1
    Password: password123
```

### Step 7: Run Flask App
```bash
python app.py
```

Visit `http://localhost:5000` and test login with provided credentials.

### Step 8: Verify Your Setup
- [ ] Can access login page
- [ ] Can login with `admin`/`admin123`
- [ ] Can login with `customer1`/`password123`
- [ ] Admin can see Admin Dashboard
- [ ] Can submit feedback as user
- [ ] No errors in terminal

If all pass, you're ready to develop! ✅

---

## 👥 Team Roles & Responsibilities

### Backend Team (Leads: 2 people)

**Tasks:**
- Implement API endpoints from `routes/` directory
- Handle database queries using SQLAlchemy
- Implement validation and error handling
- Test API with Postman or curl
- Document API endpoints

**Key Files to Modify:**
- `routes/auth.py` - Authentication logic
- `routes/feedback.py` - User feedback API
- `routes/admin.py` - Admin CRUD operations
- `models.py` - Database models (if schema changes)

**First Week Goals:**
- Complete authentication flow
- Test register/login endpoints
- Create all REST API endpoints

**Timeline:** Week 1-2, finish 80% in Week 2

---

### Frontend Team (Leads: 2 people)

**Tasks:**
- Design and code HTML/CSS templates
- Implement JavaScript for form handling
- Call backend API endpoints using Fetch
- Handle JSON responses and display data
- Improve UI/UX with Bootstrap

**Key Files to Modify:**
- `templates/base.html` - Base layout
- `templates/login.html` - Login form
- `templates/register.html` - Registration form
- `templates/dashboard.html` - User feedback form
- `templates/admin_dashboard.html` - Admin interface

**First Week Goals:**
- Create clean, responsive login/register pages
- Basic styling with Bootstrap

**Timeline:** Week 1-2, finish 80% in Week 2

---

### DevOps/Database Team (1 person)

**Tasks:**
- Set up and manage PostgreSQL database
- Handle database backups
- Configure Render deployment
- Manage environment variables
- Monitor logs and performance

**Key Files to Handle:**
- `.env` and `.env.example` - Environment config
- `config.py` - Flask configuration
- `Procfile` - Render deployment
- `requirements.txt` - Python packages
- `init_db_postgres.py` - Database initialization

**First Week Goals:**
- Ensure PostgreSQL runs locally for entire team
- Prepare Render account and database

**Timeline:** Week 1, start deployment in Week 3

---

### QA/Testing Team (1-2 people)

**Tasks:**
- Manual testing of all features
- Security testing (SQL injection, XSS, auth bypass)
- Cross-browser testing
- Performance testing
- Create test cases and bug reports

**Test Checklist:**
- [ ] Registration works correctly
- [ ] Login validation works
- [ ] Users can't access admin pages
- [ ] Feedback submission saves to DB
- [ ] Admin can CRUD menu items
- [ ] Admin can CRUD questions
- [ ] Admin can view all feedback
- [ ] Session timeout works
- [ ] All forms validate input
- [ ] API returns proper JSON

**Timeline:** Week 2-3

---

## 📋 Daily Standup Template

Each day, report on:
1. **Yesterday**: What did I complete?
2. **Today**: What will I work on?
3. **Blockers**: What's preventing progress?

Example:
```
Backend - John:
Yesterday: Implemented user registration endpoint
Today: Working on login endpoint and session handling
Blockers: Need clarification on password hashing approach

Frontend - Sarah:
Yesterday: Created login.html template with Bootstrap styling
Today: Implementing JavaScript form submission
Blockers: Waiting for API endpoint to be ready for testing
```

---

## 🔗 GitHub Workflow

### Branching Strategy
```
main (stable)
├── backend-auth (authentication features)
├── backend-api (API endpoints)
├── frontend-ui (UI templates)
└── feature/* (individual features)
```

### Creating a Feature Branch
```bash
git checkout -b feature/your-feature-name
# Make changes
git add .
git commit -m "Description of what you did"
git push origin feature/your-feature-name
```

### Creating a Pull Request
1. Go to GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Add description and screenshots
5. Request review from team
6. Merge once approved

### Pulling Latest Changes
```bash
git checkout main
git pull origin main
git checkout your-branch
git merge main
```

---

## 🚀 Weekly Milestones

### Week 1 (Apr 29 - May 5): Foundation
- [ ] All team members have local setup working
- [ ] Database schema finalized
- [ ] Authentication endpoints complete (register/login)
- [ ] Basic HTML templates created
- [ ] All tests pass

### Week 2 (May 6 - May 12): Core Features
- [ ] User feedback submission working
- [ ] Admin menu item CRUD complete
- [ ] Admin question management complete
- [ ] Admin feedback reports working
- [ ] Frontend integrated with API
- [ ] 80% of functionality working

### Week 3 (May 13 - May 19): Testing & Deployment
- [ ] All 100% features complete
- [ ] Full QA testing done
- [ ] Security testing passed
- [ ] Documentation complete
- [ ] Deployed on Render successfully
- [ ] Final demo ready

---

## 📚 Helpful Resources

### Flask
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)

### Database
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [SQLAlchemy ORM](https://www.sqlalchemy.org/)

### Frontend
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

### Deployment
- [Render Docs](https://render.com/docs)
- [Gunicorn](https://gunicorn.org/)

### Tools
- [Postman API Testing](https://www.postman.com/)
- [Thunder Client VS Code Extension](https://www.thunderclient.io/)
- [PostgreSQL Admin - pgAdmin](https://www.pgadmin.org/)

---

## ❓ Common Questions

**Q: I'm getting "ModuleNotFoundError"**
A: Run `pip install -r requirements.txt` and make sure virtual environment is activated

**Q: PostgreSQL connection refused**
A: Check PostgreSQL is running, and DATABASE_URL is correct in .env

**Q: Port 5000 already in use**
A: Run `python app.py --port 5001` or kill process using port 5000

**Q: I made a mistake, how do I revert?**
```bash
git reset --hard origin/main  # Reset local to main
git checkout your-branch      # Switch to your branch
git merge main               # Merge latest main
```

**Q: How do I sync with team changes?**
```bash
git pull origin main
git merge main  # if on feature branch
```

---

## 🎯 Success Criteria

✅ **Project is successful if:**
- All 8 team members can run locally
- System deployed on Render with working PostgreSQL
- Users can register, login, submit feedback
- Admin can manage menu items and questions
- Code is organized and documented
- Team completes within 3-week timeline

---

**Questions?** Create an issue on GitHub or post in team chat

**Ready?** Let's build something amazing! 🚀

---

Last Updated: April 30, 2026
