# Testing and evidence

## Automated tests

| Suite | Command | Evidence |
|---|---|---|
| Backend lint | `cd backend && ruff check .` | [ruff.txt](evidence/ruff.txt) |
| Backend tests (19) | `cd backend && pytest -q` | [pytest.txt](evidence/pytest.txt) |
| Frontend-to-API happy path | `cd frontend && npm run test:e2e` | [playwright.txt](evidence/playwright.txt) |
| CI on pull requests | GitHub Actions | ![CI run](evidence/ci.png) |

## PRD section 12 checklist → tests

| PRD acceptance check | Covered by |
|---|---|
| Register/login/logout work; password never stored in plain text | `test_auth.py` |
| Unauthenticated users cannot read assessments | `test_unauthenticated_requests_are_rejected` |
| A leader cannot access another leader's survey by changing the ID | `test_other_leader_cannot_access_by_changing_id` |
| A submitted invitation cannot submit twice; expired/closed ones are rejected | `test_invitation_can_submit_only_once`, `test_expired_invitation_is_rejected`, `test_closed_survey_rejects_guests` |
| With 0, 1 or 2 guest responses, results never return scores | `test_results_locked_below_three_responses` (parametrised) |
| With 3 responses, averages and gaps match hand calculations | `test_results_match_hand_calculation_and_hide_identities`, `test_matches_hand_calculation` |
| PDF contains only aggregate information | `test_pdf_report_downloads` + shared privacy gate |
| Responsive UI with error/empty/loading states | Manual check (see below) |
| CI passes, CD deploys, README reproducible | CI screenshot, Render deploy history |

### Hand calculation used in the tests

| | Others mean | Self | Gap |
|---|---|---|---|
| Communication | 3.75 | 4.50 | +0.75 |
| Collaboration | 4.00 | 4.00 | 0.00 |
| Accountability | 3.33 | 3.67 | +0.33 |
| Overall | 3.70 | 4.10 | +0.40 |

Focus areas: "Acknowledges mistakes." (2.0) and "Shares important updates on time." (3.0).

## Manual end-to-end check on the live URL

Date: <DD/MM/YYYY>

| Step | Result |
|---|---|
| Register a new account | |
| Create and launch an assessment | |
| Complete the self-assessment | |
| Invite 3 raters and submit from 3 private windows | |
| Results locked before closing, unlocked after | |
| Save 2 commitments | |
| Download PDF; no rater names or emails inside | |
| Phone-size screen (DevTools) | |
