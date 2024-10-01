DROP DATABASE IF EXISTS alarm_db;
CREATE DATABASE alarm_db
DEFAULT CHARACTER SET utf8
DEFAULT COLLATE utf8_general_ci;
USE alarm_db;

CREATE TABLE users
(
    id int NOT NULL AUTO_INCREMENT,
    u_login bigint not null unique,
    u_passhash varchar(256) not null,
    u_name varchar(256),
    CONSTRAINT PK_users PRIMARY KEY(id)
);

CREATE TABLE sessions
(
    id int not null AUTO_INCREMENT,
    user_id int,
    aes_iv varchar(256),
    aes_key varchar(2410),
    date_last_conn datetime,
    CONSTRAINT PK_sessions PRIMARY KEY (id)
);




