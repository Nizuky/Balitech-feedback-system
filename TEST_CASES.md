# Manual Test Cases — Balitech Feedback System

This document lists manual test cases to exercise the main functionality of the application. Each test case includes test data, assumptions, prerequisites, steps, expected result, and space for actual result/status.

---

TC_ID: TC_001
Title: Health endpoint
Description: Verify the `/health` endpoint returns service status
Test Data: n/a
Assumptions: App is running in testing or development mode
Prerequisites: App started (local or test server)
Steps:
1. Send GET request to `/health`
Expected Result: HTTP 200 and JSON `{ "status": "ok" }`
Actual Result:
Status:

---

TC_ID: TC_002
Title: User registration validation
Description: Verify registration rejects missing fields and short passwords
Test Data: several payloads
- Missing username: `{ "email": "a@b.com", "password": "pass" }`
- Short password: `{ "username": "u1", "email": "u1@b.com", "password": "123" }`
Assumptions: DB is empty or isolated test DB
Prerequisites: App running
Steps:
1. POST `/auth/register` with missing username payload
2. POST `/auth/register` with short password payload
Expected Result:
- 400 and message 'All fields required' (or similar) for missing fields
- 400 and message about password length for short password
Actual Result:
Status:

---

TC_ID: TC_003
Title: User registration success and duplicate checks
Description: Register a new user and verify duplicate username/email are rejected
Test Data:
`{ "username": "alice", "email": "alice@example.com", "password": "password123" }`
Assumptions: Clean DB
Prerequisites: App running
Steps:
1. POST `/auth/register` with payload above
2. Repeat POST `/auth/register` with same username
3. Repeat POST `/auth/register` with same email but different username
Expected Result:
1. 201 and success message
2. 400 and message 'Username already exists'
3. 400 and message 'Email already registered'
Actual Result:
Status:

---

TC_ID: TC_004
Title: Login validation and role-based redirect
Description: Verify login requires credentials, rejects invalid credentials, rejects deactivated accounts, and returns redirect URL for role
Test Data:
- Valid user created by registration step
- Deactivated user (set `is_active` false)
Assumptions: User account exists
Prerequisites: App running, valid user in DB
Steps:
1. POST `/auth/login` with empty username/password
2. POST `/auth/login` with wrong credentials
3. POST `/auth/login` with valid credentials
4. For a user with `is_active=False`, POST `/auth/login`
Expected Result:
1. 400 'Username and password required'
2. 401 'Invalid username or password'
3. 200 with JSON `{'status':'success', 'redirect': '<url>'}`
4. 403 'This account is deactivated.'
Actual Result:
Status:

---

TC_ID: TC_005
Title: Logout clears session and redirects to public forms
Description: Verify `/auth/logout` clears session and redirects
Test Data: Logged-in session
Assumptions: User is logged in
Prerequisites: App running, logged in session cookie
Steps:
1. GET `/auth/logout`
Expected Result: HTTP redirect to public forms list; subsequent request to `/feedback/dashboard` requires login
Actual Result:
Status:

---

TC_ID: TC_006
Title: Create, Edit, Toggle, and Delete Form (creator flows)
Description: Verify creators can create forms with questions, edit them, toggle publish, and delete
Test Data:
- Form payload (POST to `/creator/forms/new`):
```
{
  "title": "Survey",
  "description": "Short survey",
  "questions": [
    { "label": "Name", "type": "text", "required": true },
    { "label": "Satisfaction", "type": "multiple_choice", "options": ["Good","Bad"] }
  ],
  "is_published": true
}
```
Assumptions: User is a creator (logged in, `role` in session)
Prerequisites: App running, creator user exists and logged in
Steps:
1. POST to `/creator/forms/new` with payload to create form
2. GET the returned `public_url` and ensure the form loads
3. POST to `/creator/forms/<id>/toggle` to change publish state
4. POST `/creator/forms/<id>/delete` to remove the form
Expected Result:
1. 201 with `form` info and `public_url`
2. GET shows form page (HTTP 200)
3. Toggle returns success and `is_published` toggled
4. Delete returns success and form no longer accessible
Actual Result:
Status:

---

TC_ID: TC_007
Title: Form submission validation and persistence
Description: Submit a published form, verify required field validation and that responses are persisted
Test Data: Use form created in TC_006 (with required `Name`)
Assumptions: Form is published and has at least one required question
Prerequisites: App running, public form available
Steps:
1. POST `/forms/<public_id>/submit` with missing required answer
2. POST `/forms/<public_id>/submit` with all required answers
Expected Result:
1. 400 with message indicating required question
2. 200 (or 201) with success message; response stored in DB (FormResponse and FormAnswer present)
Actual Result:
Status:

---

TC_ID: TC_008
Title: Feedback submission API validation (generic responses)
Description: Verify `/feedback/api/submit_feedback` validates input and persists generic responses/comments for a question/topic
Test Data:
`{ "question_id": <id>, "comment": "This was helpful" }` (or other free-text responses)
Assumptions: User logged in via session
Prerequisites: App running, question exists, logged-in session
Steps:
1. POST endpoint with missing `question_id` or missing body
2. POST with non-existent `question_id`
3. POST with valid payload containing `question_id` and `comment`/response text
Expected Result:
1. 400 'Missing required fields'
2. 404 'Question not found' (or appropriate error)
3. 201 success and response persisted (FormResponse/Feedback row or equivalent)
Actual Result:
Status:

---

TC_ID: TC_009
Title: Topic response counts
Description: Verify `/feedback/api/menu_summaries` returns topics with `response_count` (number of responses per topic)
Test Data: Several response rows for a topic (stored in `MenuItem` or topic table)
Assumptions: Topics exist with associated responses
Prerequisites: App running, topics and responses present
Steps:
1. GET `/feedback/api/menu_summaries`
2. Validate returned `response_count` against DB values
Expected Result: `response_count` integer matching number of response rows
Actual Result:
Status:

---

TC_ID: TC_010
Title: Topic responses API and page
Description: Verify `/feedback/api/menu/<id>/reviews` (responses endpoint) returns recent responses for a topic and `/menu/<id>/reviews` renders aggregated responses per user
Test Data: Multiple response rows by same and different users about the topic
Assumptions: Response rows exist
Prerequisites: App running
Steps:
1. GET `/feedback/api/menu/<id>/reviews?limit=3` and check count <= limit
2. GET `/feedback/menu/<id>/reviews` (page) and visually inspect aggregated results
Expected Result:
1. JSON list of responses up to requested limit (comments/text and timestamps)
2. Page renders and aggregated user entries show representative response text and latest submission time
Actual Result:
Status:

---

TC_ID: TC_011
Title: Error handling for API 404 and general 500
Description: Trigger a 404 on an API route and ensure JSON error; trigger a server error and ensure consistent API JSON error
Test Data: Request non-existent API route `/api/does-not-exist` and simulate server exception in a route
Assumptions: App running
Prerequisites: App running
Steps:
1. GET `/api/does-not-exist`
2. (Dev only) create a test route that raises Exception and call it under `/api/` prefix
Expected Result:
1. 404 with JSON `{ "status": "error", "message": "Resource not found" }`
2. 500 with JSON `{ "status": "error", "message": "Internal server error" }`
Actual Result:
Status:

---

Notes:
- For tests requiring a logged-in user, use the same session cookie mechanism the app uses (set `session['user_id']`, `session['username']`, `session['role']`).
- Consider exporting this document to CSV/Excel for QA tracking; I can add a simple script to convert it if you want.

---

TC_ID: TC_012
Title: Admin login and access control
Description: Verify admin can login and access admin routes; non-admin users are blocked
Test Data: admin and regular user credentials
Assumptions: Admin user exists and has `role='admin'`
Prerequisites: App running, admin account present
Steps:
1. POST `/auth/login` with admin creds
2. Access `/admin/dashboard`
3. Login as regular user and attempt `/admin/dashboard`
Expected Result:
1. Successful login and admin redirect
2. Admin dashboard loads (HTTP 200)
3. Non-admin receives 403 or is redirected to login
Actual Result:
Status:

---

TC_ID: TC_013
Title: Admin manage topics (create/edit/delete)
Description: Verify admin can create, update, and delete topics (menu_items) via admin API
Test Data: Create payload: `{ "item_name": "Topic X", "description": "..." }`
Assumptions: Admin logged in
Prerequisites: App running, admin session
Steps:
1. POST `/admin/api/menu_items` with payload
2. PUT `/admin/api/menu_items/<id>` to update
3. DELETE `/admin/api/menu_items/<id>`
Expected Result:
1. 201 and returned item data
2. 200 and updated fields
3. 200 and item removed (subsequent GET returns 404)
Actual Result:
Status:

---

TC_ID: TC_014
Title: Admin manage questions (create/edit/delete)
Description: Verify admin can CRUD questions tied to topics via admin API
Test Data: Question payload: `{ "question_text": "...", "menu_item_id": <id> }`
Assumptions: Admin logged in
Prerequisites: App running, admin session
Steps:
1. POST `/admin/api/questions`
2. PUT `/admin/api/questions/<id>`
3. DELETE `/admin/api/questions/<id>`
Expected Result:
1. 201 with question data
2. 200 with updates persisted
3. 200 and question removed
Actual Result:
Status:

---

TC_ID: TC_015
Title: Admin view feedback reports
Description: Verify admin can fetch feedback reports and aggregated stats
Test Data: n/a
Assumptions: Admin logged in
Prerequisites: App running, feedback data exists
Steps:
1. GET `/admin/api/feedback_reports`
2. Inspect returned aggregation fields
Expected Result:
200 and JSON with per-topic `response_count`, recent comments, and optionally per-question stats
Actual Result:
Status:

---

TC_ID: TC_016
Title: Admin export responses (CSV)
Description: Verify admin can export responses for a topic/form as CSV
Test Data: n/a
Assumptions: Admin logged in
Prerequisites: App running, data present
Steps:
1. GET `/admin/api/export_responses?menu_item_id=<id>` or `?form_id=<id>`
Expected Result:
200 with Content-Type `text/csv` and attachment filename or JSON link to export
Actual Result:
Status:

---

TC_ID: TC_017
Title: Admin user management (deactivate/reactivate)
Description: Verify admin can deactivate and reactivate user accounts and that deactivated users cannot login
Test Data: User id to manage
Assumptions: Admin logged in
Prerequisites: App running, user exists
Steps:
1. POST `/admin/api/users/<id>/deactivate`
2. Attempt login as that user
3. POST `/admin/api/users/<id>/reactivate`
4. Attempt login again
Expected Result:
1. 200 deactivation success
2. Login rejected/403
3. 200 reactivation success
4. Login succeeds
Actual Result:
Status:
