# Global arrays (Lists) for different interfaces
bookings = []
rooms = [{"room_number": i, "status": "unoccupied"} for i in range(1, 11)]  
food_orders = []
bills = []
cleaning_requests = []

# Global variable to store the total price across interfaces
total_price = 0

import sqlite3
import atexit

# Connect SQLite 
conn = sqlite3.connect(r'C:\Users\USER\OneDrive\Desktop\hotelmanagement.db')  
cursor = conn.cursor()

# Create table
def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "USER" (
            "ID" INTEGER PRIMARY KEY AUTOINCREMENT,
            "NAME" TEXT NOT NULL,
            "ROOM_TYPE" TEXT NOT NULL,
            "NIGHTS" INTEGER NOT NULL,
            "TOTAL_PRICE" REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "STAFF" (
            "ROOM_NUMBER" INTEGER PRIMARY KEY,
            "STATUS" TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "KITCHEN" (
            "NAME" TEXT NOT NULL,
            "FOOD" TEXT NOT NULL,
            "PRICE" REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "BILL" (
            "NAME" TEXT NOT NULL,
            "TOTAL" REAL NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "CLEANING_SERVICE" (
            "ROOM_NUMBER" INTEGER NOT NULL
        )
    ''')

    conn.commit()

def initialize_rooms():
    cursor.execute("SELECT COUNT(*) FROM STAFF")
    if cursor.fetchone()[0] == 0:  
        for i in range(1, 11):  
            cursor.execute("INSERT INTO STAFF (ROOM_NUMBER, STATUS) VALUES (?, ?)", (i, "unoccupied"))
        conn.commit()

# ========== USER INTERFACE (Booking System) ==========

def create_booking():
    global total_price  
    name = input("Enter your name: ")
    room_type = input("Enter room type (Single/Double/Suite): ")
    nights = int(input("Enter number of nights: "))

    base_price = {"Single": 50, "Double": 100, "Suite": 200}
    if room_type in base_price:
        price = base_price[room_type] * nights
        discount = price * 0.1 if price > 150 else 0
        total_price = price + (price * 0.06) - discount
    else:
        print("Invalid room type.")
        return

    cursor.execute("INSERT INTO USER (NAME, ROOM_TYPE, NIGHTS, TOTAL_PRICE) VALUES (?, ?, ?, ?)", 
                   (name, room_type, nights, total_price))
    conn.commit()

    print(f"Booking created! Total Price: ${total_price:.2f}")


def read_bookings():
    cursor.execute("SELECT * FROM USER")
    bookings = cursor.fetchall()

    if not bookings:
        print("No bookings found.")
    else:
        for booking in bookings:
            print(f"ID: {booking[0]}, Name: {booking[1]}, Room: {booking[2]}, Nights: {booking[3]}, Total: ${booking[4]:.2f}")

def update_booking():
    booking_id = int(input("Enter the booking ID to update: "))
    new_nights = int(input("Enter new number of nights: "))
    
    cursor.execute("SELECT room_type FROM USER WHERE ID = ?", (booking_id,))
    room_type = cursor.fetchone()
    
    if room_type:
        room_type = room_type[0]
        base_price = {"Single": 50, "Double": 100, "Suite": 200}
        if room_type in base_price:
            price = base_price[room_type] * new_nights
            discount = price * 0.1 if price > 150 else 0
            total_price = price + (price * 0.06) - discount
        else:
            print("Invalid room type.")
            return
        
        cursor.execute("UPDATE USER SET NIGHTS = ?, TOTAL_PRICE = ? WHERE ID = ?", 
                       (new_nights, total_price, booking_id))
        conn.commit()
        print("Booking updated successfully!")
    else:
        print("Booking not found.")

def delete_booking():
    booking_id = int(input("Enter the booking ID to delete: "))
    cursor.execute("DELETE FROM USER WHERE ID = ?", (booking_id,))
    conn.commit()
    print("Booking deleted!")


# ========== STAFF INTERFACE (Manage Room Availability) ==========

# Checking room for availability
def check_available_rooms():
    cursor.execute("SELECT ROOM_NUMBER FROM STAFF WHERE STATUS = 'unoccupied'")
    available_rooms = cursor.fetchall()

    if not available_rooms:
        print("No available rooms.")
    else:
        print("Available Rooms:", [room[0] for room in available_rooms])

# Update room status
def update_room_status():
    room_num = int(input("Enter room number to toggle status (Occupied/Unoccupied): "))

    cursor.execute("SELECT STATUS FROM STAFF WHERE ROOM_NUMBER = ?", (room_num,))
    room = cursor.fetchone()

    if room:
        new_status = "occupied" if room[0] == "unoccupied" else "unoccupied"
        cursor.execute("UPDATE STAFF SET STATUS = ? WHERE ROOM_NUMBER = ?", (new_status, room_num))
        conn.commit()
        print(f"Room {room_num} is now {new_status}!")
    else:
        print("Room not found.")

# ========== KITCHEN INTERFACE (Food Orders) ==========

def order_food():
    name = input("Enter customer name: ")
    food_name = input("Enter food name: ")
    price = float(input("Enter price: "))
    cursor.execute("INSERT INTO KITCHEN (NAME, FOOD, PRICE) VALUES (?, ?, ?)", (name, food_name, price))
    conn.commit()
    print(f"Food order added for {name}.")

def view_food_orders():
    cursor.execute("SELECT * FROM KITCHEN")
    orders = cursor.fetchall()
    for order in orders:
        print(f"Name: {order[0]}, Food: {order[1]}, Price: ${order[2]:.2f}")


def update_food_order():
    name = input("Enter the customer name to update food order: ")
    food_name = input("Enter the food name to update: ")

    cursor.execute("SELECT * FROM KITCHEN WHERE NAME = ? AND FOOD = ?", (name, food_name))
    order = cursor.fetchone()

    if order:
        new_food_name = input("Enter new food name: ")
        new_price = float(input("Enter new price: "))
        
        cursor.execute("UPDATE KITCHEN SET FOOD = ?, PRICE = ? WHERE NAME = ? AND FOOD = ?", 
                       (new_food_name, new_price, name, food_name))
        conn.commit()

        print(f"Food order for {name} updated!")
    else:
        print("Food order not found.")

def delete_food_order():
    name = input("Enter the customer name to delete food order: ")
    food_name = input("Enter the food name to delete: ")

    cursor.execute("DELETE FROM KITCHEN WHERE NAME = ? AND FOOD = ?", (name, food_name))
    conn.commit()
    print(f"Food order for {name} removed!")

# ========== BILLING INTERFACE (Calculate Bills) ==========

def generate_bill():
    customer_name = input("Enter customer name to generate the total bill: ")

    # calculate total price user
    cursor.execute("SELECT SUM(TOTAL_PRICE) FROM USER WHERE NAME = ?", (customer_name,))
    booking_total = cursor.fetchone()[0] or 0

    # calculate kitchen price user
    cursor.execute("SELECT SUM(PRICE) FROM KITCHEN WHERE NAME = ?", (customer_name,))
    food_total = cursor.fetchone()[0] or 0

    # Total 
    customer_total = booking_total + food_total

    
    cursor.execute("INSERT INTO BILL (NAME, TOTAL) VALUES (?, ?)", (customer_name, customer_total))
    conn.commit()

    print(f"Total Bill for {customer_name}: ${customer_total:.2f}")



def update_bill():
    customer_name = input("Enter customer name to update the bill: ")

    # Update BILL table
    cursor.execute("SELECT * FROM BILL WHERE NAME = ?", (customer_name,))
    bill = cursor.fetchone()

    if bill:
        new_total = float(input("Enter new total bill amount: "))

        # Update total BILL table
        cursor.execute("UPDATE BILL SET TOTAL = ? WHERE NAME = ?", (new_total, customer_name))
        conn.commit()
        print(f"Bill for {customer_name} updated successfully!")
    else:
        print("Customer not found.")


def delete_bill():
    customer_name = input("Enter customer name to delete the bill: ")

    # Check user name
    cursor.execute("SELECT * FROM BILL WHERE NAME = ?", (customer_name,))
    bill = cursor.fetchone()

    if bill:
        cursor.execute("DELETE FROM BILL WHERE NAME = ?", (customer_name,))
        conn.commit()
        print(f"Bill for {customer_name} deleted successfully!")
    else:
        print("Customer not found.")


# ========== CLEANING SERVICE INTERFACE ==========

def request_cleaning():
    room_num = int(input("Enter room number for cleaning request: "))
    cursor.execute("INSERT INTO CLEANING_SERVICE (ROOM_NUMBER) VALUES (?)", (room_num,))
    conn.commit()
    print(f"Cleaning request added for Room {room_num}.")

def view_cleaning_requests():
    cursor.execute("SELECT * FROM CLEANING_SERVICE")
    requests = cursor.fetchall()
    for req in requests:
        print(f"Room: {req[0]}")

# ========== EXIT HANDLER ==========

def exit_handler():
    conn.close()
    print("Database connection closed.")

atexit.register(exit_handler)

# ========== MAIN MENU ==========

def main():
    create_tables()
    initialize_rooms()

    while True:
        print("\nHotel Booking System")
        print("1. User Interface")
        print("2. Staff Interface")
        print("3. Kitchen Interface")
        print("4. Billing Interface")
        print("5. Cleaning Service Interface")
        print("6. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            user_interface()
        elif choice == "2":
            staff_interface()
        elif choice == "3":
            kitchen_interface()
        elif choice == "4":
            billing_interface()
        elif choice == "5":
            cleaning_service_interface()
        elif choice == "6":
            print("Exiting system...")
            break
        else:
            print("Invalid choice! Try again.")

# ========== USER INTERFACE ==========

def user_interface():
    while True:
        print("\nUser Interface")
        print("1. Create Booking")
        print("2. View Bookings")
        print("3. Update Booking")
        print("4. Delete Booking")
        print("5. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            create_booking()
        elif choice == "2":
            read_bookings()
        elif choice == "3":
            update_booking()
        elif choice == "4":
            delete_booking()
        elif choice == "5":
            break


# ========== STAFF INTERFACE ==========

def staff_interface():
    while True:
        print("\nStaff Interface")
        print("1. Check Available Rooms")
        print("2. Update Room Status")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            check_available_rooms()  
        elif choice == "2":
            update_room_status()  
        elif choice == "3":
            break  
        else:
            print("Invalid choice! Try again.")

def kitchen_interface():
    while True:
        print("\nKitchen Interface")
        print("1. Order Food")
        print("2. View Food Orders")
        print("3. Update Food Order")
        print("4. Delete Food Order")
        print("5. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            order_food()
        elif choice == "2":
            view_food_orders()
        elif choice == "3":
            update_food_order()
        elif choice == "4":
            delete_food_order()
        elif choice == "5":
            break
        else:
            print("Invalid choice! Try again.")


def billing_interface():
    while True:
        print("\nBilling Interface")
        print("1. Generate Bill")
        print("2. Update Bill")
        print("3. Delete Bill")
        print("4. Back to Main Menu")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            generate_bill()
        elif choice == "2":
            update_bill()  
        elif choice == "3":
            delete_bill()
        elif choice == "4":
            break
        else:
            print("Invalid choice! Try again.")


def cleaning_service_interface():
    while True:
        print("\nCleaning Service Interface")
        print("1. Request Cleaning")
        print("2. View Cleaning Requests")
        print("3. Back to Main Menu")

        choice = input("Enter your choice: ")

        if choice == "1":
            request_cleaning()
        elif choice == "2":
            view_cleaning_requests()
        elif choice == "3":
            break

if __name__ == "__main__":
    main()