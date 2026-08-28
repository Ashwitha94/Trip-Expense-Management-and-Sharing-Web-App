# Trip Expense Management and Sharing Web App

A production-ready, full-stack B.Tech level web application for managing trips, logging shared group expenses, dynamically splitting costs, calculating individual member balances, and generating simplified debt settlements with interactive Chart.js visualizations.

---

## 🌟 Key Features

1. **User Authentication & Authorization**:
   - Secure Registration & Login with Werkzeug password hashing (bcrypt).
   - Stateless JWT (JSON Web Token) authentication with authorization headers.
   - Protected API routes and protected client side routes.

2. **Trip & Member Management**:
   - Create, view, edit, and delete trips with destinations, dates, and descriptions.
   - Add/Remove trip members (friends/travel companions).
   - Automatic assignment of trip creator as the primary member.

3. **Expense Splitting & Category Tracking**:
   - Log expenses with title, amount, category, payer, date, notes, and custom shared member selection.
   - Categories: **Food**, **Travel**, **Hotel**, **Shopping**, **Entertainment**, **Other**.
   - Automatic backend calculation of split amounts ($Amount / N$).

4. **Greedy Debt Simplification Settlement Algorithm**:
   - Calculates individual member **Total Paid**, **Total Share**, and **Net Balance** ($Balance = Paid - Share$).
   - Greedy debt matching algorithm pairs largest debtors with largest creditors to minimize total money transfer transactions.

5. **Interactive Summary & Visualizations**:
   - Real-time Chart.js doughnut chart for expenses by category.
   - Real-time Chart.js bar chart for member contribution comparison.
   - Professional responsive UI with Bootstrap 5 and FontAwesome icons.

---

## 🛠️ Technology Stack

### Backend
- **Python 3.10+**
- **Flask** (Web Framework & REST APIs)
- **Flask-SQLAlchemy** (ORM)
- **PyJWT** (JSON Web Tokens)
- **Werkzeug** (Password hashing & security)
- **Flask-CORS** (Cross-Origin Resource Sharing)

### Frontend
- **HTML5 & CSS3**
- **Bootstrap 5.3** (UI Framework)
- **JavaScript (ES6+)**
- **Fetch API** (Asynchronous HTTP requests)
- **Chart.js** (Data visualization)

### Database
- **SQLite** (Relational Database)

---

## 📁 Project Folder Structure

```
Trip-Expense-Management/
│
├── backend/
│   ├── app.py                  # Flask Application Entrypoint & Static Server
│   ├── config.py               # Application & JWT Configurations
│   ├── requirements.txt        # Python Dependencies
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py               # SQLAlchemy Instance
│   │   └── seed.py             # Demo Data Population Script
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User Model
│   │   ├── trip.py             # Trip Model
│   │   ├── member.py           # Trip Member Model
│   │   └── expense.py          # Expense & ExpenseShare Models
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # Auth Endpoints (/api/register, /api/login, /api/me)
│   │   ├── trip_routes.py      # Trip & Member Endpoints
│   │   ├── expense_routes.py   # Expense Endpoints
│   │   └── settlement_routes.py# Settlements & Summary Endpoints
│   │
│   └── services/
│       ├── __init__.py
│       ├── expense_service.py  # Expense Splitting Logic
│       └── settlement_service.py # Debt Simplification Algorithm
│
├── frontend/
│   ├── index.html              # Landing Page
│   ├── login.html              # Login Page
│   ├── register.html           # Registration Page
│   ├── dashboard.html          # Main User Dashboard
│   ├── create-trip.html        # Create Trip Form
│   ├── trip-details.html       # Single Trip Workspace (Tabs for Expenses, Members, Settlements)
│   ├── expenses.html           # Expenses Redirect Page
│   ├── settlements.html        # Settlements Redirect Page
│   ├── profile.html            # User Profile Page
│   │
│   ├── css/
│   │   └── style.css           # Custom CSS & Theme Overrides
│   │
│   └── js/
│       ├── config.js           # API Base URL & Fetch Helpers
│       ├── auth.js             # Authentication Logic
│       ├── dashboard.js        # Dashboard Metrics & Stats
│       ├── trips.js            # Trip & Member Handling
│       ├── expenses.js         # Expense CRUD & Splitting UI
│       └── settlements.js      # Settlement Tables & Chart.js Integration
│
├── database/
│   └── schema.sql              # Raw SQL Schema Documentation
│
├── .env                        # Environment Variables
├── .gitignore                  # Git Ignore Rules
└── README.md                   # Complete Documentation
```

---

## 🗄️ Database Tables & Schema

1. **`users`**: Stores user authentication accounts.
   - `id`, `name`, `email` (UNIQUE), `password_hash`, `created_at`
2. **`trips`**: Stores trip information.
   - `id`, `name`, `destination`, `start_date`, `end_date`, `description`, `created_by` (FK -> `users.id`), `created_at`
3. **`trip_members`**: Stores trip participants.
   - `id`, `trip_id` (FK -> `trips.id`), `name`, `email`, `user_id` (FK -> `users.id`), `joined_at`
4. **`expenses`**: Stores individual expense transactions.
   - `id`, `trip_id` (FK -> `trips.id`), `title`, `amount`, `category`, `paid_by_member_id` (FK -> `trip_members.id`), `expense_date`, `notes`, `created_at`
5. **`expense_shares`**: Stores cost allocation per member for an expense.
   - `id`, `expense_id` (FK -> `expenses.id`), `member_id` (FK -> `trip_members.id`), `share_amount`

---

## 🔌 API Endpoints Reference

### Authentication
- `POST /api/register` - Register a new user account.
- `POST /api/login` - Authenticate user and receive JWT access token.
- `GET /api/me` - Get profile info of current logged-in user.
- `POST /api/logout` - Logout user.

### Trips
- `GET /api/trips` - List trips created by or joined by current user.
- `POST /api/trips` - Create a new trip.
- `GET /api/trips/<trip_id>` - Get single trip details with members & expenses.
- `PUT /api/trips/<trip_id>` - Update trip details.
- `DELETE /api/trips/<trip_id>` - Delete a trip.

### Members
- `GET /api/trips/<trip_id>/members` - Get members of a trip.
- `POST /api/trips/<trip_id>/members` - Add a member to a trip.
- `DELETE /api/members/<member_id>` - Remove a member from a trip.

### Expenses
- `GET /api/trips/<trip_id>/expenses` - Get expenses for a trip (supports category, search, and sort filters).
- `POST /api/trips/<trip_id>/expenses` - Add a new expense (auto-splits across shared members).
- `PUT /api/expenses/<expense_id>` - Update an expense.
- `DELETE /api/expenses/<expense_id>` - Delete an expense.

### Settlements & Dashboard
- `GET /api/trips/<trip_id>/settlements` - Get calculated member balances & simplified settlement transactions.
- `GET /api/trips/<trip_id>/summary` - Get full trip summary including category breakdown.
- `GET /api/dashboard/stats` - Get user-level statistics (trips count, total paid, owe, receive amounts).

---

## ⚙️ Installation & Setup Instructions

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Set Up Virtual Environment

#### Windows (PowerShell):
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Ensure the `.env` file exists in the root directory:
```env
SECRET_KEY=antigravity_trip_expense_super_secret_key_2026
JWT_SECRET_KEY=antigravity_jwt_secret_key_trip_app_2026
FLASK_ENV=development
PORT=5000
```

### 5. Initialize & Seed Database
Populate SQLite database with demo user and sample trip data:
```bash
python backend/database/seed.py
```

### 6. Run Flask Backend & Frontend Server
```bash
python backend/app.py
```

### 7. Access Application in Browser
Open your browser and navigate to:
[http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔑 Demo Login Credentials

- **Email**: `demo@example.com`
- **Password**: `password123`

The demo dataset comes with **"Manali Adventure Trip"** featuring 4 members (John Doe, Alice Smith, Bob Johnson, Charlie Brown) and 5 pre-configured expenses showcasing splits and settlement calculations.

---

## 🧠 Debt Simplification Algorithm

The application implements a **Greedy Debt Simplification Algorithm** in `backend/services/settlement_service.py`:

1. Calculate `Net Balance` for every member $m$:
   $$\text{Balance}_m = \text{Total Paid}_m - \text{Total Share}_m$$
2. Separate members into `Debtors` ($\text{Balance} < 0$) and `Creditors` ($\text{Balance} > 0$).
3. Sort Debtors descending by debt magnitude and Creditors descending by credit magnitude.
4. Repeatedly match top debtor $D$ with top creditor $C$:
   $$\text{Payment} = \min(|Balance_D|, Balance_C)$$
5. Adjust balances until all debts are fully cleared. This guarantees at most $N - 1$ payment transactions for $N$ members.
