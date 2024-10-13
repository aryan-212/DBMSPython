import os
import mysql.connector
from mysql.connector import Error

def create_connection():
    """Create a database connection using environment variables"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'HostelManagement')
        )
        if connection.is_connected():
            print("Successfully connected to the database")
            return connection
    except Error as e:
        print(f"Error: '{e}'")
        return None

def fetch_students():
    """Fetch and display students"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM STUDENT;")
        result = cursor.fetchall()
        for row in result:
            print(row)
        cursor.close()
        connection.close()

def insert_student(student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no):
    """Insert a new student into the database"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        sql = """INSERT INTO STUDENT (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s);"""
        values = (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no)
        try:
            cursor.execute(sql, values)
            connection.commit()
            print(f"Student {name} added successfully!")
        except Error as e:
            print(f"Error: '{e}'")
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Insert a sample student and then fetch all students
    insert_student('S003', 'Charlie Brown', 'Mechanical Engineering', 'Standard', 'Weekly', 1, 101)
    fetch_students()
