# TODO: Add Phone Number Support to Backend

## Changes Required:

### 1. Update User Model (`models.py`)

- [ ] Add `phone_number` column with `unique=True`
- [ ] Add validation for phone number format

### 2. Update Auth Routes (`routes/auth_routes.py`)

- [ ] Update `register_user()` function to accept and store phone_number
- [ ] Update registration route to include phone_number validation
- [ ] Add check for duplicate phone numbers

### 3. Database Migration

- [ ] Generate and run Alembic migration for the new column

## Status:

- [ ] In Progress
- [ ] Completed
