# Multi-Tenancy Implementation Roadmap

## Quick Reference Checklist

### ✅ Phase 0: Foundation (COMPLETED)
- [x] Architecture design (`MULTI_TENANCY_ARCHITECTURE.md`)
- [x] Implementation guide (`MULTI_TENANCY_IMPLEMENTATION.md`)  
- [x] Database models updated
- [x] Data migration script created
- [x] Summary documentation

### 🔄 Phase 1: Database Migration (CURRENT PHASE)

#### Step 1.1: Generate Migration
```bash
flask db migrate -m "Add multi-tenancy support"
```

**Review Checklist:**
- [ ] Club table created with all columns
- [ ] ClubMembership table created with unique constraint
- [ ] club_id columns added to all models (nullable at first)
- [ ] Indexes created on all club_id columns
- [ ] Foreign key constraints added
- [ ] Unique constraints updated (category name per club, etc.)

#### Step 1.2: Apply Migration
```bash
flask db upgrade
```

**Verification:**
- [ ] No errors during migration
- [ ] All tables created successfully
- [ ] Constraints applied correctly

#### Step 1.3: Run Data Migration
```bash
python migrate_to_multitenancy.py
```

**Verification:**
- [ ] Default club created
- [ ] All users migrated to ClubMembership
- [ ] All inventory categories have club_id
- [ ] All inventory items have club_id
- [ ] All events have club_id
- [ ] All competitions have club_id
- [ ] All beginners students have club_id

#### Step 1.4: Make club_id NOT NULL
Create a follow-up migration:
```bash
flask db migrate -m "Make club_id NOT NULL"
```

Update migration to make club_id NOT NULL now that all data has values.

**Completion Criteria:** ✅ All data migrated, constraints in place, tests pass

---

### 📋 Phase 2: Core Infrastructure

#### Step 2.1: Club Utilities
File: `app/club_utils.py`

- [ ] `get_current_club()` function
- [ ] `get_current_membership()` function
- [ ] `require_club_context()` decorator
- [ ] `require_club_admin()` decorator
- [ ] `club_query()` helper function

#### Step 2.2: Application Middleware
File: `app/__init__.py`

- [ ] Add `before_request` handler for club context
- [ ] Add `context_processor` for templates
- [ ] Import club utilities
- [ ] Register new blueprints

**Completion Criteria:** ✅ Club context available in all requests

---

### 🔐 Phase 3: Authentication Updates

#### Step 3.1: Update Login Flow
File: `app/auth/__init__.py`

- [ ] Update `login()` to handle club selection
- [ ] Create `select_club()` view
- [ ] Create `switch_club()` view
- [ ] Update `logout()` to clear club session

#### Step 3.2: Create Templates
Files: `app/templates/auth/`

- [ ] `select_club.html` - Club selection page
- [ ] Update `login.html` if needed

#### Step 3.3: Update Forms
File: `app/forms.py`

- [ ] Create `ClubSelectionForm` if needed

**Completion Criteria:** ✅ Users can log in and select clubs

---

### 🏢 Phase 4: Club Registration

#### Step 4.1: Create Club Blueprint
File: `app/clubs/__init__.py`

- [ ] Create blueprint
- [ ] Create `register()` view
- [ ] Create `settings()` view for club admins

#### Step 4.2: Create Club Forms
File: `app/forms.py`

- [ ] `ClubRegistrationForm`
  - club_name
  - description
  - email
  - admin_username
  - admin_email
  - admin_password
  - admin_first_name
  - admin_last_name

#### Step 4.3: Create Templates
Files: `app/templates/clubs/`

- [ ] `register.html` - Club registration form
- [ ] `settings.html` - Club settings (replaces old settings)

#### Step 4.4: Update Main Routes
File: `app/main/__init__.py`

- [ ] Update landing page to show "Register Club" option
- [ ] Update index route

**Completion Criteria:** ✅ New clubs can register via web interface

---

### 🔄 Phase 5: Update Existing Views

#### Step 5.1: Inventory Blueprint
File: `app/inventory/__init__.py`

- [ ] Replace `admin_required` with `require_club_admin`
- [ ] Update all queries to use `club_query()` or filter by `g.current_club.id`
- [ ] Set `club_id` when creating new items/categories
- [ ] Update category uniqueness checks (per club)

#### Step 5.2: Events Blueprint
File: `app/events/__init__.py`

- [ ] Replace `admin_required` with `require_club_admin`
- [ ] Update all queries to filter by club
- [ ] Set `club_id` when creating new events

#### Step 5.3: Members Blueprint
File: `app/members/__init__.py`

- [ ] Update to show ClubMembership instead of User directly
- [ ] Update role checks to use `is_admin_of_club()`
- [ ] Filter members by current club
- [ ] Update member creation to create ClubMembership

#### Step 5.4: Competitions Blueprint
File: `app/competitions/__init__.py`

- [ ] Replace `admin_required` with `require_club_admin`
- [ ] Update all queries to filter by club
- [ ] Set `club_id` when creating competitions

#### Step 5.5: Main Blueprint
File: `app/main/__init__.py`

- [ ] Update dashboard to show club-specific stats
- [ ] Update settings to use Club model instead of ClubSettings

**Completion Criteria:** ✅ All views work with club context

---

### 🎨 Phase 6: Template Updates

#### Step 6.1: Base Template
File: `app/templates/base.html`

- [ ] Add club name display
- [ ] Add club switcher dropdown (if user has multiple clubs)
- [ ] Update navigation to include club context
- [ ] Add club logo/branding area

#### Step 6.2: Dashboard Template
File: `app/templates/dashboard.html`

- [ ] Show club name prominently
- [ ] Update statistics to be club-specific
- [ ] Add club admin quick links

#### Step 6.3: Update All Other Templates
- [ ] Ensure club context is visible where relevant
- [ ] Update titles to include club name
- [ ] Update breadcrumbs

**Completion Criteria:** ✅ UI reflects current club throughout

---

### 🧪 Phase 7: Testing

#### Step 7.1: Update Unit Tests
Files: `tests/test_models_*.py`

- [ ] Update all tests to create clubs
- [ ] Test club isolation
- [ ] Test ClubMembership relationships
- [ ] Test User club methods

#### Step 7.2: Update Integration Tests
Files: `tests/test_routes*.py`

- [ ] Update all tests to set club context
- [ ] Test club switching
- [ ] Test unauthorized club access
- [ ] Test club registration flow

#### Step 7.3: Add New Tests
- [ ] Test club isolation (can't see other club's data)
- [ ] Test multi-club user scenarios
- [ ] Test club admin permissions

**Completion Criteria:** ✅ All tests pass, >80% coverage maintained

---

### 📦 Phase 8: Final Steps

#### Step 8.1: Documentation
- [ ] Update README.md
- [ ] Update API documentation
- [ ] Create user guide for multi-tenancy
- [ ] Create admin guide for club management

#### Step 8.2: Deployment Preparation
- [ ] Test migration on staging database
- [ ] Create rollback plan
- [ ] Prepare deployment checklist
- [ ] Communication plan for existing users

#### Step 8.3: Production Deployment
- [ ] Backup production database ⚠️
- [ ] Run migration on production
- [ ] Run data migration
- [ ] Verify all clubs working
- [ ] Monitor for issues

**Completion Criteria:** ✅ Production deployment successful

---

## Future Features (Post-MVP)

### Open Invite Events
- [ ] Add `is_open_invite` field to ShootingEvent
- [ ] Add `attending_as_club_id` to EventAttendance
- [ ] Create global events board
- [ ] Update event views to show/hide based on open invite

### Global Events Board
- [ ] Create `/events/global` route
- [ ] Filter to show only open invite events
- [ ] Allow cross-club registration
- [ ] Track which club user is attending as

### Community Board
- [ ] Create CommunityPost model
- [ ] Create `/community` route
- [ ] Implement posting, reactions, voting
- [ ] Add club badges to posts

---

## Progress Tracking

**Current Status**: Phase 0 Complete, Starting Phase 1

**Estimated Timeline**:
- Phase 1: 1-2 hours (database migration)
- Phase 2-3: 2-3 hours (infrastructure + auth)
- Phase 4: 2-3 hours (club registration)
- Phase 5: 4-6 hours (update all views)
- Phase 6: 2-3 hours (templates)
- Phase 7: 4-6 hours (testing)
- Phase 8: 2-4 hours (docs + deployment)

**Total Estimate**: 17-27 hours of development work

---

## Getting Help

If you encounter issues:
1. Check `MULTI_TENANCY_ARCHITECTURE.md` for design decisions
2. Check `MULTI_TENANCY_IMPLEMENTATION.md` for detailed code examples
3. Check `MULTI_TENANCY_SUMMARY.md` for overview
4. Review existing tests for patterns

---

**Last Updated**: November 16, 2025
**Branch**: multi-tenancy
