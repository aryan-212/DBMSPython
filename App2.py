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
            if Student.insert(
                student_id.value, name.value, course.value,
                mess_plan.value, laundry_plan.value,
                int(hostel_id.value), int(room_no.value)
            ):
                show_snackbar(f"Student {name.value} added successfully!")
                clear_fields()
                load_students()
            else:
                show_snackbar("Failed to add student", "red")
        except ValueError:
            show_snackbar("Invalid hostel ID or room number", "red")

    def edit_student(student_data):
        nonlocal current_student
        current_student = student_data
        student_id.value = student_data[0]
        name.value = student_data[1]
        course.value = student_data[2]
        mess_plan.value = student_data[3]
        laundry_plan.value = student_data[4]
        hostel_id.value = str(student_data[5])
        room_no.value = str(student_data[6])
        student_id.disabled = True
        add_button.visible = False
        update_button.visible = True
        page.update()

    def update_student(e):
        if not validate_fields():
            return
        
        try:
            if Student.update(
                student_id.value, name.value, course.value,
                mess_plan.value, laundry_plan.value,
                int(hostel_id.value), int(room_no.value)
            ):
                show_snackbar(f"Student {name.value} updated successfully!")
                clear_fields()
                student_id.disabled = False
                add_button.visible = True
                update_button.visible = False
                load_students()
            else:
                show_snackbar("Failed to update student", "red")
        except ValueError:
            show_snackbar("Invalid hostel ID or room number", "red")

    def delete_student(student_id_val):
        def confirm_delete(e):
            if Student.delete(student_id_val):
                show_snackbar("Student deleted successfully!")
                load_students()
            else:
                show_snackbar("Failed to delete student", "red")
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this student?"),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: setattr(dialog, 'open', False)),
                ft.TextButton("Delete", on_click=confirm_delete),
            ],
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    # Buttons
    add_button = ft.ElevatedButton(
        text="Add Student",
        on_click=add_student,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="blue",
            padding=20,
        ),
    )

    update_button = ft.ElevatedButton(
        text="Update Student",
        on_click=update_student,
        visible=False,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="green",
            padding=20,
        ),
    )

    # Layout
    page.add(
        ft.Column([
            ft.Container(
                content=ft.Text(
                    "Hostel Management System",
                    size=30,
                    weight="bold",
                ),
                padding=20,
            ),
            ft.Row(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                student_id,
                                name,
                                course,
                                mess_plan,
                                laundry_plan,
                                hostel_id,
                                room_no,
                                ft.Row(
                                    [add_button, update_button],
                                    alignment=ft.MainAxisAlignment.START,
                                ),
                            ],
                            spacing=20,
                        ),
                        padding=20,
                        border=ft.border.all(2, "grey"),
                        border_radius=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            ft.Container(
                content=students_table,
                padding=20,
            ),
        ])
    )

    # Initial load
    load_students()

if __name__ == "__main__":
    ft.app(target=main, view=ft.AppView.WEB_BROWSER)