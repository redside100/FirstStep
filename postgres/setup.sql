BEGIN;

CREATE TABLE Groups(
    id SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    expire INT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Users(
    id SERIAL PRIMARY KEY ,
    group_id INT NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    student_id INT UNIQUE NOT NULL,
    program VARCHAR(10),
    avatar_url VARCHAR(2048),
    bio TEXT,
    software_rating FLOAT,
    leadership_rating FLOAT,
    database_rating FLOAT,
    writing_rating FLOAT,
    hardware_rating FLOAT,
    embedded_rating FLOAT,
    in_group BOOLEAN,
    intend_stay BOOLEAN,
    join_date TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES Groups(id)
);

CREATE TABLE FYDPProjects(
    id SERIAL PRIMARY KEY,
    name VARCHAR(64),
    description TEXT,
    software_rating FLOAT,
    hardware_rating FLOAT,
    embedded_rating FLOAT,
    database_rating FLOAT,
    writing_rating FLOAT,
    leadership_rating FLOAT,
);

COMMIT;