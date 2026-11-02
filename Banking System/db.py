import mysql.connector
from mysql.connector import Error


def get_connection():
    """Create and return a connection to the banking database."""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="YOUR_MYSQL_PASSWORD",  # Change this to your MySQL password
        database="banking_db",
        autocommit=False,
    )


if __name__ == "__main__":
    connection = None
    try:
        connection = get_connection()
        print("Database connected successfully!")
    except Error as error:
        print("Database connection failed:", error)
    finally:
        if connection and connection.is_connected():
            connection.close()
