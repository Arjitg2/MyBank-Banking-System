import random
import re
import sqlite3
from datetime import datetime

# Database connection setup
conn = sqlite3.connect('banking_system.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    account_number TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    dob TEXT NOT NULL,
                    city TEXT NOT NULL,
                    password TEXT NOT NULL,
                    initial_balance REAL NOT NULL,
                    contact_number TEXT NOT NULL,
                    email TEXT NOT NULL,
                    address TEXT NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS login (
                    account_number TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    active INTEGER NOT NULL)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_number TEXT,
                    transaction_type TEXT,
                    amount REAL,
                    transaction_time TEXT)''')


conn.commit()

class Bank:
    def __init__(self):
        self.conn = sqlite3.connect('banking_system.db')
        self.cursor = self.conn.cursor()
        self.logged_in_user = None

    def add_user(self):
        print("Add a New User")
        
        # Taking user input with validations
        name = input("Enter name: ")
        while not name.isalpha():
            print("Name should contain only alphabets.")
            name = input("Enter name: ")

        dob = input("Enter Date of Birth (YYYY-MM-DD): ")
        try:
            dob = datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please enter in YYYY-MM-DD.")
            return

        city = input("Enter city: ")
        contact_number = input("Enter contact number (10 digits): ")
        while not re.match(r'^\d{10}$', contact_number):
            print("Contact number must be 10 digits.")
            contact_number = input("Enter contact number: ")

        email = input("Enter Email ID: ")
        while not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z]+\.[a-zA-Z0-9-.]+$', email):
            print("Invalid email format.")
            email = input("Enter Email ID: ")

        address = input("Enter address: ")
        
        account_number = str(random.randint(1000000000, 9999999999))  # Generate 10 digit account number

        password = input("Enter a password (min 8 characters, 1 uppercase, 1 special char): ")
        while not re.match(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            print("Password must be at least 8 characters long, with 1 uppercase, 1 digit, and 1 special character.")
            password = input("Enter password: ")

        initial_balance = float(input("Enter initial balance (min 2000): "))
        while initial_balance < 2000:
            print("Initial balance must be at least 2000.")
            initial_balance = float(input("Enter initial balance: "))

        # Insert data into the database
        cursor.execute('''INSERT INTO users (account_number, name, dob, city, password, initial_balance, contact_number, email, address) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (account_number, name, dob, city, password, initial_balance, contact_number, email, address))

        # Add login record with active status as 1
        cursor.execute('''INSERT INTO login (account_number, password, active) 
                          VALUES (?, ?, ?)''', (account_number, password, 1))

        conn.commit()
        print(f"User added successfully with account number {account_number}")

    def show_user(self):
        account_number = input("Enter account number to search: ")
        cursor.execute("SELECT * FROM users WHERE account_number=?", (account_number,))
        user = cursor.fetchone()

        if user:
            print("\nUser Information:")
            print(f"Name: {user[1]}")
            print(f"DOB: {user[2]}")
            print(f"City: {user[3]}")
            print(f"Initial Balance: {user[5]}")
            print(f"Contact Number: {user[6]}")
            print(f"Email: {user[7]}")
            print(f"Address: {user[8]}")
        else:
            print("User not found.")

    def login(self):
        account_number = input("Enter account number: ")
        password = input("Enter password: ")

        cursor.execute("SELECT * FROM login WHERE account_number=? AND password=?", (account_number, password))
        user_login = cursor.fetchone()

        if user_login:
            if user_login[2] == 0:
                print("Account is deactivated. Please contact support.")
                return

            print(f"Login successful for account {account_number}")
            self.logged_in_user = account_number
            self.user_dashboard()
        else:
            print("Invalid credentials. Please try again.")

    def user_dashboard(self):
        while True:
            print("\nUSER DASHBOARD")
            print("1. Show Balance")
            print("2. Show Transactions")
            print("3. Credit Amount")
            print("4. Debit Amount")
            print("5. Transfer Amount")
            print("6. Deactivate Account")
            print("7. Change Password")
            print("8. Update Profile")
            print("9. Logout")
            
            choice = int(input("Enter your choice: "))
            if choice == 1:
                self.show_balance()
            elif choice == 2:
                self.show_transactions()
            elif choice == 3:
                self.credit_amount()
            elif choice == 4:
                self.debit_amount()
            elif choice == 5:
                self.transfer_amount()
            elif choice == 6:
                self.deactivate_account()
            elif choice == 7:
                self.change_password()
            elif choice == 8:
                self.update_profile()
            elif choice == 9:
                self.logout()
                break

    def show_balance(self):
        cursor.execute("SELECT initial_balance FROM users WHERE account_number=?", (self.logged_in_user,))
        balance = cursor.fetchone()[0]
        print(f"Your balance is: {balance}")

    def show_transactions(self):
        cursor.execute("SELECT * FROM transaction WHERE account_number=?", (self.logged_in_user,))
        transactions = cursor.fetchall()
        
        if transactions:
            print("Transaction History:")
            for txn in transactions:
                print(f"ID: {txn[0]}, Type: {txn[2]}, Amount: {txn[3]}, Date: {txn[4]}")
        else:
            print("No transactions found.")

    def credit_amount(self):
        amount = float(input("Enter amount to credit: "))
        cursor.execute("SELECT initial_balance FROM users WHERE account_number=?", (self.logged_in_user,))
        balance = cursor.fetchone()[0]
        new_balance = balance + amount
        cursor.execute("UPDATE users SET initial_balance=? WHERE account_number=?", (new_balance, self.logged_in_user))
        cursor.execute("INSERT INTO transaction (account_number, transaction_type, amount, transaction_time) VALUES (?, ?, ?, ?)", 
                       (self.logged_in_user, 'Credit', amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()
        print(f"Amount credited successfully. New balance: {new_balance}")

    def debit_amount(self):
        amount = float(input("Enter amount to debit: "))
        cursor.execute("SELECT initial_balance FROM users WHERE account_number=?", (self.logged_in_user,))
        balance = cursor.fetchone()[0]
        if balance >= amount:
            new_balance = balance - amount
            cursor.execute("UPDATE users SET initial_balance=? WHERE account_number=?", (new_balance, self.logged_in_user))
            cursor.execute("INSERT INTO transaction (account_number, transaction_type, amount, transaction_time) VALUES (?, ?, ?, ?)", 
                           (self.logged_in_user, 'Debit', amount, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            print(f"Amount debited successfully. New balance: {new_balance}")
        else:
            print("Insufficient balance.")

    def transfer_amount(self):
        to_account = input("Enter recipient account number: ")
        amount = float(input("Enter amount to transfer: "))
        
        # Fetch sender and recipient balances
        self.cursor.execute("SELECT initial_balance FROM users WHERE account_number=?", (self.logged_in_user,))
        sender_balance = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT initial_balance FROM users WHERE account_number=?", (to_account,))
        recipient_balance = self.cursor.fetchone()

        if sender_balance >= amount and recipient_balance:
            # Update balances and insert transactions
            self.cursor.execute("UPDATE users SET initial_balance=? WHERE account_number=?", 
                                (sender_balance - amount, self.logged_in_user))
            self.cursor.execute("UPDATE users SET initial_balance=? WHERE account_number=?", 
                                (recipient_balance[0] + amount, to_account))
            
            transaction_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.executemany('''INSERT INTO transactions (account_number, transaction_type, amount, transaction_time) 
                                       VALUES (?, ?, ?, ?)''', [
                                       (self.logged_in_user, 'Transfer', -amount, transaction_time),
                                       (to_account, 'Transfer', amount, transaction_time)
                                       ])
            
            self.conn.commit()
            print(f"Transfer successful. New balance: {sender_balance - amount}")
        else:
            print("Insufficient balance or recipient not found.")

    def deactivate_account(self):
        cursor.execute("UPDATE login SET active=0 WHERE account_number=?", (self.logged_in_user,))
        conn.commit()
        print("Account deactivated.")

    def change_password(self):
        new_password = input("Enter new password: ")
        cursor.execute("UPDATE login SET password=? WHERE account_number=?", (new_password, self.logged_in_user))
        conn.commit()
        print("Password changed successfully.")

    def update_profile(self):
        print("Update Profile")
        name = input("Enter new name: ")
        city = input("Enter new city: ")
        email = input("Enter new email: ")
        contact_number = input("Enter new contact number: ")
        address = input("Enter new address: ")
        
        cursor.execute('''UPDATE users SET name=?, city=?, email=?, contact_number=?, address=? WHERE account_number=?''', 
                       (name, city, email, contact_number, address, self.logged_in_user))
        conn.commit()
        print("Profile updated successfully.")

    def logout(self):
        self.logged_in_user = None
        print("Logged out successfully.")

def main():
    bank = Bank()
    
    while True:
        print("\nBANKING SYSTEM")
        print("1. Add User")
        print("2. Show User")
        print("3. Login")
        print("4. Exit")
        
        choice = int(input("Enter your choice: "))
        
        if choice == 1:
            bank.add_user()
        elif choice == 2:
            bank.show_user()
        elif choice == 3:
            bank.login()
        elif choice == 4:
            print("Exiting...")
            break

if __name__ == "__main__":
    main()
