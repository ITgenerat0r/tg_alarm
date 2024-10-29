DROP DATABASE IF EXISTS alarm_db;
CREATE DATABASE alarm_db
DEFAULT CHARACTER SET utf8
DEFAULT COLLATE utf8_general_ci;
USE alarm_db;

CREATE TABLE users
(
    u_login bigint not null unique,
    u_passhash varchar(256) not null,
    u_name varchar(256),
    CONSTRAINT PK_users PRIMARY KEY(u_login)
);

CREATE TABLE sessions
(
    id int not null AUTO_INCREMENT,
    user_id bigint,
    aes_iv varchar(256),
    aes_key varchar(2410),
    date_last_conn datetime,
    CONSTRAINT PK_sessions PRIMARY KEY (id),
    KEY IDX_USER (id),
    CONSTRAINT FK_sessions FOREIGN KEY(user_id) REFERENCES users(u_login)
    ON UPDATE CASCADE
);


CREATE TABLE online
(
    id int not null AUTO_INCREMENT,
    mac varchar(64) not null unique,
    short_name varchar(256),
    date_last_conn datetime,
    CONSTRAINT PK_online PRIMARY KEY (id)
);




CREATE TABLE o_u_bonds
(
    id int not null AUTO_INCREMENT,
    mac varchar(32) not null,
    user_id bigint not null,
    CONSTRAINT PK_ou_bonds PRIMARY KEY (id),

    -- CONSTRAINT FK_bonds FOREIGN KEY(mac) REFERENCES online(mac)
    -- ON UPDATE CASCADE,

    CONSTRAINT FK_bonds FOREIGN KEY(user_id) REFERENCES users(u_login)
    ON UPDATE CASCADE
);



