-- CREATE DATABASE --

USE monitor_db;

-- CREATE TABLES --
DROP TABLE IF EXISTS aniyama;
CREATE TABLE aniyama (
    stream VARCHAR(40) NOT NULL,
    timestamp INTEGER,
    value FLOAT,
    anomaly INTEGER,
    type ENUM('ampds', 'dataport', 'eco', 'refit') NOT NULL
);


-- LOAD DATA --

LOAD DATA LOCAL INFILE "events/data/vector/aniyama/aniyama_data.csv" INTO TABLE aniyama FIELDS TERMINATED BY ",";

CREATE INDEX aniyama on aniyama(stream, type);
