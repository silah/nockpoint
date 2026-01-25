# Nockpoint Manual QA Test Plan

This document contains step-by-step, human-executable test cases to validate the main features of the Nockpoint Archery Club Management application.

Scope: web UI, RBAC, common workflows (auth, members, inventory, events, payments), competitions and winner tracking, Pro member dashboard, and club settings. Includes basic non-functional checks (navigation, responsiveness, accessibility hints).

Note: Prefer testing in a fresh dev database to avoid data contamination between scenarios.

---

## 0) Test Environment & Prerequisites

- Application running locally on: http://127.0.0.1:5000/
- Database initialized with migrations applied and at least one Admin account.
- Browsers: Chrome (latest), Firefox (latest). Mobile view via dev tools.

Test accounts (example)
- Admin: username: admin, password: adminpass
- Member: username: member1, password: memberpass

If you don’t have these accounts, register new users and set admin on one via the app (or the DB).

Pass criteria for each test: Expected result(s) match, no unhandled exceptions (no 500 pages), UI messages are clear.

---

## 1) Global Navigation & RBAC

1.1 Authenticated Navigation (Member)
- Preconditions: Logged in as Member.
- Steps: Open top navbar; check links: Dashboard, Inventory, Inventory > Categories, Members, Events (Calendar, My Charges).
- Expected: Member sees Dashboard, Inventory, Categories, Members, Events. In user dropdown, sees “My Profile”, “Logout”. No admin-only links should be visible (no Create Event, Manage Payments, no Club Management) unless the member is admin.

1.2 Authenticated Navigation (Admin)
- Preconditions: Logged in as Admin.
- Steps: Open Events dropdown.
- Expected: Admin sees Create Event, Manage Payments entries in Events dropdown; In user dropdown, sees an Admin badge and “Club Management” link (Settings).

1.3 Access Control
- Steps: While logged out, try navigating directly to /dashboard, /members/, /inventory/, /events/.
- Expected: Redirect to Login.
- Steps: Logged in as Member, try to reach admin-only endpoints (e.g., /events/new, /members/new, Settings pages).
- Expected: Access denied (flash message or redirect); no admin-only forms visible.

---

## 2) Authentication

2.1 Register New User
- Steps: Go to Auth > Register; enter valid details.
- Expected: Success flash; redirected to dashboard or login; new user exists; password rules enforced; duplicate username/email rejected with validation messages.

2.2 Login / Logout
- Steps: Login with valid creds; verify dashboard loads. Logout; verify redirected to homepage.
- Negative: Bad password or unknown user shows friendly error; stays on login.

2.3 Profile Edit
- Steps: Members > My Profile; update email/fields; save.
- Expected: Changes persisted; flash success; validations enforced.

2.4 Registration Activation Code (Club setting)
- Preconditions: As Admin, set a non-empty Activation Code in Club Management > Edit Settings and save.
- Steps: Log out. Open Auth > Register.
  - Verify an Activation Code field is visible on the form.
  - Submit valid user details WITHOUT entering the activation code.
  - Expected: Registration is blocked with a friendly error indicating the activation code is required.
  - Enter an incorrect activation code and resubmit.
  - Expected: Registration is blocked with an invalid code message.
  - Enter the correct activation code and resubmit.
  - Expected: Registration succeeds and you are redirected to Login with a success flash.
  - Cleanup: Optionally delete the test user afterwards.
 - Toggle: Remove/clear the Activation Code in settings and revisit Register.
   - Expected: Activation Code field is hidden and registration works without a code.

---

## 3) Club Settings (Admin-only)

3.1 View Club Settings
- Preconditions: Logged in as Admin.
- Steps: Open user dropdown > Club Management.
- Expected: Settings overview page shows current configured values (club name, URLs, contact, pricing, pro toggle status).

3.2 Edit Club Settings
- Steps: Click “Edit Settings”; update fields (e.g., Club Name, default location, website, pricing, activation code, toggle pro enabled).
- Expected: Save succeeds; redirected back to settings page; new values displayed; flash “updated successfully”.

3.3 Pro Toggle Impact (see also Member Dashboard section)
- Steps: Toggle Pro on/off and save.
- Expected: Member dashboard pro-only sections appear when Pro enabled; hidden when disabled (see section 8).

---

## 4) Inventory Management

4.1 Create Category (Admin-only)
- Preconditions: Admin.
- Steps: Inventory > Categories > New; fill name/description; save.
- Expected: Category listed; duplicate name rules (if any) enforced.

4.2 Create Item (Admin-only)
- Steps: Inventory > New Item; fill fields incl. category, quantity, unit, condition; save.
- Expected: Item appears in inventory list and view page; fields accurate.

4.3 Edit Item (Admin-only)
- Steps: From item view > Edit; change fields; save.
- Expected: Changes persist; view page shows updates.

4.4 Delete Item (Admin-only)
- Steps: From item view > Delete; confirm.
- Expected: Item removed from list; no stale references.

4.5 Search/Filter (if present on list)
- Steps: Use any search/filter controls on inventory index.
- Expected: List updates accordingly.

---

## 5) Member Management

5.1 List Members
- Preconditions: Logged in.
- Steps: Members > Index; observe member list.
- Expected: Members displayed with key info; pagination if applicable.

5.2 Create Member (Admin-only)
- Steps: Members > New; fill fields; save.
- Expected: New member visible; validation enforced; admin checkbox works.

5.3 Edit Member (Admin-only)
- Steps: Open a member > Edit; change fields; save.
- Expected: Updates persist; role/active flags reflect correctly.

5.4 Toggle Active / Delete (Admin-only)
- Steps: Use available actions; confirm deactivation or delete.
- Expected: Member no longer appears in active lists; cannot log in if deactivated.

5.5 Member Profile (Self)
- Steps: Logged in member > My Profile; edit allowed fields; save.
- Expected: Personal updates persist.

---

## 6) Events, Attendance, and Payments

6.1 Create Event (Admin-only)
- Steps: Events > Create Event; fill name, location, date/time, price, max participants (optional); save.
- Expected: Event appears on calendar and view page; capacity and pricing shown.

6.2 Manage Attendance (Admin-only)
- Steps: From event view > Manage Attendance; add a member; optionally mark attended.
- Expected: Attendance records show; counts updated.

6.3 Member Registration (if allowed by design)
- Steps: As a Member, register for an event if UI allows.
- Expected: Event shows under member’s upcoming events; capacity reflects registration.

6.4 Payments – Outstanding & Mark Paid (Admin)
- Steps: Events > Manage Payments; verify list of outstanding charges; mark one as paid; add payment notes.
- Expected: Charge status flips to Paid; Paid Date/Notes appear; disappears from Outstanding tab if filtered.

6.5 My Charges (Member)
- Steps: Events > My Charges; view summary totals (Outstanding Balance, Total Paid, Total Charges); filter list by All/Outstanding/Paid.
- Expected: Totals accurate; Paid vs Outstanding rows styled and dated correctly; no errors like undefined variables.
- Edge: If no charges, empty state message and link to calendar visible.

---

## 7) Competitions (if enabled in this branch)

7.1 Create Competition for an Event (Admin)
- Steps: From competitions index or event actions, create a competition; set rounds, arrows per round, target size, max team size.
- Expected: Competition created and tied to event; status starts at setup or registration_open per UI.

7.2 Setup Groups/Teams (Admin)
- Steps: Open competition > Setup Groups; create groups; generate teams/targets.
- Expected: Groups and teams listed; counts correct.

7.3 Registration
- Steps: As a member, register; as admin, optionally register members.
- Expected: Registrations appear in competition participants; capacity reflects.

7.4 Scoring (Admin)
- Steps: Open Manage Scoring; enter arrow scores for selected registration across rounds; save.
- Expected: Totals update; round breakdowns correct.

7.5 Complete Competition & Winner Determination (Admin)
- Steps: Click Complete Competition; confirm.
- Expected: Missing arrows auto-filled as 0; status becomes completed; overall winner set to the registration with the highest total score; completion date recorded.
- Verify: Results page shows final standings; on the competition record, winner and score set.

7.6 Member Dashboard Wins (Pro)
- Steps: If the winning user is within last 6 months, check their Pro Dashboard (see next section) and confirm “Recent Competition Victories” shows the win card with points and link to results.

---

## 8) Member Dashboard (Pro Feature)

8.1 Pro Disabled
- Preconditions: Club settings Pro disabled.
- Steps: Visit dashboard as member.
- Expected: Basic dashboard shown; no pro-only sections (e.g., recent activity cards/pro badges/wins section hidden); any upsell banner (if present) displays.

8.2 Pro Enabled
- Preconditions: Club settings Pro enabled.
- Steps: Visit dashboard as member.
- Expected: Pro dashboard shows:
  - My Upcoming Events (if any)
  - Recent Activity (last ~90 days attendance)
  - Available Events
  - Competition Victories (wins within last 6 months) shown prominently if any
- Admin Preview: If feature allows admin preview, confirm badge/banner indicates preview mode.

---

## 9) API Smoke Checks (Optional)

9.1 Competitions API
- Steps: Obtain an API token (if API auth is configured) and GET /api/competitions and /api/competitions/<id>.
- Expected: 200 OK; JSON contains expected fields (name, dates, location, status, user_registered flags).

9.2 Submit Scores (if used by mobile/scoring client)
- Steps: POST /api/competitions/<id>/scores with sample payload for a registered user.
- Expected: 200 OK; scores persisted; reflected in UI totals.

---

## 10) Non-Functional Checks

10.1 Responsiveness
- Steps: Resize viewport (desktop, tablet, mobile); also test in device toolbar.
- Expected: Nav collapses to burger; cards/tables remain readable; no horizontal scroll on primary pages.

10.2 Accessibility (quick sweep)
- Steps: Navigate via keyboard (Tab/Shift+Tab); check visible focus.
- Expected: Focus outline present; forms labeled; no inaccessible color contrasts where critical.

10.3 Error Handling
- Steps: Trigger invalid forms (missing required, bad email format, negative prices).
- Expected: Friendly validation messages; no 500 errors.

10.4 Security
- Steps: Attempt to access admin routes as Member or logged out.
- Expected: Access is denied with redirect/flash; no sensitive data leaked.

---

## 11) Regression Checks

11.1 My Charges Template Variables
- Steps: Load /events/my-charges for a user with paid and outstanding charges.
- Expected: Uses is_paid, charge_date, paid_date; shows accurate totals; no undefined variables.

11.2 Admin Menu
- Steps: As Admin, open user dropdown.
- Expected: “Club Management” is visible and links to Settings overview. As Member, this link is hidden.

11.3 Competition Completion Path
- Steps: Complete a competition with at least one registration having scores.
- Expected: Winner fields populate; results page consistent.

---

## 12) Data Cleanup (optional)

- Delete test events, inventory items, members that were created for testing (if safe).
- Revert club settings to original values (note initial Club Name etc.).

---

## Known Caveats / Tips

- If editor/IDE reports unresolved imports, ensure it’s pointing to the project virtual environment; this doesn’t affect runtime.
- If you encounter a 500 page, check terminal logs for stack traces—report the exact route, steps taken, and error lines.
