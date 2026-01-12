import mysql.connector
import re
from mysql.connector import Error

myconn = mysql.connector.connect( host="localhost",
                                user="root",
                                password="root",
                                database='project',
                                auth_plugin='mysql_native_password')
cur = myconn.cursor()
# ---------------- SQL-----------------
# user registration table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT unique,
    user_id int unique key,
    name VARCHAR(100),
    phone VARCHAR(10),
    address TEXT,
    password VARCHAR(255)
)
""")
# bike details table
cur.execute("""
CREATE TABLE IF NOT EXISTS bikes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(100),
    type VARCHAR(50),
    price_per_hour INT,
    stock INT
)
""")     #data inserted into bike table
cur.execute("""
INSERT INTO bikes (model, type, price_per_hour, stock) VALUES
('Hero Splendor', 'Standard', 50, 5),
('Honda Activa', 'Scooter', 70, 5),
('TVS Apache', 'Sports', 100, 3),
('Yamaha FZ', 'Sports', 90, 4)
""")
myconn.commit()

# rentals details
cur.execute("""
CREATE TABLE IF NOT EXISTS rentals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    bike_id INT,
    hours INT,
    cost INT
)
""")
myconn.commit()

def show_menu():
    print("\n****** Bike Rental System******")
    print("1. Registration")
    print("2. Login")
    print("3. Available Bikes")
    print("4. Rent Bike")
    print("5. Return Bike")
    print("6. Exit")
    choice = input("Select an option (1-6): ")
    return choice

def register_user():
    print("\n--- Registration ---")
    user_id = input("Enter your ID (5-digit number): ")
    name = input("Enter your name: ")
    address = input("Enter your address: ")
    print(" password must contain atleast 1 uppercase, 1 lowercase, 1 number, 1 special character: ")
    password = input("Enter a password")
    while True:
          phone = input("Enter your 10-digit mobile number: ").strip()
          if phone.isdigit() and len(phone) == 10:
                break
          else:
                print("Invalid mobile number. It must be exactly 10 digits.")
          if not (user_id.isdigit() and len(user_id) == 5):
                print("Incorrect ID. Please enter a 5-digit number.")
                return
          if not (re.search(r"[A-Z]", password) and
                re.search(r"[a-z]", password) and
                re.search(r"\d", password) and
                re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
                print("Incorrect password. Password must have at least 1 uppercase, 1 lowercase, 1 number, and 1 special character.")
                return

    # Insert user into database
    cur.execute("""
    INSERT INTO users (user_id, name, phone, address, password)
    VALUES (%s, %s, %s, %s, %s)
    """, (user_id, name, phone, address,password))
    myconn.commit()
    print(f"\nRegistration successful!\nName: {name}\nID: {user_id}\nPhone: {phone}\nAddress: {address}")
    print("Registration completed.")

#login section
def login_user():
    print("\n--- Login ---")
    username = input("Enter your username (name): ")
    cur.execute("SELECT password FROM users WHERE name = %s", (username,))
    row = cur.fetchone()
    if not row:
        print("User not found. Please register first.")
        return None

    attempts = 3
    while attempts > 0:
        password =input("Enter your password: ")
        if row[0] == password:
            print(f"Login successful for {username}.")
            return username
        else:
            attempts -= 1
            print(f"Invalid password. Attempts left: {attempts}")
    print("Login failed.")
    return None

# Available bikes
def show_bikes():
    print("\n--- Available Bikes ---")
    cur.execute("SELECT id, model, type, price_per_hour, stock FROM bikes")
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Model: {row[1]}, Type: {row[2]}, Price per hour: ₹{row[3]}, Stock: {row[4]}")

def rent_bike(current_user):
    if current_user is None:
        print("Please login first to rent a bike.")
        return

  
    # Check if user already has rental
    cur.execute("SELECT bike_id FROM rentals WHERE username = %s", (current_user,))
    if cur.fetchone():
        print("You already have a bike rented. Please return it first.")
        return

    show_bikes()
    try:
        bike_id = int(input("Select bike ID to rent: "))
        hours = int(input("Enter number of hours: "))
    except ValueError:
        print("Please enter valid numbers.")
        return

    if hours <= 0:
        print("Hours must be positive.")
        return

    cur.execute("SELECT stock, price_per_hour FROM bikes WHERE id = %s", (bike_id,))
    row = cur.fetchone()
    if not row:
        print("Invalid bike option.")
        return
    stock, price_per_hour = row
    if stock <= 0:
        print("Selected bike is not available.")
        return

    cost = price_per_hour * hours
    cur.execute("UPDATE bikes SET stock = stock - 1 WHERE id = %s", (bike_id,))
    cur.execute("INSERT INTO rentals (username, bike_id, hours, cost) VALUES (%s, %s, %s, %s)", (current_user, bike_id, hours, cost))
    myconn.commit()
    print(f"You have rented bike ID {bike_id} for {hours} hour(s). Total cost: ₹{cost}")

# return module
def return_bike(current_user):
    if current_user is None:
        print("Please login first to return a bike.")
        return

    cur.execute("SELECT id, bike_id, cost FROM rentals WHERE username = %s", (current_user,))
    row = cur.fetchone()
    if not row:
        print("You do not have any active rental.")
        return

    rental_id, bike_id, cost = row
    cur.execute("UPDATE bikes SET stock = stock + 1 WHERE id = %s", (bike_id,))
    myconn.commit()
    print(f"Bike returned successfully.")
    print(f"Your bill amount: ₹{cost}")

#user choice
def main():
    current_user = None
    while True:
        choice = show_menu()
        if choice == '1':
            register_user()
        elif choice == '2':
        
            current_user = login_user()
        elif choice == '3':
            show_bikes()
        elif choice == '4':
            rent_bike(current_user)
        elif choice == '5':
            return_bike(current_user)
        elif choice == '6':
            print("Exiting the application.")
            break
        else:
            print("Invalid option. Please select 1-6.")

if __name__ == "__main__":
    main()
    
