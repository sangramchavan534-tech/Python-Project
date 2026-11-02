from decimal import Decimal, InvalidOperation
from mysql.connector import Error
from db import get_connection


def read_account_number(message="Enter account number: "):
    try:
        number = int(input(message))
        if number <= 0:
            raise ValueError
        return number
    except ValueError:
        print("Please enter a valid positive account number.")
        return None


def read_amount(message):
    try:
        amount = Decimal(input(message)).quantize(Decimal("0.01"))
        if not amount.is_finite() or amount <= 0:
            raise ValueError
        return amount
    except (ValueError, InvalidOperation):
        print("Please enter a valid amount greater than zero.")
        return None


def create_account():
    name = input("Customer name: ").strip()
    phone = input("Phone number (optional): ").strip()

    if not name:
        print("Customer name is required.")
        return

    opening_balance = read_amount("Opening balance (enter 0 if none): ")
    # Opening balance may be zero, unlike later deposits/withdrawals.
    if opening_balance is None:
        if input("Would you like to open the account with Rs. 0.00? (y/n): ").lower() != "y":
            return
        opening_balance = Decimal("0.00")

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO accounts (customer_name, phone, balance) VALUES (%s, %s, %s)",
            (name, phone or None, opening_balance),
        )
        account_number = cursor.lastrowid

        if opening_balance > 0:
            cursor.execute(
                """INSERT INTO transactions
                   (account_number, transaction_type, amount, description)
                   VALUES (%s, %s, %s, %s)""",
                (account_number, "DEPOSIT", opening_balance, "Opening balance"),
            )

        connection.commit()
        print("Account created successfully.")
        print("Account number:", account_number)
    except Error as error:
        if connection:
            connection.rollback()
        print("Could not create account:", error)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def check_balance():
    account_number = read_account_number()
    if account_number is None:
        return

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT customer_name, phone, balance, created_at FROM accounts WHERE account_number = %s",
            (account_number,),
        )
        account = cursor.fetchone()
        if account:
            print("\n--- Account Details ---")
            print("Customer:", account[0])
            print("Phone:", account[1] or "Not provided")
            print("Balance: Rs.", account[2])
            print("Created:", account[3])
        else:
            print("Account not found.")
    except Error as error:
        print("Could not retrieve account:", error)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def deposit_money():
    account_number = read_account_number()
    if account_number is None:
        return
    amount = read_amount("Deposit amount: ")
    if amount is None:
        return

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_number = %s",
            (amount, account_number),
        )
        if cursor.rowcount == 0:
            connection.rollback()
            print("Account not found.")
            return

        cursor.execute(
            """INSERT INTO transactions
               (account_number, transaction_type, amount, description)
               VALUES (%s, %s, %s, %s)""",
            (account_number, "DEPOSIT", amount, "Cash deposit"),
        )
        connection.commit()
        print("Deposit successful.")
    except Error as error:
        if connection:
            connection.rollback()
        print("Deposit failed:", error)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def withdraw_money():
    account_number = read_account_number()
    if account_number is None:
        return
    amount = read_amount("Withdrawal amount: ")
    if amount is None:
        return

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT balance FROM accounts WHERE account_number = %s FOR UPDATE",
            (account_number,),
        )
        account = cursor.fetchone()

        if not account:
            connection.rollback()
            print("Account not found.")
            return
        if account[0] < amount:
            connection.rollback()
            print("Insufficient balance.")
            return

        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_number = %s",
            (amount, account_number),
        )
        cursor.execute(
            """INSERT INTO transactions
               (account_number, transaction_type, amount, description)
               VALUES (%s, %s, %s, %s)""",
            (account_number, "WITHDRAWAL", amount, "Cash withdrawal"),
        )
        connection.commit()
        print("Withdrawal successful.")
    except Error as error:
        if connection:
            connection.rollback()
        print("Withdrawal failed:", error)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def transfer_money():
    sender = read_account_number("Sender account number: ")
    receiver = read_account_number("Receiver account number: ")
    if sender is None or receiver is None:
        return
    if sender == receiver:
        print("Sender and receiver must be different accounts.")
        return

    amount = read_amount("Transfer amount: ")
    if amount is None:
        return

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Lock both accounts in a consistent order to reduce deadlock risk.
        balances = {}
        for account_number in sorted((sender, receiver)):
            cursor.execute(
                "SELECT balance FROM accounts WHERE account_number = %s FOR UPDATE",
                (account_number,),
            )
            row = cursor.fetchone()
            if row is None:
                connection.rollback()
                print("One or both accounts were not found.")
                return
            balances[account_number] = row[0]

        if balances[sender] < amount:
            connection.rollback()
            print("Insufficient balance.")
            return

        cursor.execute(
            "UPDATE accounts SET balance = balance - %s WHERE account_number = %s",
            (amount, sender),
        )
        cursor.execute(
            "UPDATE accounts SET balance = balance + %s WHERE account_number = %s",
            (amount, receiver),
        )
        cursor.execute(
            """INSERT INTO transactions
               (account_number, transaction_type, amount, description)
               VALUES (%s, %s, %s, %s)""",
            (sender, "TRANSFER_OUT", amount, f"Transfer to account {receiver}"),
        )
        cursor.execute(
            """INSERT INTO transactions
               (account_number, transaction_type, amount, description)
               VALUES (%s, %s, %s, %s)""",
            (receiver, "TRANSFER_IN", amount, f"Transfer from account {sender}"),
        )
        connection.commit()
        print("Transfer completed successfully.")
    except Error as error:
        if connection:
            connection.rollback()
        print("Transfer failed:", error)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def transaction_history():
    account_number = read_account_number()
    if account_number is None:
        return

    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            """SELECT transaction_id, transaction_type, amount,
                      transaction_date, description
               FROM transactions
               WHERE account_number = %s
               ORDER BY transaction_id DESC""",
            (account_number,),
        )
        rows = cursor.fetchall()
        if not rows:
            print("No transactions found for this account.")
            return

        print("\n--- Transaction History ---")
        for row in rows:
            print(
                f"ID: {row[0]} | Type: {row[1]} | Amount: Rs. {row[2]} | "
                f"Date: {row[3]} | Details: {row[4] or '-'}"
            )
    except Error as error:
        print("Could not retrieve transactions:", error)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
