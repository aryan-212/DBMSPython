CREATE TABLE IF NOT EXISTS HOSTEL (
    hostel_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS ROOM (
    room_no INT PRIMARY KEY,
    capacity INT,
    type VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS STUDENT (
    student_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    course VARCHAR(100),
    mess_plan VARCHAR(50),
    laundry_plan VARCHAR(50),
    hostel_id INT,
    room_no INT,
    FOREIGN KEY (hostel_id) REFERENCES HOSTEL(hostel_id),
    FOREIGN KEY (room_no) REFERENCES ROOM(room_no)
);

CREATE TABLE IF NOT EXISTS FEE (
    fee_id VARCHAR(10) PRIMARY KEY,
    amount FLOAT,
    status VARCHAR(50),
    due_date DATE
);

CREATE TABLE IF NOT EXISTS EMPLOYEE (
    emp_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(255),
    activity VARCHAR(100),
    service VARCHAR(100),
    shift VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS HOSTEL_SERVICE (
    service_id VARCHAR(10) PRIMARY KEY,
    service_type VARCHAR(100),
    details TEXT
);
