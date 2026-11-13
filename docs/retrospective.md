# Retrospective

## 3 decisions made

### 1. Design the ER diagram and the user flow before writing code
- **Decision:** Before building, I drew the ER diagram and walked through the full flow: the leader registers, creates and launches an assessment, rates themselves and invites raters; raters submit through one-time links; results unlock; the leader saves commitments and downloads a PDF.
- **Why:** The tables, the API endpoints and the privacy rules all depend on how the data is related. Getting that right first gave every module a clear starting point.
- **Trade-off / what changed:** The diagram was not final. Checking it against the PRD while building showed missing fields: `closes_at` (scheduled close), `expires_at` for invitations, `due_date` and `status` for commitments, plus unique and check constraints. These changes are recorded in `docs/er-diagram.md`.
- **What I learned:** Writing the SQLAlchemy models was mostly translating the diagram, so the database module went quickly and the relationships were right first time. A design diagram is a starting point, not a contract: comparing it with the requirements while building is what exposed the missing fields.

### 2. Split the whole project into small modules and steps
- **Decision:** I broke the work into modules (setup, database, auth, assessments, invitations, scoring, frontend, Docker, tests, deployment) and each module into small steps, with a check at the end of every step before moving on.
- **Why:** So I always had a clear picture of what was happening and why, instead of writing a lot of code and debugging everything at once.
- **Trade-off:** Slower at the start and many small commits, but problems showed up close to where they were caused.
- **What I learned:** When the first database connection failed in Module 1, only one thing had changed, so the cause (Postgres had kept the password from when its volume was first created) was quick to find. If I had built three modules before testing, the same error would have looked like a problem anywhere in the backend.

### 3. Hash passwords with Argon2
- **Decision:** Store only an Argon2 (`argon2id`) hash of each password, never the password itself.
- **Why:** Argon2 is deliberately slow and memory-hard, so even if the database leaked, guessing passwords from the hashes would be very expensive. The PRD recommends it, and I kept it after understanding why.
- **My additions:** Emails are lowercased before saving; the API never returns `password_hash`; a failed login always returns the same message and verifies against a dummy hash when the email does not exist, so an attacker cannot tell which emails are registered. A test checks that the stored value starts with `$argon2id$`.
- **Trade-off:** Each login takes a little longer, and the app needs an extra library.
- **What I learned:** Passwords are short and chosen by people, so they can be guessed; a slow hash makes every guess expensive. Invitation tokens are 256-bit random values that cannot be guessed, and the app must look them up by their hash, so a fast SHA-256 hash is the right choice there. The type of secret decides the type of hash.

## 2 mistakes corrected

### 1. Frontend could not read the backend's response (CORS)
- **What happened:** After setting up both apps, the React page (`http://localhost:5173`) called the backend's `/health` (`http://127.0.0.1:8001`). It worked with `curl`, but the page showed an error and the browser console showed a CORS error.
- **How I found the cause:** The backend log showed the request arrived and was answered, so the server was fine. The browser was blocking the page from reading the response, because the frontend and backend were on different origins (different host and port).
- **Fix:** Added FastAPI's `CORSMiddleware` with the exact frontend origins (`http://localhost:5173` and `http://127.0.0.1:5173`), not a wildcard. Later the origins moved to `.env`, credentials were allowed for the login cookie, and in production the frontend and API were served from one origin (`/api`), which removed the cross-origin problem entirely.
- **What I learned:** CORS is enforced by the browser, not by the server: the server only says which origins may read its responses, which is why `curl` worked. A wildcard would let any website read responses on behalf of a logged-in user, and browsers do not allow it with cookies anyway, so the origins must be listed exactly.

### 2. PDF download returned 404 — caught by automated tests
- **What happened:** When I added the backend test suite, 15 tests passed and 4 failed. All four called `/assessments/{id}/report.pdf` and got **404**, while `/assessments/{id}/results` for the same assessment and the same leader worked as expected.
- **How I found the cause:** The pattern ruled out the data and the ownership check: if the assessment were missing or belonged to someone else, `/results` would have failed too. So the problem had to be the PDF route itself. Checking `main.py` showed the PDF router was not included, so FastAPI did not know the endpoint existed.
- **Fix:** Registered the router in `main.py`, re-ran the suite (19 passed) and rebuilt the Docker image. CI now runs these tests on every pull request, so a missing route cannot reach `main` again.
- **What I learned:** The PDF button only appears after a survey has closed with at least three responses, so clicking around the app might not have revealed this for days; the tests found it in seconds. Comparing two requests that differ in only one thing is a fast way to isolate a cause.

<!--
Other real mistakes from this project:
- The virtual environment was not active, so conda's pip overwrote requirements.txt; restored with git checkout.
- A downloaded report.pdf would not open: it was a JSON 'results_locked' error, because the test assessment had fewer than 3 responses (the privacy gate worked).
- First Render deploy timed out: the app waited about 10 minutes for the newly created database before migrations ran (found by reading log timestamps).
- FRONTEND_URL was left as a placeholder on Render, so invite links pointed to example.com.
-->

## 1 thing to improve next time

**Send invitation emails automatically instead of only showing links to copy.**

- **Now:** When the leader enters the raters' emails, the app shows one link per rater, and the leader has to copy each link and send it themselves. The PRD allows this as a fallback (FR-03), but it is a manual step: the links are shown only once, so if the leader refreshes the page before copying them, they are lost and new invitations are needed.
- **Improvement:** When the leader clicks "Create invitation links", the backend sends each rater an email with their personal link through an email service, and the copy-link option stays as a fallback. A single reminder before the closing date would follow (a PRD stretch goal).
- **What I would need to handle:**
  - Send the email at the moment the invitation is created, because only the hash of the token is stored afterwards. A reminder cannot reuse the old link; it would need a new token.
  - Send emails in the background, so the leader does not wait for the email service, and record whether each email was sent or failed.
  - Keep the email-service API key in environment variables only, and never write tokens or full links to the logs.
  - Set up the sending domain correctly (SPF/DKIM) so invitations do not end up in spam.
