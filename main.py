import os
import mysql.connector
from mysql.connector import Error
import flet as ft
from datetime import datetime

class DatabaseManager:
    @staticmethod
    def create_connection():
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=os.getenv("DB_PORT", 4121),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "root_password"),
                database=os.getenv("DB_NAME", "HostelManagement"),
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            return connection
        except Error as e:
            print(f"Error: '{e}'")
        return None

    @staticmethod
    def execute_query(query, values=None, fetch=False):
        connection = DatabaseManager.create_connection()
        result = None
        if connection:
            try:
                with connection.cursor() as cursor:
                    if values:
                        cursor.execute(query, values)
                    else:
                        cursor.execute(query)
                    
                    if fetch:
                        result = cursor.fetchall()
                    else:
                        connection.commit()
                        result = True
            except Error as e:
                print(f"Database error: {e}")
                result = False
            finally:
                connection.close()
        return result

class Student:
    @staticmethod
    def fetch_all():
        query = "SELECT * FROM STUDENT ORDER BY student_id;"
        return DatabaseManager.execute_query(query, fetch=True)

    @staticmethod
    def insert(student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no):
        query = """
        INSERT INTO STUDENT (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no) 
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        values = (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no)
        return DatabaseManager.execute_query(query, values)

    @staticmethod
    def update(student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no):
        query = """
        UPDATE STUDENT 
        SET name=%s, course=%s, mess_plan=%s, laundry_plan=%s, hostel_id=%s, room_no=%s 
        WHERE student_id=%s;
        """
        values = (name, course, mess_plan, laundry_plan, hostel_id, room_no, student_id)
        return DatabaseManager.execute_query(query, values)

    @staticmethod
    def delete(student_id):
        query = "DELETE FROM STUDENT WHERE student_id = %s;"
        return DatabaseManager.execute_query(query, (student_id,))

def main(page: ft.Page):
    page.title = "Hostel Management System"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1200
    page.window_height = 800
    page.padding = 20

    # State management
    current_student = None
    
    # Input fields
    student_id = ft.TextField(
        label="Student ID",
        width=200,
        height=50,
        border_radius=10,
    )
    name = ft.TextField(
        label="Name",
        width=200,
        height=50,
        border_radius=10,
    )
    course = ft.TextField(
        label="Course",
        width=200,
        height=50,
        border_radius=10,
    )
    mess_plan = ft.Dropdown(
        label="Mess Plan",
        width=200,
        options=[
            ft.dropdown.Option("Regular"),
            ft.dropdown.Option("Premium"),
            ft.dropdown.Option("Special Diet"),
        ],
    )
    laundry_plan = ft.Dropdown(
        label="Laundry Plan",
        width=200,
        options=[
            ft.dropdown.Option("Basic"),
            ft.dropdown.Option("Premium"),
            ft.dropdown.Option("None"),
        ],
    )
    hostel_id = ft.TextField(
        label="Hostel ID",
        width=200,
        height=50,
        border_radius=10,
    )
    room_no = ft.TextField(
        label="Room No",
        width=200,
        height=50,
        border_radius=10,
    )

    # DataTable for students
    def create_data_table():
        return ft.DataTable(
            border=ft.border.all(2, "grey"),
            border_radius=10,
            vertical_lines=ft.border.BorderSide(1, "grey"),
            horizontal_lines=ft.border.BorderSide(1, "grey"),
            columns=[
                ft.DataColumn(ft.Text("Student ID")),
                ft.DataColumn(ft.Text("Name")),
                ft.DataColumn(ft.Text("Course")),
                ft.DataColumn(ft.Text("Mess Plan")),
                ft.DataColumn(ft.Text("Laundry Plan")),
                ft.DataColumn(ft.Text("Hostel ID")),
                ft.DataColumn(ft.Text("Room No")),
                ft.DataColumn(ft.Text("Actions")),
            ],
        )

    students_table = create_data_table()

    # Snackbar for notifications
    def show_snackbar(message, color="green"):
        page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=color,
        )
        page.snack_bar.open = True
        page.update()

    # Clear form fields
    def clear_fields():
        student_id.value = ""
        name.value = ""
        course.value = ""
        mess_plan.value = None
        laundry_plan.value = None
        hostel_id.value = ""
        room_no.value = ""
        page.update()

    # Validate input fields
    def validate_fields():
        if not all([
            student_id.value, name.value, course.value,
            mess_plan.value, laundry_plan.value,
            hostel_id.value, room_no.value
        ]):
            show_snackbar("Please fill all fields", "red")
            return False
        return True

    # Load students into table
    def load_students():
        students_table.rows.clear()
        students = Student.fetch_all()
        
        for s in students:
            students_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(s[0])),
                        ft.DataCell(ft.Text(s[1])),
                        ft.DataCell(ft.Text(s[2])),
                        ft.DataCell(ft.Text(s[3])),
                        ft.DataCell(ft.Text(s[4])),
                        ft.DataCell(ft.Text(s[5])),
                        ft.DataCell(ft.Text(s[6])),
                        ft.DataCell(
                            ft.Row(
                                [
                                    ft.IconButton(
                                        icon=ft.icons.EDIT,
                                        icon_color="blue",
                                        tooltip="Edit",
                                        data=s,
                                        on_click=lambda e: edit_student(e.control.data),
                                    ),
                                    ft.IconButton(
                                        icon=ft.icons.DELETE,
                                        icon_color="red",
                                        tooltip="Delete",
                                        data=s[0],
                                        on_click=lambda e: delete_student(e.control.data),
                                    ),
                                ]
                            )
                        ),
                    ]
                )
            )
        page.update()

    # CRUD Operations
    def add_student(e):
        if not validate_fields():
            return
        
        try:
            # Step 1: Check the number of students already assigned to the room
            student_count_query = """
            SELECT COUNT(*) 
            FROM STUDENT 
            WHERE room_no = %s;
            """
            student_count = DatabaseManager.execute_query(student_count_query, (room_no.value,), fetch=True)
            
            # Step 2: Get the room's capacity
            room_capacity_query = """
            SELECT capacity 
            FROM ROOM 
            WHERE room_no = %s;
            """
            room_capacity = DatabaseManager.execute_query(room_capacity_query, (room_no.value,), fetch=True)

            # Step 3: Compare the current occupancy with room capacity
            if student_count and room_capacity:
                if student_count[0][0] >= room_capacity[0][0]:
                    # If room is full, show error message
                    show_snackbar(f"Room {room_no.value} is full. No available space.", "red")
                    return False

            # Step 4: Insert student if space is available
            insert_student_query = """
            INSERT INTO STUDENT (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """
            values = (student_id.value, name.value, course.value, mess_plan.value, laundry_plan.value, hostel_id.value, room_no.value)
            
            if DatabaseManager.execute_query(insert_student_query, values):
                show_snackbar(f"Student {name.value} added successfully!")
                return True
            else:
                show_snackbar("Failed to add student", "red")
                return False
        except Exception as e:
            show_snackbar(f"Error: {e}", "red")
            return False

    def edit_student(student_data):
        student_id.value = student_data[0]
        name.value = student_data[1]
        course.value = student_data[2]
        mess_plan.value = student_data[3]
        laundry_plan.value = student_data[4]
        hostel_id.value = student_data[5]
        room_no.value = student_data[6]

        # Update button will now act as "Save"
        page.update()

    def delete_student(student_id):
        confirmation = ft.AlertDialog(
            title=ft.Text("Delete Student?"),
            content=ft.Text(f"Are you sure you want to delete student {student_id}?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: page.close_alert_dialog()),
                ft.TextButton("Confirm", on_click=lambda e: confirm_delete(student_id)),
            ]
        )
        page.add(confirmation)
        page.update()

    def confirm_delete(student_id):
        result = Student.delete(student_id)
        if result:
            show_snackbar(f"Student {student_id} deleted successfully!")
            load_students()
        else:
            show_snackbar("Failed to delete student", "red")
        page.close_alert_dialog()

    load_students()

    # Action buttons
    add_button = ft.ElevatedButton("Add Student", on_click=add_student)

    page.add(
        student_id,
        name,
        course,
        mess_plan,
        laundry_plan,
        hostel_id,
        room_no,
        add_button,
        students_table,
    )
    page.update()
ft.app(target=main, view=ft.AppView.WEB_BROWSER)    