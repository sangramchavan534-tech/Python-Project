from bank import (
    create_account,
    check_balance,
    deposit_money,
    withdraw_money,
    transfer_money,
    transaction_history,
)


def main():
    while True:
        print("\n========== BANKING MANAGEMENT SYSTEM ==========")
        print("1. Create account")
        print("2. Check balance")
        print("3. Deposit money")
        print("4. Withdraw money")
        print("5. Transfer money")
        print("6. Transaction history")
        print("7. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            create_account()
        elif choice == "2":
            check_balance()
        elif choice == "3":
            deposit_money()
        elif choice == "4":
            withdraw_money()
        elif choice == "5":
            transfer_money()
        elif choice == "6":
            transaction_history()
        elif choice == "7":
            print("Thank you for using the Banking Management System.")
            break
        else:
            print("Invalid choice. Please select 1-7.")


if __name__ == "__main__":
    main()
