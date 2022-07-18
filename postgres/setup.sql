BEGIN;

CREATE TABLE Groups(
    id SERIAL PRIMARY KEY,
    group_name VARCHAR(64),
    expire INT NOT NULL,
    is_permanent BOOLEAN,
    creation_date TIMESTAMP
);

CREATE TABLE MatchRounds(
    id SERIAL PRIMARY KEY,
    current_status INT,
    next_status INT,
    last_updated TIMESTAMP,
    current_start TIMESTAMP,
    next_start TIMESTAMP,
    next_end TIMESTAMP
);

CREATE TABLE Skillsets(
    id SERIAL PRIMARY KEY,
    skill_name VARCHAR(64),
    skill_description TEXT,
    skill_type INT
);

CREATE TABLE Programs(
    id SERIAL PRIMARY KEY,
    code VARCHAR(10),
    program_name VARCHAR(64)
);

CREATE TABLE Users(
    id SERIAL PRIMARY KEY,
    email VARCHAR(128),
    class_year INT,
    group_id INT NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    student_id INT UNIQUE NOT NULL,
    program_id INT NOT NULL,
    skills_id INT NOT NULL,
    match_round_id INT NOT NULL,
    avatar_url VARCHAR(2048),
    bio TEXT,
    display_name VARCHAR(128),
    FOREIGN KEY (group_id) REFERENCES Groups(id),
    FOREIGN KEY (program_id) REFERENCES Programs(id),
    FOREIGN KEY (skills_id) REFERENCES Skillsets(id),
    FOREIGN KEY (match_round_id) REFERENCES MatchRounds(id)
);

CREATE TABLE UserSkills(
    user_rating INT NOT NULL,
    user_id INT,
    skill_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (skill_id) REFERENCES Skillsets(id)
);

CREATE TABLE FYDPProjects(
    id SERIAL PRIMARY KEY,
    project_name VARCHAR(64),
    project_description TEXT,
    software_rating FLOAT,
    hardware_rating FLOAT,
    embedded_rating FLOAT,
    database_rating FLOAT,
    writing_rating FLOAT,
    leadership_rating FLOAT,
    image_url TEXT,
    project_type INT
);

INSERT INTO 
    Skillsets (skill_name, skill_description, skill_type) 
VALUES
    ('Embedded Software', 'Embedded software is a piece of software that is embedded in hardware or non-PC devices.', 0),
    ('Distributed Systems', 'A distributed system is a computing environment in which various components are spread across multiple computers (or other computing devices) on a network.', 0),
    ('Database Systems', 'A database typically requires a comprehensive database software program known as a database management system (DBMS).', 0),
    ('Hardware', 'Computer hardware includes the physical parts of a computer, such as the case, central processing unit (CPU), random access memory (RAM).', 0),
    ('Leadership', 'Leadership is the ability of an individual or a group of individuals to influence and guide followers or other members of an organization.', 0),
    ('Technical Writing', 'Technical writing is any writing designed to explain complex, technical, and specialized information to audiences who may or may not be familiar with them.', 0);

INSERT INTO 
    Programs (code, program_name)
VALUES 
    ('CE', 'Computer Engineering'),
    ('EE', 'Electrical Engineering'),
    ('SE', 'Software Engineering');

COMMIT;