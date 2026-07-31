CREATE TABLE Hotels (
    hotel_id INT PRIMARY KEY,
    hotel_name VARCHAR(100),
    city VARCHAR(50),
    address VARCHAR(255),
    phone VARCHAR(20)
);
CREATE TABLE Guests (
    guest_id INT PRIMARY KEY,
    full_name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    nationality VARCHAR(50),
    loyalty_level VARCHAR(20)
);
