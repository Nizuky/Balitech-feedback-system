# Render Deployment Guide

Complete step-by-step guide to deploy the Balitech Feedback System on Render with PostgreSQL.

## Prerequisites

- GitHub account with the project repository
- Render account (free tier available)
- Already have `requirements.txt`, `Procfile`, and code pushed to GitHub

## 📋 Option 1: Manual Deployment (Recommended for First Time)

### Step 1: Create a Render Account

1. Go to [render.com](https://render.com)
2. Click "Sign up"
3. Choose "Sign up with GitHub" for easier setup
4. Authorize Render to access your GitHub account

### Step 2: Create PostgreSQL Database

1. In Render dashboard, click **"New +"** button
2. Select **"PostgreSQL"**
3. Fill in the database details:
   - **Name**: `balitech-db` (or your choice)
   - **Database**: `balitech_db` (will be created automatically)
   - **User**: `balitech` (will be auto-generated)
   - **Region**: Select closest to your location
   - **PostgreSQL Version**: 14 or 15 (latest stable)
4. Click **"Create Database"**
5. **Wait for database to be created** (usually 1-2 minutes)
6. Once created, you'll see a page with connection details
7. **Copy the External Database URL** - it looks like:
   ```
   postgresql://balitech:password@your-host.postgres.render.com:5432/balitech_db
   ```
   Keep this safe - you'll need it in Step 5

### Step 3: Create Web Service

1. In Render dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Choose **"Build and deploy from a Git repository"**
4. Click **"Connect"** to connect your GitHub repository
5. Search for and select your Balitech repository
6. Click **"Connect"** again

### Step 4: Configure Web Service

Fill in the service details:

**Basic Settings:**
- **Name**: `balitech-feedback` (or your choice)
- **Environment**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt && python init_db_postgres.py
  ```
- **Start Command**: 
  ```
  gunicorn app:create_app()
  ```

**Advanced Settings (scroll down):**
- **Plan**: Free (or upgrade as needed)
- **Auto-Deploy**: Select "Yes" (redeploy when you push to GitHub)
- **Instance Count**: 1
- **Disk**: 1 GB (free tier)

### Step 5: Set Environment Variables

1. Scroll down to **"Environment"** section
2. Click **"Add Environment Variable"** and add each:

   | Key | Value |
   |-----|-------|
   | `FLASK_ENV` | `production` |
   | `SECRET_KEY` | (Generate a random secret - see note below) |
   | `DATABASE_URL` | (Paste the PostgreSQL URL from Step 2) |

   **To generate SECRET_KEY**, run in your terminal:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Or use any random 32+ character string.

3. Click **"Save"** for each variable

### Step 6: Deploy

1. Click **"Create Web Service"** button
2. Render will start building and deploying
3. You'll see a **"Build in Progress"** message
4. The build takes 2-5 minutes
5. Once complete, you'll see a green checkmark and a URL like:
   ```
   https://balitech-feedback.onrender.com
   ```

### Step 7: Test Your Deployment

1. Click the URL to open your app
2. You should see the login page
3. Use the test credentials:
   - **Admin**: `admin` / `admin123`
   - **User**: `customer1` / `password123`
4. Test all features:
   - Create feedback as user
   - Login as admin
   - Manage menu items
   - Manage questions
   - View reports

## 🚀 Option 2: Blueprint Deployment (Automated One-Click)

This deploys everything automatically in one click.

### Step 1: Push render.yaml to GitHub

Ensure `render.yaml` is in your repository root and pushed to GitHub.

### Step 2: Create Blueprint

1. In Render dashboard, click **"New +"** button
2. Select **"Blueprint"**
3. Choose **"Connect Repository"**
4. Select your GitHub repository
5. Click **"Deploy"**

### Step 3: Wait for Automatic Setup

Render will automatically:
- Create PostgreSQL database
- Create Web service
- Set environment variables
- Initialize database
- Deploy your app

The entire process takes 5-10 minutes.

## 🔧 Configuration Details

### Procfile

The `Procfile` tells Render how to start your app:
```
web: gunicorn app:create_app()
```

This uses the `create_app()` factory function from `app.py`.

### requirements.txt

Render automatically installs all Python packages listed in `requirements.txt`:
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
psycopg2-binary==2.9.7
gunicorn==21.2.0
python-dotenv==1.0.0
```

### Build Command

During deployment, Render runs:
```bash
pip install -r requirements.txt && python init_db_postgres.py
```

This:
1. Installs all Python dependencies
2. Runs the database initialization script
3. Creates tables and inserts seed data

## 🔄 Deploying Updates

After making changes to your code:

### Option A: Automatic (Recommended)
1. Push your changes to GitHub:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin main
   ```
2. Render automatically rebuilds and deploys
3. Check deployment status in Render dashboard

### Option B: Manual Redeploy
1. Go to your Web Service in Render
2. Click **"Manual Deploy"**
3. Select **"Deploy latest commit"**

## 🐛 Troubleshooting

### Deployment Fails with Database Error

**Problem**: Build fails during `python init_db_postgres.py`

**Solution**:
1. Check that PostgreSQL database was created in Step 2
2. Verify DATABASE_URL environment variable is set correctly
3. In Render dashboard, check "Logs" tab for detailed error
4. Manually trigger init script:
   - Click "Manual Deploy"
   - Wait for logs to show initialization success

### App Crashes After Deployment

**Problem**: Deployment succeeds but visiting URL shows error

**Solution**:
1. Check Render logs (click "Logs" tab)
2. Common issues:
   - Missing environment variable
   - DATABASE_URL format incorrect
   - Flask import errors
3. Fix code and push to GitHub (or manually redeploy)

### Database Won't Initialize

**Problem**: `init_db_postgres.py` hangs or fails

**Solution**:
1. Ensure PostgreSQL service is running and accessible
2. Check DATABASE_URL is correct format:
   ```
   postgresql://user:password@host:port/database
   ```
3. Try rebuilding:
   - Click "Manual Deploy" > "Clear Build Cache" (if available)
   - Or delete and recreate service

### Render Free Tier Limitations

- **Web Service**: 0.5 GB RAM, sleeps after 15 min of inactivity
- **PostgreSQL**: 256 MB storage, auto-shutdown after 7 days of inactivity
- **Bandwidth**: 100 GB/month

For production, upgrade to paid plans.

## 📊 Monitoring

### View Logs
1. Click your Web Service
2. Click **"Logs"** tab
3. See real-time logs of requests and errors

### View Database
1. Click your PostgreSQL database
2. Click **"Connect"** tab
3. Use connection details to connect with psql/pgAdmin:
   ```bash
   psql "postgresql://user:password@host:port/database"
   ```

### View Deployments
1. Click **"Deploys"** tab
2. See all deployment history
3. Click any deployment to see logs

## 🔐 Security Best Practices

1. **Change Default Admin Password**
   - Login as `admin` / `admin123`
   - Update password in database (or through app if you add that feature)

2. **Generate Strong SECRET_KEY**
   - Use Python:
     ```bash
     python -c "import secrets; print(secrets.token_hex(32))"
     ```
   - Store in Render environment variables, never in code

3. **Enable HTTPS**
   - Render provides free HTTPS automatically
   - All traffic to `https://` is encrypted

4. **Backup Database**
   - In Render dashboard, go to PostgreSQL details
   - Look for backup/export options
   - Regular backups recommended

5. **Monitor Activity**
   - Check logs regularly
   - Watch for unusual traffic patterns
   - Set up alerts if available

## 📝 Additional Notes

### Environment Variable Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `FLASK_ENV` | Environment mode | `production` or `development` |
| `SECRET_KEY` | Session encryption key | `abc123def456...` |
| `DATABASE_URL` | Database connection | `postgresql://user:pass@host/db` |
| `PORT` | Web server port | `10000` (set by Render) |

### Database Initialization Details

The `init_db_postgres.py` script:
1. Creates all tables (Users, MenuItems, Questions, Feedback)
2. Inserts 5 sample menu items
3. Creates 3 overall experience questions
4. Creates 2 questions per menu item
5. Inserts 2 sample feedback entries
6. Creates admin and test user accounts

### Useful Render Commands

```bash
# View remote logs
render logs <service-id>

# Check service status
curl https://your-app.onrender.com/health

# SSH into service (if enabled)
render shell <service-id>
```

---

**Questions?** Check [Render Docs](https://render.com/docs) or GitHub Issues

**Last Updated**: April 30, 2026
