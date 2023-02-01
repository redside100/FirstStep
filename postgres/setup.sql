BEGIN;

CREATE TABLE Groups(
    id SERIAL PRIMARY KEY,
    name VARCHAR(64),
    is_group_permanent BOOLEAN,
    date_of_creation TIMESTAMP
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
    name VARCHAR(64),
    description TEXT,
    response_required BOOLEAN,
    type INT
);

CREATE TABLE Programs(
    id SERIAL PRIMARY KEY,
    code VARCHAR(10),
    name VARCHAR(64)
);

CREATE TABLE Preferences(
    id SERIAL PRIMARY KEY,
    name VARCHAR(2048),
    description TEXT,
    image_url TEXT,
    type INT,
    response_required BOOLEAN
);


CREATE TABLE Users(
    id SERIAL PRIMARY KEY,
    email VARCHAR(128),
    class_year INT,
    group_id INT,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    program_id INT,
    match_round_id INT,
    avatar_url VARCHAR(2048),
    bio TEXT,
    display_name VARCHAR(128),
    FOREIGN KEY (group_id) REFERENCES Groups(id) ON DELETE SET NULL,
    FOREIGN KEY (program_id) REFERENCES Programs(id) ON DELETE SET NULL,
    FOREIGN KEY (match_round_id) REFERENCES MatchRounds(id) ON DELETE SET NULL
);

CREATE TABLE UserAuth(
    user_id INT,
    h_password VARCHAR(128),
    FOREIGN KEY(user_id) REFERENCES Users(id)
);

CREATE TABLE UserSkills(
    rating FLOAT NOT NULL,
    user_id INT,
    skill_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES Skillsets(id) ON DELETE CASCADE
);

CREATE TABLE UserPreferences(
    preferred BOOLEAN,
    user_id INT,
    preference_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY (preference_id) REFERENCES Preferences(id) ON DELETE CASCADE
);

CREATE TABLE UserOnboarding(
    user_id INT,
    onboarding_status INT,
    is_verified BOOLEAN,
    is_eligible BOOLEAN
);

INSERT INTO 
    Skillsets (name, description, response_required, type)
VALUES 
    ('Embedded Software', 'Embedded software is a piece of software that is embedded in hardware or non-PC devices.', TRUE, 0),
    ('Distributed Systems', 'A distributed system is a computing environment in which various components are spread across multiple computers (or other computing devices) on a network.', TRUE, 0),
    ('Database Systems', 'A database typically requires a comprehensive database software program known as a database management system (DBMS).', TRUE, 0),
    ('Hardware', 'Computer hardware includes the physical parts of a computer, such as the case, central processing unit (CPU), random access memory (RAM).', TRUE, 0),
    ('Leadership', 'Leadership is the ability of an individual or a group of individuals to influence and guide followers or other members of an organization.', TRUE, 0),
    ('Technical Writing', 'Technical writing is any writing designed to explain complex, technical, and specialized information to audiences who may or may not be familiar with them.', TRUE, 0);

INSERT INTO
    Preferences(name, description, image_url, type, response_required)
VALUES
    ('Goldilocks: Consumer Electronics Comparator and Price Tracker', 'A growing share of consumer electronics sales are being conducted online. However, comparing products across different online retailers can be difficult. The objective of this project is to consolidate information across major retailers into one platform, making online shopping simpler and saving time, money, and effort. The benefit of this project is that it puts an emphasis on comparison of similar products within the same electronics category so as to allow consumers to shop for electronics when they are undecided on a particular product.', 'https://www.eng.uwaterloo.ca/2021-capstone-design/software/__@_@__images@_/software1_team-photo.55dda2fb4f26.png', 2, TRUE),
    ('EyeGuide: Smart Cane for the Visually Impaired', '"C500,000 Canadians are estimated to be affected by sight loss, and have difficulty navigating unfamiliar spaces. The objective of EyeGuide is to attach an embedded device onto a traditional white cane. This system is responsible for detecting and identifying nearby objects, providing navigation assistance and providing location sharing. The main advantage of EyeGuide is that it provides more information to the blind than the traditional white cane and does not require training unlike guide dogs.', 'https://www.eng.uwaterloo.ca/2021-capstone-design/software/__@_@__images@_/software1_team-photo.55dda2fb4f26.png', 2, TRUE),
    ('Tutorr', 'Market research has shown a rising demand in tutoring services as the percentage of students meeting provincial standards continue to decrease year-by-year. To address this, a crowd-sourced platform for private tutoring services that promotes personal engagement and immediate feedback has been created. With Tutorr, students are matched with mentors within their geographical location that possess relevant subject expertise, and a full-scale application integrated with payment services and live-chat is used to facilitate this experience seamlessly and efficiently.', NULL, 2, TRUE);

INSERT INTO 
    Programs (code, name)
VALUES 
    ('CE', 'Computer Engineering'),
    ('EE', 'Electrical Engineering'),
    ('SE', 'Software Engineering');

INSERT INTO
    MatchRounds (current_status, next_status, last_updated, current_start, next_start, next_end)
VALUES
    (5, 5, '2020-1-11 05:00:00', '2020-1-11 05:00:00', NULL, NULL),
    (5, 5, '2020-1-11 05:00:00', '2020-1-11 05:00:00', '2022-12-22 12:30:00', '2022-12-25 12:30:00');

COMMIT;