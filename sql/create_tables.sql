-- CREATE DATABASE --

DROP DATABASE IF EXISTS monitor_db;
CREATE DATABASE monitor_db;
USE monitor_db;

-- CREATE TABLES --

CREATE TABLE mapping (
	id INTEGER,
	true_type VARCHAR(4000)
);

CREATE TABLE ground_truth (
	source VARCHAR(40),
	name VARCHAR(100),
	true_type INTEGER
);

CREATE TABLE streams (
	stream VARCHAR(100),
	timestamp INTEGER,
	value FLOAT,
	event INTEGER
);

CREATE TABLE stream_attributes (
	stream VARCHAR(100),
	attribute_text VARCHAR(8000)
);

CREATE TABLE attribute_index (
	attribute VARCHAR(100),
	stream VARCHAR(100),
	value VARCHAR(100)
);

CREATE TABLE attribute_extension (
	attribute VARCHAR(100),
	attribute_text VARCHAR(8000)
);

CREATE TABLE attribute_alias (
    attribute VARCHAR(100),
    text VARCHAR(100),
    operator VARCHAR(100),
    value VARCHAR(100),
    UNIQUE(text)
);

-- LOAD DATA --

LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/class_mapping.csv" INTO TABLE mapping FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/rice_ground_truth.csv" INTO TABLE ground_truth FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/sdh_ground_truth.csv" INTO TABLE ground_truth FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/soda_ground_truth.csv" INTO TABLE ground_truth FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/stream_attributes.csv" INTO TABLE stream_attributes FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/extra_stream_attributes.csv" INTO TABLE stream_attributes FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/attribute_index.csv" INTO TABLE attribute_index FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/attribute_extension.csv" INTO TABLE attribute_extension FIELDS TERMINATED BY "|";
LOAD DATA LOCAL INFILE "~/CS/UCSD/Research/Data-Mining-Lab/Monitor/sql/sample_data/data.csv" INTO TABLE streams FIELDS TERMINATED BY ",";

-- DATA BASED TABLES --

CREATE TABLE stream_type_attributes (
	SELECT
		c.source,
		a.stream,
		b.true_type,
		a.attribute_text
	FROM 
		stream_attributes as a,
		mapping as b,
		ground_truth as c
	WHERE
		a.stream = c.name AND
		c.true_type = b.id
);

CREATE TABLE max_timestamps (
    SELECT
        DISTINCT stream,
        MAX(timestamp) as timestamp
    FROM
        streams
    GROUP BY
        stream
);

-- CREATE VIEWS --

CREATE VIEW stream_data AS (
	SELECT
		b.source,
		c.stream as name,
		b.true_type,
		b.attribute_text,
		c.timestamp,
		c.value,
		c.event
	FROM
		stream_type_attributes as b,
		streams as c
	WHERE
		b.stream = c.stream
);

CREATE VIEW attribute_data AS (
	SELECT 
		a.stream,
		a.attribute,
		a.value,
		b.attribute_text
	FROM
		attribute_index AS a,
		attribute_extension AS b
	WHERE 
		a.attribute = b.attribute
);

CREATE VIEW all_data AS (
    SELECT
        a.name as stream, 
        a.source,
        a.timestamp,
        a.value,
        a.event,
        b.attribute,
        b.value as attribute_value,
        b.attribute_text
    FROM
        stream_data as a,
        attribute_data as b
    WHERE
        a.name = b.stream
);

-- CREATE INDEXES --

CREATE INDEX stream_name_timestamp ON streams(stream, timestamp);
CREATE INDEX attribute_text_index on attribute_index(stream);
CREATE INDEX attribute_value_index on attribute_index(value);
ALTER TABLE stream_type_attributes ADD FULLTEXT INDEX (source, stream, true_type, attribute_text);
ALTER TABLE attribute_extension ADD FULLTEXT INDEX (attribute_text);
