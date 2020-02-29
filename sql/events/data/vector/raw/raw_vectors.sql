USE monitor_db;

DROP TABLE IF EXISTS raw_vectors;

CREATE TABLE raw_vectors(
	name VARCHAR(100),
	start INTEGER,
	end INTEGER
);

LOAD DATA LOCAL INFILE "/home/akshat/Documents/School/Semester_4/Thesis/UVAMonitor/sql/events/data/vector/raw_vectors.csv" INTO TABLE raw_vectors FIELDS TERMINATED BY ",";

