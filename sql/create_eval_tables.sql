-- CREATE DATABASE --

USE DATABASE monitor_db;

-- CREATE TABLES --
DROP TABLE IF EXISTS ampds;
CREATE TABLE ampds (
    stream VARCHAR(40),
    timestamp INTEGER,
    power FLOAT,
    anomaly INTEGER 
);

DROP TABLE IF EXISTS dataport;
CREATE TABLE dataport (
    stream VARCHAR(40),
    timestamp INTEGER,
    power FLOAT,
    anomaly INTEGER 
);

DROP TABLE IF EXISTS eco;
CREATE TABLE eco (
    stream VARCHAR(40),
    timestamp INTEGER,
    power FLOAT,
    anomaly INTEGER 
);

DROP TABLE IF EXISTS refit;
CREATE TABLE refit (
    stream VARCHAR(40),
    timestamp INTEGER,
    power FLOAT,
    anomaly INTEGER 
);

-- LOAD DATA --

LOAD DATA LOCAL INFILE "events/data/vector/eval/ampds.csv" INTO TABLE ampds FIELDS TERMINATED BY ",";
LOAD DATA LOCAL INFILE "events/data/vector/eval/dataport.csv" INTO TABLE dataport FIELDS TERMINATED BY ",";
LOAD DATA LOCAL INFILE "events/data/vector/eval/eco.csv" INTO TABLE eco FIELDS TERMINATED BY ",";
LOAD DATA LOCAL INFILE "events/data/vector/eval/refit.csv" INTO TABLE refit FIELDS TERMINATED BY ",";


CREATE INDEX ampds on ampds(stream);
CREATE INDEX dataport on dataport(stream);
CREATE INDEX eco on eco(stream);
CREATE INDEX refit on refit(stream);
