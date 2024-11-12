import streamlit as st
import mysql.connector
import os

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 4121)),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root_password"),
        database=os.getenv("DB_NAME", "HostelManagement"),
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )

# CRUD operations for Hostel table
def get_hostels():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM HOSTEL")
    hostels = cursor.fetchall()
    conn.close()
    return hostels

def add_hostel(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO HOSTEL (name) VALUES (%s)", (name,))
    conn.commit()
    conn.close()

def update_hostel(hostel_id, name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE HOSTEL SET name = %s WHERE hostel_id = %s", (name, hostel_id))
    conn.commit()
    conn.close()

def delete_hostel(hostel_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM HOSTEL WHERE hostel_id = %s", (hostel_id,))
    conn.commit()
    conn.close()

# CRUD operations for Student table
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM STUDENT")
    students = cursor.fetchall()
    conn.close()
    return students

def add_student(student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO STUDENT (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no))
    conn.commit()
    conn.close()

def update_student(student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE STUDENT 
        SET name = %s, course = %s, mess_plan = %s, laundry_plan = %s, hostel_id = %s, room_no = %s
        WHERE student_id = %s
    """, (name, course, mess_plan, laundry_plan, hostel_id, room_no, student_id))
    conn.commit()
    conn.close()

def delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM STUDENT WHERE student_id = %s", (student_id,))
    conn.commit()
    conn.close()

# Streamlit UI
st.title("Hostel Management System")

# Hostel CRUD
st.header("Hostel Management")

hostels = get_hostels()

st.subheader("Add New Hostel")
hostel_name = st.text_input("Hostel Name")
if st.button("Add Hostel"):
    add_hostel(hostel_name)
    st.success(f"Hostel '{hostel_name}' added successfully!")

st.subheader("Update Hostel")
hostel_id_to_update = st.selectbox("Select Hostel to Update", [hostel["hostel_id"] for hostel in hostels])
updated_hostel_name = st.text_input("Updated Hostel Name", value=hostels[0]["name"])
if st.button("Update Hostel"):
    update_hostel(hostel_id_to_update, updated_hostel_name)
    st.success(f"Hostel ID {hostel_id_to_update} updated successfully!")

st.subheader("Delete Hostel")
hostel_id_to_delete = st.selectbox("Select Hostel to Delete", [hostel["hostel_id"] for hostel in hostels])
if st.button("Delete Hostel"):
    delete_hostel(hostel_id_to_delete)
    st.success(f"Hostel ID {hostel_id_to_delete} deleted successfully!")

# Student CRUD
st.header("Student Management")

students = get_students()

st.subheader("Add New Student")
student_id = st.text_input("Student ID")
student_name = st.text_input("Student Name")
course = st.text_input("Course")
mess_plan = st.text_input("Mess Plan")
laundry_plan = st.text_input("Laundry Plan")
hostel_id = st.selectbox("Hostel", [hostel["hostel_id"] for hostel in hostels])
room_no = st.number_input("Room No", min_value=1)
if st.button("Add Student"):
    add_student(student_id, student_name, course, mess_plan, laundry_plan, hostel_id, room_no)
    st.success(f"Student '{student_name}' added successfully!")

st.subheader("Update Student")
student_id_to_update = st.selectbox("Select Student to Update", [student["student_id"] for student in students])
student_to_update = next(student for student in students if student["student_id"] == student_id_to_update)
updated_student_name = st.text_input("Updated Student Name", value=student_to_update["name"])
updated_course = st.text_input("Updated Course", value=student_to_update["course"])
updated_mess_plan = st.text_input("Updated Mess Plan", value=student_to_update["mess_plan"])
updated_laundry_plan = st.text_input("Updated Laundry Plan", value=student_to_update["laundry_plan"])
updated_hostel_id = st.selectbox("Updated Hostel", [hostel["hostel_id"] for hostel in hostels], index=hostels.index({"hostel_id": student_to_update["hostel_id"]}))
updated_room_no = st.number_input("Updated Room No", value=student_to_update["room_no"], min_value=1)
if st.button("Update Student"):
    update_student(student_id_to_update, updated_student_name, updated_course, updated_mess_plan, updated_laundry_plan, updated_hostel_id, updated_room_no)
    st.success(f"Student '{student_id_to_update}' updated successfully!")

st.subheader("Delete Student")
student_id_to_delete = st.selectbox("Select Student to Delete", [student["student_id"] for student in students])
if st.button("Delete Student"):
    delete_student(student_id_to_delete)
    st.success(f"Student '{student_id_to_delete}' deleted successfully!")
