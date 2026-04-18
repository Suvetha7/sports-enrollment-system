CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    student_id VARCHAR(40) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sports_programs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(80) NOT NULL,
    coach_name VARCHAR(120) NOT NULL,
    capacity INT NOT NULL,
    enrolled_count INT NOT NULL DEFAULT 0,
    schedule VARCHAR(120) NOT NULL,
    fee INT NOT NULL DEFAULT 0,
    skill_level VARCHAR(40) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enrollments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    program_id INT NOT NULL,
    enrollment_status VARCHAR(30) NOT NULL DEFAULT 'Confirmed',
    notes TEXT,
    enrolled_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_program UNIQUE (user_id, program_id),
    CONSTRAINT fk_enrollments_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_enrollments_program FOREIGN KEY (program_id) REFERENCES sports_programs(id) ON DELETE CASCADE
);

CREATE TABLE audit_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    action_type VARCHAR(60) NOT NULL,
    actor_email VARCHAR(120),
    details TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

