# CSV Member Import Feature

## Overview

Club administrators can now bulk import members from CSV files. This feature automatically creates user accounts, generates secure passwords, and adds members to the club.

## Features

✅ **Bulk Import**: Import multiple members at once from a CSV file  
✅ **Email as Username**: Automatically uses email addresses as usernames  
✅ **Random Password Generation**: Creates secure 12-character passwords  
✅ **One-Time Password Display**: Shows generated passwords only once for security  
✅ **Existing User Handling**: Adds existing users to the club without creating duplicates  
✅ **CSV Template Download**: Pre-formatted template with examples  
✅ **Import Results Export**: Download imported member credentials as CSV  
✅ **Flexible Options**: Set membership type and admin status for all imports  

## How to Use

### For Administrators

1. **Access the Feature**
   - Go to Members page
   - Click the dropdown arrow next to "Add New Member"
   - Select "Import from CSV"

2. **Download Template**
   - Click "Download CSV Template" to get a pre-formatted file
   - Template includes example rows

3. **Prepare Your CSV**
   - Fill in member information:
     - `email` - Member's email address (required, will be used as username)
     - `first_name` - Member's first name (required)
     - `last_name` - Member's last name (required)
   - Save as CSV file

4. **Import Members**
   - Upload your completed CSV file
   - Select default membership type (monthly, quarterly, annual, per_event)
   - Optionally check "Make all imported users administrators"
   - Click "Import Members"

5. **Save Passwords**
   - **IMPORTANT**: Passwords are shown only once!
   - Download the results as CSV for your records
   - Or print the page for distribution
   - Copy individual passwords using the copy button

### CSV Format

**Required columns:**
```csv
email,first_name,last_name
john.doe@example.com,John,Doe
jane.smith@example.com,Jane,Smith
```

**Example file:** See `example_member_import.csv` in the project root

## Technical Details

### Password Generation
- 12 characters long
- Mix of uppercase, lowercase, digits, and special characters (@#$%&*)
- Cryptographically secure using Python's `secrets` module
- Guaranteed to contain at least one of each character type

### Existing User Handling
- If email already exists in the system:
  - User is added to your club (ClubMembership created)
  - No new password is generated
  - Marked as "Existing User" in results
  
- If email doesn't exist:
  - New User account created
  - Random password generated
  - ClubMembership created
  - Marked as "New User" in results

### Error Handling
- Validates CSV headers before processing
- Skips empty rows
- Reports errors for rows with missing required fields
- Prevents duplicate club memberships
- Rolls back entire import if database error occurs

## Routes

- **`/members/import-csv`** (GET, POST) - Upload and process CSV file
- **`/members/download-template`** (GET) - Download CSV template

## Security

- ✅ Admin-only access (`@require_club_admin`)
- ✅ Club-scoped (users added to current club only)
- ✅ Secure password generation
- ✅ Passwords displayed only once
- ✅ CSRF protection on upload
- ✅ File type validation (CSV only)

## Files Modified/Created

**New Files:**
- `app/templates/members/import_csv.html` - Import form page
- `app/templates/members/import_results.html` - Results display with passwords
- `example_member_import.csv` - Example CSV file

**Modified Files:**
- `app/members/__init__.py` - Added import routes and password generation
- `app/forms.py` - Added `CSVImportForm` with file upload
- `app/templates/members/index.html` - Added import options to dropdown

## Usage Example

1. Admin downloads template from Members page
2. Fills in team members:
   ```csv
   email,first_name,last_name
   coach@archeryclub.com,Sarah,Coach
   member1@gmail.com,Tom,Archer
   member2@yahoo.com,Lisa,Bowman
   ```
3. Uploads CSV, selects "Annual" membership type
4. Reviews results showing:
   - coach@archeryclub.com: Password `A7b#x2M9k@Lp` (New User)
   - member1@gmail.com: Password `K2m$P8w#N5vQ` (New User)
   - member2@yahoo.com: Password `R9t&V3h@X7cD` (New User)
5. Downloads CSV of credentials and emails to members

## Tips for Admins

- ✅ Always download or save the password list immediately
- ✅ Encourage members to change passwords on first login
- ✅ Use the template to ensure proper formatting
- ✅ Test with a small file first
- ✅ Keep imported password records secure
- ✅ Inform members that their username is their email address

## Future Enhancements (Optional)

- Email passwords directly to members
- Bulk user update (not just import)
- Import additional fields (phone, address, membership expiry)
- Schedule automated imports
- Import validation preview before commit
