import streamlit as st
import mysql.connector
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
from dotenv import load_dotenv

# st.set_page_config(
#         page_title="Hostel Management System",
#         page_icon="🏢",
#         layout="wide"
#     )
load_dotenv()
def create_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 4121)),

        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root_password"),
        database=os.getenv("DB_NAME", "HostelManagement"),
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'  # Replace with your database name
    )

def get_database_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", 4121)),

        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root_password"),
        database=os.getenv("DB_NAME", "HostelManagement"),
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci'
    )

def get_columns(table_name):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(f"DESCRIBE {table_name};")
    columns = cursor.fetchall()
    conn.close()
    return [column[0] for column in columns]

# Function to search in a table by a selected column
def search_data(table_name, column, search_value):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    query = f"SELECT * FROM {table_name} WHERE {column} LIKE %s"
    cursor.execute(query, (f"%{search_value}%",))
    results = cursor.fetchall()
    conn.close()
    return pd.DataFrame(results)

def init_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'Dashboard'

def run_query(query, params=None):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        # Check if the query is a SELECT statement
        if query.strip().upper().startswith('SELECT') or query.strip().upper().startswith('CALL'):
            result = cursor.fetchall()

            # Consume any remaining result sets (if it's a stored procedure)
            while cursor.nextset():
                cursor.fetchall()

            return result
        
        # Commit changes if it's an INSERT, UPDATE, or DELETE query
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()


def dashboard():
    st.title("Hostel Management Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    # Total Students
    total_students = run_query("SELECT COUNT(*) as count FROM STUDENT")[0]['count']
    col1.metric("Total Students", total_students)
    
    # Available Rooms
    # occupied_rooms = run_query("SELECT COUNT(DISTINCT room_no) as count FROM STUDENT")[0]['count']
    # total_rooms = run_query("SELECT COUNT(*) as count FROM ROOM")[0]['count']
    # col2.metric("Available Rooms", total_rooms - occupied_rooms)
    
    # Pending Fees
    pending_fees = run_query("SELECT COUNT(*) as count FROM FEE WHERE status = 'Pending'")[0]['count']
    col3.metric("Pending Fees", pending_fees)
    
    # Room Occupancy Chart
    room_data = run_query("""
        SELECT r.type, COUNT(*) as count 
        FROM ROOM r 
        GROUP BY r.type
    """)
    if room_data:
        df_rooms = pd.DataFrame(room_data)
        fig = px.pie(df_rooms, values='count', names='type', title='Room Distribution')
        st.plotly_chart(fig)

def manage_students():
    st.header("Student Management")
    
    # Creating tabs for different operations
    tab1, tab2, tab3 = st.tabs(["View Students", "Add Student", "Update/Delete Student"])
    
    # Tab 1: View Students
    with tab1:
        # Get column names for STUDENT table
        columns = get_columns("STUDENT")
        
        # Select column to search
        column_option = st.selectbox("Select Column", columns)

        # Input for search value
        search_value = st.text_input(f"Enter {column_option} to search:")

        if st.button("Search"):
            if search_value:
                # Fetch and display search results
                results = search_data("STUDENT", column_option, search_value)
                if results.empty:
                    st.write(f"No results found for {search_value} in column {column_option}.")
                else:
                    st.write(f"Search Results for {search_value} in {column_option}:")
                    st.dataframe(results)
            else:
                st.warning("Please enter a search term.")

        # View all students
        students = run_query("SELECT * FROM STUDENT")
        if students:
            st.dataframe(pd.DataFrame(students))

    
    with tab2:
        with st.form("add_student_form"):
            student_id = st.text_input("Student ID")
            name = st.text_input("Name")
            course = st.text_input("Course")
            mess_plan = st.selectbox("Mess Plan", ["Standard", "Premium"])
            laundry_plan = st.selectbox("Laundry Plan", ["Basic", "Standard", "Premium"])

            # Fetch and display available hostels
            hostels = run_query("SELECT hostel_id, name FROM HOSTEL")
            hostel_dict = {h['name']: h['hostel_id'] for h in hostels}
            hostel = st.selectbox("Hostel", list(hostel_dict.keys()))

            # Fetch and display available rooms
            rooms = run_query("SELECT room_no, type FROM ROOM")
            room_dict = {f"Room {r['room_no']} ({r['type']})": r['room_no'] for r in rooms}
            room = st.selectbox("Room", list(room_dict.keys()))

            # Add Student button
            if st.form_submit_button("Add Student"):
                # Check current occupancy and capacity of the selected room
                room_no = room_dict[room]
                current_occupancy_result = run_query(
                    "SELECT current_occupancy FROM ROOM_OCCUPANCY WHERE room_no = %s", (room_no,)
                )
                print(current_occupancy_result)
                capacity_result = run_query(
                    "SELECT capacity FROM ROOM WHERE room_no = %s", (room_no,)
                )
                print(capacity_result)

                current_occupancy = current_occupancy_result[0]['current_occupancy'] if current_occupancy_result else 0
                capacity = capacity_result[0]['capacity'] if capacity_result else 0

                # Check if the room is full
                if current_occupancy >= capacity:
                    st.error(f"Room {room_no} is already full. Please choose another room.")
                else:
                    print(capacity-current_occupancy)
                    print(capacity-current_occupancy)

                    # Proceed to add the student if there's space
                    query = """
                    INSERT INTO STUDENT (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    params = (student_id, name, course, mess_plan, laundry_plan, hostel_dict[hostel], room_no)
                    
                    # Insert student and update occupancy
                    if run_query(query, params):
                        st.success("Student added successfully!")
                        st.rerun()

    with tab3:
        student_to_update = st.selectbox(
            "Select Student to Update/Delete",
            [s['student_id'] + " - " + s['name'] for s in run_query("SELECT student_id, name FROM STUDENT")]
        )
        if student_to_update:
            student_id = student_to_update.split(" - ")[0]
            student = run_query("SELECT * FROM STUDENT WHERE student_id = %s", (student_id,))[0]
            
            with st.form("update_student_form"):
                name = st.text_input("Name", student['name'])
                course = st.text_input("Course", student['course'])
                mess_plan = st.selectbox("Mess Plan", ["Standard", "Premium"], 
                                       ["Standard", "Premium"].index(student['mess_plan']))
                laundry_plan = st.selectbox("Laundry Plan", ["Basic", "Standard", "Premium"],
                                          ["Basic", "Standard", "Premium"].index(student['laundry_plan']))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Update Student"):
                        query = """
                        UPDATE STUDENT 
                        SET name = %s, course = %s, mess_plan = %s, laundry_plan = %s
                        WHERE student_id = %s
                        """
                        params = (name, course, mess_plan, laundry_plan, student_id)
                        if run_query(query, params):
                            st.success("Student updated successfully!")
                            st.rerun
                
                with col2:
                    if st.form_submit_button("Delete Student", type="primary"):
                        if run_query("DELETE FROM STUDENT WHERE student_id = %s", (student_id,)):
                            st.success("Student deleted successfully!")
                            st.rerun

def manage_rooms():
    st.header("Room Management")
    
    tab1, tab2, tab3 = st.tabs(["View Rooms", "Add Room", "Update Room"])
    
    # View Rooms tab
    
    with tab1:
         columns = get_columns("ROOM")
        
        # Select column to search
         column_option = st.selectbox("Select Column", columns)

        # Input for search value
         search_value = st.text_input(f"Enter {column_option} to search:")

         if st.button("Search"):
            if search_value:
                # Fetch and display search results
                results = search_data("ROOM", column_option, search_value)
                if results.empty:
                    st.write(f"No results found for {search_value} in column {column_option}.")
                else:
                    st.write(f"Search Results for {search_value} in {column_option}:")
                    st.dataframe(results)
            else:
                st.warning("Please enter a search term.")

         rooms = run_query("""
                SELECT r.*, COUNT(s.student_id) as occupants
                FROM ROOM r
                LEFT JOIN STUDENT s ON r.room_no = s.room_no
                GROUP BY r.room_no
            """)
         if rooms:
                st.dataframe(pd.DataFrame(rooms))
    
    # Add Room tab
    with tab2:
        with st.form("add_room_form"):
            room_no = st.number_input("Room Number", min_value=1)
            capacity = st.number_input("Capacity", min_value=1, max_value=4)
            room_type = st.selectbox("Room Type", ["Single", "Double", "Triple", "Dormitory"])
            
            if st.form_submit_button("Add Room"):
                query = "INSERT INTO ROOM (room_no, capacity, type) VALUES (%s, %s, %s)"
                params = (room_no, capacity, room_type)
                if run_query(query, params):
                    st.success("Room added successfully!")
                    st.rerun()
    
    # Update Room tab
    with tab3:
        rooms = run_query("SELECT room_no, capacity, type FROM ROOM")
        room_options = {f"Room {r['room_no']}": r for r in rooms}
        selected_room = st.selectbox("Select Room to Update", list(room_options.keys()))
        
        if selected_room:
            room_details = room_options[selected_room]
            new_capacity = st.number_input("New Capacity", min_value=1, max_value=4, value=room_details["capacity"])
            new_type = st.selectbox("New Room Type", ["Single", "Double", "Triple", "Dormitory"], index=["Single", "Double", "Triple", "Dormitory"].index(room_details["type"]))
            
            if st.button("Update Room"):
                query = "UPDATE ROOM SET capacity = %s, type = %s WHERE room_no = %s"
                params = (new_capacity, new_type, room_details["room_no"])
                if run_query(query, params):
                    st.success("Room updated successfully!")
                    st.rerun()

def manage_employees():
    st.header("Employee Management")

    # Tabs for different operations
    tab1, tab2, tab3 = st.tabs(["View Employees", "Add Employee", "Update Employee"])

    # Tab 1: View Employees
    with tab1:
        columns = get_columns("EMPLOYEE")
        
        # Select column to search
        column_option = st.selectbox("Select Column", columns)

        # Input for search value
        search_value = st.text_input(f"Enter {column_option} to search:")

        if st.button("Search"):
            if search_value:
                # Fetch and display search results
                results = search_data("EMPLOYEE", column_option, search_value)
                if results.empty:
                    st.write(f"No results found for {search_value} in column {column_option}.")
                else:
                    st.write(f"Search Results for {search_value} in {column_option}:")
                    st.dataframe(results)
            else:
                st.warning("Please enter a search term.")

        employees = run_query("SELECT * FROM EMPLOYEE")
        if employees:
            st.dataframe(pd.DataFrame(employees))

    # Tab 2: Add Employee
    with tab2:
        # print(run_query("CALL get_fee_details();"))

        with st.form("add_employee_form"):
            emp_id = st.text_input("Employee ID")
            name = st.text_input("Name")
            activity = st.selectbox("Activity", ["Cleaning", "Cooking", "Security", "Maintenance", "Admin"])
            service = st.selectbox("Service", ["Housekeeping", "Cafeteria", "Guarding", "Plumbing", "Reception"])

            # Button to add the employee
            if st.form_submit_button("Add Employee"):
                query = "INSERT INTO EMPLOYEE (emp_id, name, activity, service) VALUES (%s, %s, %s, %s)"
                params = (emp_id, name, activity, service)
                if run_query(query, params):
                    st.success("Employee added successfully!")
                    st.rerun

    # Tab 3: Update Employee
    with tab3:
        employees = run_query("SELECT emp_id, name FROM EMPLOYEE")
        emp_dict = {f"{e['name']} ({e['emp_id']})": e['emp_id'] for e in employees}

        if emp_dict:
            emp_to_update = st.selectbox("Select Employee to Update", list(emp_dict.keys()))
            if emp_to_update:
                emp_id = emp_dict[emp_to_update]
                employee = run_query("SELECT * FROM EMPLOYEE WHERE emp_id = %s", (emp_id,))[0]

                with st.form("update_employee_form"):
                    name = st.text_input("Name", value=employee['name'])
                    activity = st.selectbox(
                        "Activity",
                        ["Cleaning", "Cooking", "Security", "Maintenance", "Admin"],
                        index=["Cleaning", "Cooking", "Security", "Maintenance", "Admin"].index(employee['activity'])
                    )
                    service = st.selectbox(
                        "Service",
                        ["Housekeeping", "Cafeteria", "Guarding", "Plumbing", "Reception"],
                        index=["Housekeeping", "Cafeteria", "Guarding", "Plumbing", "Reception"].index(employee['service'])
                    )

                    # Button to update the employee
                    if st.form_submit_button("Update Employee"):
                        query = """
                        UPDATE EMPLOYEE 
                        SET name = %s, activity = %s, service = %s 
                        WHERE emp_id = %s
                        """
                        params = (name, activity, service, emp_id)
                        if run_query(query, params):
                            st.success("Employee updated successfully!")
                            st.rerun

def call_stored_procedure(proc_name, params=None):
    conn = get_database_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Call the stored procedure with parameters if provided
        cursor.callproc(proc_name, params or [])
        result = []
        
        # Fetch all the result sets returned by the stored procedure
        for result_set in cursor.stored_results():
            result.extend(result_set.fetchall())
        
        return result
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False
    finally:
        cursor.close()
        conn.close()


def manage_fees():
    st.header("Fee Management")
    
    tab1, tab2 = st.tabs(["View Fees", "Update Fee Status"])
    
    with tab1:
        # fees = run_query("""
        #     SELECT f.*, s.name as student_name
        #     FROM FEE f
        #     JOIN STUDENT s ON f.fee_id = CONCAT('F', LPAD(SUBSTRING(s.student_id, 2), 3, '0'))
        # """)
        fees = call_stored_procedure("get_fee_details")  # Using stored procedure

        
        if fees:
            st.dataframe(pd.DataFrame(fees))
    
    with tab2:
        fee_to_update = st.selectbox(
            "Select Fee to Update",
            [f"{f['fee_id']} - {f['student_name']} (₹{f['amount']})" for f in fees]
        )
        if fee_to_update:
            fee_id = fee_to_update.split(" - ")[0]
            with st.form("update_fee_form"):
                status = st.selectbox("Status", ["Pending", "Paid", "Overdue"])
                if st.form_submit_button("Update Status"):
                    query = "UPDATE FEE SET status = %s WHERE fee_id = %s"
                    params = (status, fee_id)
                    if run_query(query, params):
                        st.success("Fee status updated successfully!")
                        st.rerun

def main():
    
    
    init_session_state()
    
    with st.sidebar:
        st.title("🏢 Hostel Management")
        selected = st.radio(
            "Navigate to",
            ["Dashboard", "Students", "Rooms", "Fees", "Employees"]
        )
        st.session_state.page = selected

    if st.session_state.page == "Dashboard":
        dashboard()
    elif st.session_state.page == "Students":
        manage_students()
    elif st.session_state.page == "Rooms":
        manage_rooms()
    elif st.session_state.page == "Fees":
        manage_fees()
    elif st.session_state.page == "Employees":
        manage_employees()


if __name__ == "__main__":
    main()