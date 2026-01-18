# 📋 SafariConnect Backend - README

---

## 🌍 Project Overview

**SafariConnect** is a tourism booking platform for Kenya that connects tourists with accommodation providers (hosts) and transport services (drivers). Users can browse listings, make bookings, and manage their travel experiences all in one place.

---

## 👥 Team Members & Roles

| Member | Role | Responsibilities |
|--------|------|------------------|
| **Member 1** | Authentication & Core Infrastructure | User model, JWT auth, login/register endpoints, extensions setup |
| **Member 2** | Accommodation & Transport Management | CRUD operations for listings, role-based access control |
| **Member 3** | Bookings & Relationships | Booking workflows, many-to-many relationships, booking schemas |

---

## 🛠️ Tech Stack

- **Framework:** Flask
- **API:** Flask-RESTful
- **Database:** SQLite (development) / PostgreSQL (production)
- **ORM:** SQLAlchemy
- **Migrations:** Flask-Migrate (Alembic)
- **Authentication:** Flask-JWT-Extended
- **Password Hashing:** Flask-Bcrypt
- **CORS:** Flask-CORS
- **Environment:** Python 3.8+, Pipenv

---

## 📁 Project Structure

```
safari-connect-backend/
├── app.py                      # Main Flask application & route registration
├── config.py                   # Configuration settings (JWT, CORS, Database)
├── extensions.py               # Flask extensions initialization (db, bcrypt, jwt)
├── models.py                   # SQLAlchemy database models
├── Pipfile                     # Python dependencies
├── Pipfile.lock                # Locked dependency versions
├── README.md                   # Project documentation
├── routes/
│   ├── auth_routes.py          # Authentication endpoints (register, login, me)
│   ├── accommodation_routes.py # Accommodation CRUD operations
│   ├── transport.py            # Transport CRUD operations
│   └── booking_routes.py       # Booking management (accommodation & transport)
└── schemas/
    └── booking_schema.py       # Booking validation schemas
```

---

## 🚀 Setup Instructions

### **1. Clone the Repository**

```bash
git clone https://github.com/moses804/safari-connect-backend.git
cd safari-connect-backend
```

### **2. Install Dependencies**

```bash
# Install Pipenv if you don't have it
pip install pipenv

# Install all project dependencies
pipenv install

# Activate virtual environment
pipenv shell
```

### **3. Set Up Environment Variables**

Create a `.env` file in the root directory:

```bash
touch .env
```

Add the following environment variables:

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///safariconnect.db
```

**Generate secure keys:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### **4. Initialize Database**

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration to database
flask db upgrade
```

### **5. Run the Application**

```bash
python app.py
```

Server will start at: **`http://localhost:5000`**

You should see:
```
* Running on http://127.0.0.1:5000
* Debug mode: on
```

---

## 📡 API Endpoints

### **Base URL:** `http://localhost:5000`

---

### **Authentication Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ No |
| POST | `/auth/login` | Login user (returns JWT) | ❌ No |
| GET | `/auth/me` | Get current user info | ✅ Yes |

---

### **Accommodation Endpoints**

| Method | Endpoint | Description | Auth Required | Role Required |
|--------|----------|-------------|---------------|---------------|
| GET | `/accommodations` | List all accommodations | ❌ No | - |
| GET | `/accommodations/<id>` | Get single accommodation | ❌ No | - |
| POST | `/accommodations` | Create new accommodation | ✅ Yes | Host |
| PATCH | `/accommodations/<id>` | Update accommodation | ✅ Yes | Owner |
| DELETE | `/accommodations/<id>` | Delete accommodation | ✅ Yes | Owner |

---

### **Transport Endpoints**

| Method | Endpoint | Description | Auth Required | Role Required |
|--------|----------|-------------|---------------|---------------|
| GET | `/transports` | List all transports | ❌ No | - |
| GET | `/transports/<id>` | Get single transport | ❌ No | - |
| POST | `/transports` | Create new transport | ✅ Yes | Driver |
| PATCH | `/transports/<id>` | Update transport | ✅ Yes | Owner |
| DELETE | `/transports/<id>` | Delete transport | ✅ Yes | Owner |

---

### **Booking Endpoints**

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/accommodation_bookings` | List accommodation bookings | ✅ Yes |
| GET | `/accommodation_bookings/<id>` | Get single accommodation booking | ✅ Yes |
| POST | `/accommodation_bookings` | Create accommodation booking | ✅ Yes |
| PATCH | `/accommodation_bookings/<id>` | Update booking status | ✅ Yes |
| GET | `/transport_bookings` | List transport bookings | ✅ Yes |
| GET | `/transport_bookings/<id>` | Get single transport booking | ✅ Yes |
| POST | `/transport_bookings` | Create transport booking | ✅ Yes |
| PATCH | `/transport_bookings/<id>` | Update booking status | ✅ Yes |

---

## 🔐 Authentication Guide

### **1. Register a New User**

```bash
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "tourist"
}
```

**Available Roles:**
- `tourist` - Can browse and book accommodations/transports
- `host` - Can create and manage accommodations
- `driver` - Can create and manage transports

**Response:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "role": "tourist",
  "created_at": "2026-01-16T10:30:00"
}
```

---

### **2. Login**

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "role": "tourist"
  }
}
```

---

### **3. Using JWT Token**

Include the JWT token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Example with curl:**
```bash
curl -X POST http://localhost:5000/accommodations \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Safari Paradise Lodge",
    "description": "Luxury safari experience",
    "location": "Maasai Mara",
    "price_per_night": 15000,
    "capacity": 4,
    "available": true
  }'
```

**Example with JavaScript:**
```javascript
const token = localStorage.getItem('access_token');

fetch('http://localhost:5000/accommodations', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'Safari Paradise Lodge',
    description: 'Luxury safari experience',
    location: 'Maasai Mara',
    price_per_night: 15000,
    capacity: 4,
    available: true
  })
});
```

---

## 📦 Database Models

### **User Model**
```python
- id (Integer, Primary Key)
- name (String, Required)
- email (String, Unique, Required)
- password_hash (String, Required)
- role (Enum: tourist/host/driver, Default: tourist)
- created_at (DateTime)
```

**Relationships:**
- One-to-Many with Accommodation (as host)
- One-to-Many with Transport (as driver)
- One-to-Many with AccommodationBooking (as tourist)
- One-to-Many with TransportBooking (as tourist)

---

### **Accommodation Model**
```python
- id (Integer, Primary Key)
- host_id (Foreign Key → User)
- title (String, Required)
- description (String, Required)
- location (String, Required)
- price_per_night (Float, Required)
- capacity (Integer, Required)
- available (Boolean, Default: True)
- created_at (DateTime)
```

**Relationships:**
- Many-to-One with User (host)
- One-to-Many with AccommodationBooking

---

### **Transport Model**
```python
- id (Integer, Primary Key)
- driver_id (Foreign Key → User)
- vehicle_type (String, Required)
- price_per_day (Float, Required)
- total_capacity (Integer, Required)
- available (Boolean, Default: True)
- created_at (DateTime)
```

**Relationships:**
- Many-to-One with User (driver)
- One-to-Many with TransportBooking

---

### **AccommodationBooking Model**
```python
- id (Integer, Primary Key)
- tourist_id (Foreign Key → User)
- accommodation_id (Foreign Key → Accommodation)
- check_in_date (Date, Required)
- check_out_date (Date, Required)
- total_price (Float, Required)
- status (Enum: pending/confirmed/cancelled, Default: pending)
- created_at (DateTime)
```

---

### **TransportBooking Model**
```python
- id (Integer, Primary Key)
- tourist_id (Foreign Key → User)
- transport_id (Foreign Key → Transport)
- travel_date (Date, Required)
- seats_booked (Integer, Required)
- total_price (Float, Required)
- status (Enum: pending/confirmed/cancelled, Default: pending)
- created_at (DateTime)
```

---

## 🧪 Testing with Examples

### **Example 1: Create an Accommodation (Host)**

```bash
# 1. Register as host
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Host",
    "email": "jane@host.com",
    "password": "password123",
    "role": "host"
  }'

# 2. Login
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@host.com",
    "password": "password123"
  }'

# Copy the access_token from response

# 3. Create accommodation
curl -X POST http://localhost:5000/accommodations \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Luxury Safari Lodge",
    "description": "5-star accommodation with amazing views",
    "location": "Maasai Mara",
    "price_per_night": 20000,
    "capacity": 6,
    "available": true
  }'
```

---

### **Example 2: Browse Accommodations (Public)**

```bash
# No authentication needed
curl http://localhost:5000/accommodations
```

**Response:**
```json
[
  {
    "id": 1,
    "title": "Luxury Safari Lodge",
    "description": "5-star accommodation with amazing views",
    "location": "Maasai Mara",
    "price_per_night": 20000.0,
    "capacity": 6,
    "available": true,
    "host_id": 1,
    "created_at": "2026-01-16T10:30:00"
  }
]
```

---

### **Example 3: Create a Booking (Tourist)**

```bash
# 1. Login as tourist
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "tourist@example.com",
    "password": "password123"
  }'

# 2. Book accommodation
curl -X POST http://localhost:5000/accommodation_bookings \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "accommodation_id": 1,
    "check_in_date": "2026-02-01",
    "check_out_date": "2026-02-05",
    "total_price": 80000
  }'
```

---

## 🔄 Git Workflow

### **Branch Strategy**

```
main
├── member-1-auth          (Authentication)
├── member-2-listings      (Accommodations & Transports)
└── member-3-bookings      (Booking system)
```

### **Daily Workflow**

```bash
# 1. Start of day - sync with main
git checkout main
git pull origin main
git checkout your-branch-name
git merge main

# 2. Work on features
# ... make changes ...

# 3. Commit frequently (every 30-60 min)
git add .
git commit -m "Descriptive commit message"

# 4. Push to GitHub
git push origin your-branch-name

# 5. Create Pull Request when feature complete
```

### **Commit Message Guidelines**

**Good:**
- ✅ `Add JWT authentication to accommodation routes`
- ✅ `Fix transport creation validation error`
- ✅ `Update accommodation model to include amenities`

**Bad:**
- ❌ `stuff`
- ❌ `changes`
- ❌ `fix`

---

## 🚨 Common Issues & Solutions

### **Issue 1: ModuleNotFoundError**

```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Make sure you're in Pipenv shell
pipenv shell
python app.py
```

---

### **Issue 2: Port Already in Use**

```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Run app again
python app.py
```

---

### **Issue 3: JWT Token Errors**

```
{"msg": "Missing Authorization Header"}
```

**Solution:**
- Make sure you're including the token in headers
- Format: `Authorization: Bearer YOUR_TOKEN`
- Token must be obtained from `/auth/login`

---

### **Issue 4: Role Permission Denied**

```
{"message": "Only hosts can create accommodations"}
```

**Solution:**
- Check user role matches requirement
- Hosts create accommodations
- Drivers create transports
- Tourists create bookings

---

### **Issue 5: Database Migration Errors**

```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
```bash
# Reset migrations
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 🌐 Frontend Integration

### **CORS Configuration**

The backend is configured to accept requests from:
- `http://localhost:3000` (React default)
- `http://localhost:5173` (Vite default)

To add more origins, update `config.py`:
```python
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173", "your-frontend-url"]
```

---

### **Frontend Example (React)**

```javascript
// Login function
const login = async (email, password) => {
  const response = await fetch('http://localhost:5000/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};

// Fetch accommodations (public)
const getAccommodations = async () => {
  const response = await fetch('http://localhost:5000/accommodations');
  return await response.json();
};

// Create accommodation (authenticated)
const createAccommodation = async (accommodationData) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:5000/accommodations', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(accommodationData)
  });
  
  return await response.json();
};
```

---

## 📝 Development Guidelines

### **Code Style**

- Follow PEP 8 for Python code
- Use descriptive variable names
- Add comments for complex logic
- Keep functions small and focused

### **Security Best Practices**

- ✅ Never commit `.env` file
- ✅ Use strong JWT secrets
- ✅ Hash all passwords with bcrypt
- ✅ Validate all user input
- ✅ Use HTTPS in production

### **Testing Checklist**

Before pushing code:
- [ ] All endpoints return expected responses
- [ ] JWT authentication works correctly
- [ ] Role-based access control enforced
- [ ] Database operations succeed
- [ ] No syntax errors or warnings
- [ ] Code follows team conventions

---

## 🎯 Member 2 Contribution

**Responsibilities Completed:**
- ✅ Accommodation CRUD routes (`routes/accommodation_routes.py`)
- ✅ Transport CRUD routes (`routes/transport.py`)
- ✅ JWT authentication integration
- ✅ Role-based access control (Host/Driver restrictions)
- ✅ Ownership validation (users can only edit their own listings)
- ✅ Request validation with RequestParser
- ✅ Public browsing (GET endpoints require no auth)
- ✅ Integration with team's models and extensions

---

## 📞 Support

For questions or issues:
1. Check this README first
2. Review common issues section
3. Ask in team chat
4. Create GitHub issue if bug found

---

## 👨‍💻 Team

- **Member 1 (Stanley)** - Authentication & Infrastructure
- **Member 2 (Andrew)** - Accommodation & Transport Management
- **Member 3 ** - Bookings & Relationships

**Institution:** Moringa School  
**Project:** Phase 4 Backend Development  
**Last Updated:** January 16, 2026

---

## 📄 License

This project is for educational purposes as part of Moringa School's curriculum.

---
