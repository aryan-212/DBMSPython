-- Ensure tables are dropped if they exist
DROP TABLE IF EXISTS STUDENT;
DROP TABLE IF EXISTS ROOM;
DROP TABLE IF EXISTS FEE;
DROP TABLE IF EXISTS EMPLOYEE;
DROP TABLE IF EXISTS HOSTEL_SERVICE;
DROP TABLE IF EXISTS HOSTEL;
DROP TABLE IF EXISTS ROOM_OCCUPANCY;

-- Create the tables again
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
    FOREIGN KEY (hostel_id) REFERENCES HOSTEL(hostel_id) ON DELETE SET NULL,
    FOREIGN KEY (room_no) REFERENCES ROOM(room_no) ON DELETE SET NULL
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
    service VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS HOSTEL_SERVICE (
    service_id VARCHAR(10) PRIMARY KEY,
    service_type VARCHAR(100),
    details TEXT
);

CREATE TABLE IF NOT EXISTS ROOM_OCCUPANCY (
    room_no INT PRIMARY KEY,
    current_occupancy INT DEFAULT 0,
    FOREIGN KEY (room_no) REFERENCES ROOM(room_no)
);

INSERT INTO ROOM_OCCUPANCY (room_no, current_occupancy)
SELECT room_no, 0 FROM ROOM;

-- Update ROOM_OCCUPANCY table with correct occupancy count
UPDATE ROOM_OCCUPANCY ro
JOIN STUDENT s ON ro.room_no = s.room_no
SET ro.current_occupancy = (
    SELECT COUNT(*) 
    FROM STUDENT 
    WHERE room_no = ro.room_no
);


DELIMITER //

CREATE TRIGGER after_student_insert
AFTER INSERT ON STUDENT
FOR EACH ROW
BEGIN
    UPDATE ROOM_OCCUPANCY 
    SET current_occupancy = current_occupancy + 1
    WHERE room_no = NEW.room_no;
END //

-- Create trigger to update room occupancy after student delete
CREATE TRIGGER after_student_delete
AFTER DELETE ON STUDENT
FOR EACH ROW
BEGIN
    UPDATE ROOM_OCCUPANCY 
    SET current_occupancy = current_occupancy - 1
    WHERE room_no = OLD.room_no;
END //

DELIMITER ;

-- Initial population of ROOM_OCCUPANCY table
DELIMITER //

CREATE PROCEDURE get_fee_details()
BEGIN
    SELECT f.*, s.name AS student_name
    FROM FEE f
    JOIN STUDENT s 
    ON f.fee_id = CONCAT('F', LPAD(SUBSTRING(s.student_id, 2), 3, '0'));
END //

DELIMITER ;

-- Insert sample data
INSERT INTO HOSTEL (name) VALUES 
('Alpha Hostel'),
('Beta Hostel'),
('Gamma Hostel');

INSERT INTO ROOM (room_no, capacity, type) VALUES 
(101, 2, 'Double'),
(102, 1, 'Single'),
(103, 4, 'Dormitory'),
(201, 3, 'Triple'),
(202, 2, 'Double');

INSERT INTO STUDENT (student_id, name, course, mess_plan, laundry_plan, hostel_id, room_no) VALUES 
('S001', 'Alice Brown', 'Engineering', 'Standard', 'Basic', 1, 101),
('S002', 'Bob Smith', 'Arts', 'Premium', 'Standard', 1, 102),
('S003', 'Charlie Davis', 'Science', 'Standard', 'Basic', 2, 103),
('S004', 'Daisy Johnson', 'Engineering', 'Premium', 'Premium', 3, 201),
('S005', 'Evan Lee', 'Medicine', 'Standard', 'Standard', 2, 202);

INSERT INTO FEE (fee_id, amount, status, due_date) VALUES 
('F001', 500.0, 'Paid', '2023-05-10'),
('F002', 750.0, 'Pending', '2023-06-15'),
('F003', 600.0, 'Paid', '2023-07-20'),
('F004', 800.0, 'Overdue', '2023-08-25'),
('F005', 700.0, 'Pending', '2023-09-30');

INSERT INTO EMPLOYEE (emp_id, name, activity, service) VALUES 
('E001', 'John Doe', 'Cleaning', 'Housekeeping'),
('E002', 'Anna White', 'Cooking', 'Cafeteria'),
('E003', 'Rick Green', 'Security', 'Guarding'),
('E004', 'Mary Black', 'Maintenance', 'Plumbing'),
('E005', 'Tom Grey', 'Admin', 'Reception');

INSERT INTO HOSTEL_SERVICE (service_id, service_type, details) VALUES 
('SVC001', 'Wi-Fi', 'High-speed internet access available throughout the hostel'),
('SVC002', 'Laundry', 'Self-service laundry facility'),
('SVC003', 'Housekeeping', 'Daily room cleaning services'),
('SVC004', 'Security', '24/7 CCTV and security guard service'),
('SVC005', 'Cafeteria', 'Cafeteria provides three meals a day');

-- Create trigger to update room occupancy after student insert
-- Insert initial data into ROOM_OCCUPANCY if it's empty
INSERT INTO ROOM_OCCUPANCY (room_no, current_occupancy)
SELECT room_no, 0 FROM ROOM;

-- Update ROOM_OCCUPANCY table with correct occupancy count
UPDATE ROOM_OCCUPANCY ro
JOIN STUDENT s ON ro.room_no = s.room_no
SET ro.current_occupancy = (
    SELECT COUNT(*) 
    FROM STUDENT 
    WHERE room_no = ro.room_no
);

-- Insert initial data into ROOM_OCCUPANCY if it's empty
