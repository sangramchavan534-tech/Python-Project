# Banking Management System (Python + MySQL)

## Project features
- Create customer accounts
- Check account details and balance
- Deposit and withdraw money
- Transfer funds between accounts
- View transaction history
- Store data persistently in MySQL

## Requirements
- Python 3.9 or newer
- MySQL Server and MySQL Workbench (Workbench is optional)
- `mysql-connector-python`

## Setup instructions

### 1. Create the database
Open MySQL Workbench, open `schema.sql`, and execute the complete script.

### 2. Install the Python dependency
Open a terminal in this project folder and run:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the database connection
Open `db.py` and replace `YOUR_MYSQL_PASSWORD` with your local MySQL password.
Do not share a real database password in submitted source code.

### 4. Test the connection
Run:

```bash
python db.py
```

Expected output: `Database connected successfully!`

### 5. Run the project
Run:

```bash
python main.py
```

## Suggested student test cases
1. Create two accounts.
2. Deposit money and verify the balance.
3. Withdraw an amount within the balance.
4. Try to withdraw more than the balance; the operation should be rejected.
5. Transfer money between accounts and check both balances.
6. Verify that transfer-in and transfer-out entries appear in both accounts' histories.
7. Close and restart the program, then verify the data is still stored in MySQL.

## Files
- `main.py`: menu and program entry point
- `bank.py`: banking operations
- `db.py`: MySQL connection configuration
- `schema.sql`: database and table definitions
- `requirements.txt`: Python dependency list

## Notes
This is an educational project, not production banking software. It does not implement customer login, PIN verification, role-based access, or production-grade auditing. Use only sample data.
