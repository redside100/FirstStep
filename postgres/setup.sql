BEGIN;

CREATE TABLE Groups(
    id INT,
    name VARCHAR(64) NOT NULL,
    expire BIT NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE Users(
    id INT,
    group_id INT NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    student_id INT UNIQUE NOT NULL,
    program VARCHAR(3),
    avatar_url VARCHAR(2048),
    bio TEXT,
    software_rating FLOAT,
    leadership_rating FLOAT,
    database_rating FLOAT,
    writing_rating FLOAT,
    hardware_rating FLOAT,
    embedded_rating FLOAT,
    in_group BOOLEAN,
    intend_star BOOLEAN,
    join_date TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (group_id) REFERENCES Groups(id)
);

CREATE TABLE FYDPProjects(
    id INT,
    name VARCHAR(64),
    software_rating FLOAT,
    hardware_rating FLOAT,
    embedded_rating FLOAT,
    database_rating FLOAT,
    PRIMARY KEY (id)
);

COMMIT;