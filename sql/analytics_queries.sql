-- Overall portal summary
SELECT
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM sports_programs) AS total_programs,
    (SELECT COUNT(*) FROM enrollments) AS total_enrollments,
    (SELECT SUM(capacity) FROM sports_programs) AS total_capacity,
    (SELECT SUM(enrolled_count) FROM sports_programs) AS total_filled;

-- Program utilization
SELECT
    name,
    category,
    capacity,
    enrolled_count,
    ROUND((enrolled_count * 100.0) / capacity, 2) AS occupancy_rate
FROM sports_programs
ORDER BY occupancy_rate DESC;

-- Category-level demand
SELECT
    category,
    COUNT(*) AS program_count,
    SUM(capacity) AS total_capacity,
    SUM(enrolled_count) AS total_enrollments
FROM sports_programs
GROUP BY category
ORDER BY total_enrollments DESC;

-- Student-wise enrollment report
SELECT
    u.full_name,
    u.student_id,
    s.name AS program_name,
    s.category,
    e.enrollment_status,
    e.enrolled_on
FROM enrollments e
JOIN users u ON u.id = e.user_id
JOIN sports_programs s ON s.id = e.program_id
ORDER BY e.enrolled_on DESC;

