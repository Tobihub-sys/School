import sqlite3
from datetime import datetime

DB_FILE = "school.db"

def create_database():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_number INTEGER PRIMARY KEY,
                name TEXT,
                nickname TEXT,
                age INTEGER,
                grade INTEGER,
                registration_date TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                student_number INTEGER,
                lesson_name TEXT,
                FOREIGN KEY (student_number) REFERENCES students (student_number) ON DELETE CASCADE
            )
        ''')

        conn.commit()

def get_int_input(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def get_validated_input(prompt, is_text=True, is_date=False):
    while True:
        user_input = input(prompt)
        if is_text and not user_input.isdigit():
            return user_input
        elif not is_text and user_input.isdigit():
            return user_input
        elif is_date:
            try:
                # Attempt to convert the input to a datetime object
                datetime.strptime(user_input, "%Y-%m-%d")
                return user_input
            except ValueError:
                print("Invalid date format. Please enter a valid date (YYYY-MM-DD).")
        elif not is_text and not user_input:
            # Allow empty input for non-text fields (e.g., Enter to finish entering lesson name)
            return user_input
        print("Invalid input. Please enter a valid value.")

def add_student():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        student_number = get_int_input("Enter student number: ")
        name = get_validated_input("Enter name: ")
        nickname = get_validated_input("Enter nickname: ")
        age = get_int_input("Enter age: ")
        grade = get_int_input("Enter grade: ")
        registration_date = get_validated_input("Enter registration date (YYYY-MM-DD): ", is_date=True)

        cursor.execute('''
            INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_number, name, nickname, age, grade, registration_date))

        while True:
            lesson_name = get_validated_input("Enter lesson name (Press Enter to finish): ", False)
            if not lesson_name:
                break
            cursor.execute('''
                INSERT INTO lessons VALUES (?, ?)
            ''', (student_number, lesson_name))

        print("Student added successfully.")
        conn.commit()

def delete_student():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        student_number = int(input("Enter student number to delete: "))

        # Check if the student exists
        cursor.execute('SELECT 1 FROM students WHERE student_number = ?', (student_number,))
        existing_student = cursor.fetchone()

        if existing_student is None:
            print("Student not found.")
            return

        try:
            conn.execute('BEGIN TRANSACTION')

            cursor.execute('''
                DELETE FROM lessons WHERE student_number = ?
            ''', (student_number,))

            cursor.execute('''
                DELETE FROM students WHERE student_number = ?
            ''', (student_number,))

            print("Student deleted successfully.")
            conn.commit()

        except Exception as e:
            print(f"Error deleting student: {e}")
            conn.rollback()

def update_student():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        student_number = int(input("Enter student number to update: "))

        cursor.execute('''
            SELECT * FROM students WHERE student_number = ?
        ''', (student_number,))
        existing_student = cursor.fetchone()

        if existing_student is None:
            print("Student not found.")
            return

        name = input(f"Enter new name (Press Enter to keep current name: {existing_student[1]}): ")
        nickname = input(f"Enter new nickname (Press Enter to keep current nickname: {existing_student[2]}): ")
        age = int(input(f"Enter new age (Press Enter to keep current age: {existing_student[3]}): "))
        grade = int(input(f"Enter new grade (Press Enter to keep current grade: {existing_student[4]}): "))
        registration_date = input(f"Enter new registration date (Press Enter to keep current date: {existing_student[5]}): ")
        lesson_name = input("Enter new lesson name (Press Enter to keep current date): ")

        try:
            conn.execute('BEGIN TRANSACTION')

            cursor.execute('''
                UPDATE students
                SET name = COALESCE(?, name),
                    nickname = COALESCE(?, nickname),
                    age = COALESCE(?, age),
                    grade = COALESCE(?, grade),
                    registration_date = COALESCE(?, registration_date)
                WHERE student_number = ?
            ''', (name, nickname, age, grade, registration_date, student_number))

            cursor.execute('''
                UPDATE lessons
                SET lesson_name = COALESCE(?, lesson_name)
                WHERE student_number = ?
            ''', (lesson_name, student_number))

            print("Student updated successfully.")
            conn.commit()

        except Exception as e:
            print(f"Error updating student: {e}")
            conn.rollback()

def view_student():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        student_number = int(input("Enter student number to view: "))

        cursor.execute('''
            SELECT * FROM students WHERE student_number = ?
        ''', (student_number,))
        existing_student = cursor.fetchone()

        if existing_student is None:
            print("Student not found.")
            return

        print("\nStudent Information:")
        print(f"Student Number: {existing_student[0]}")
        print(f"Name: {existing_student[1]}")
        print(f"Nickname: {existing_student[2]}")
        print(f"Age: {existing_student[3]}")
        print(f"Grade: {existing_student[4]}")
        print(f"Registration Date: {existing_student[5]}")

        cursor.execute('''
            SELECT lesson_name FROM lessons WHERE student_number = ?
        ''', (student_number,))
        lessons = cursor.fetchall()

        if lessons:
            print("\nLessons:")
            for lesson in lessons:
                print(lesson[0])

# Main program loop
create_database()

while True:
    print("\nPlease choose the operation you want to perform:")
    print("* To add a student, press the letter a")
    print("* To delete a student, press the letter d")
    print("* To modify a student’s information, press the letter u")
    print("* To view student information, press the letter s")
    print("* To exit, press the letter x")

    choice = input("Your choice: ")

    if choice.lower() == 'a':
        add_student()
    # Add similar modifications for other operations
    elif choice.lower() == 'd':
        delete_student()
    elif choice.lower() == 'u':
        update_student()
    elif choice.lower() == 's':
        view_student()
    elif choice.lower() == 'x':
        break
    else:
        print("Invalid choice. Please try again.")

        
