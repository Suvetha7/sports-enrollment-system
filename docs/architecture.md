# Architecture Overview

## System Flow

```mermaid
flowchart LR
    A["Student / Admin"] --> B["Web UI"]
    B --> C["Python HTTP Server"]
    C --> D["Validation Layer"]
    D --> E["Transaction + Enrollment Service"]
    E --> F["SQLite Demo DB / MySQL Deployment DB"]
    F --> G["Analytics Queries"]
    G --> B
```

## Database Design

```mermaid
erDiagram
    USERS ||--o{ ENROLLMENTS : registers
    SPORTS_PROGRAMS ||--o{ ENROLLMENTS : receives

    USERS {
        int id PK
        string full_name
        string email UK
        string student_id UK
        string phone
        string password_hash
    }

    SPORTS_PROGRAMS {
        int id PK
        string name
        string category
        string coach_name
        int capacity
        int enrolled_count
        string schedule
        int fee
        string skill_level
        string status
    }

    ENROLLMENTS {
        int id PK
        int user_id FK
        int program_id FK
        string enrollment_status
        string notes
        datetime enrolled_on
    }
```

## Concurrency Strategy

- Enrollment writes use a transaction boundary.
- Seat count is checked before insertion.
- Enrollment and seat update happen in the same atomic unit.
- Duplicate enrollment is blocked by logic and uniqueness rules.

