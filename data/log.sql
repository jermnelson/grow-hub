CREATE TABLE Activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name VARCHAR NOT NULL
);

CREATE TABLE ActivityLog (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    activity INTEGER NOT NULL,
    plant INTEGER NOT NULL,
    taken DATETIME DEFAULT CURRENT_TIMESTAMP,
    description VARCHAR,
    FOREIGN KEY (activity) REFERENCES Activity,
    FOREIGN KEY (plant) REFERENCES Plant
);

CREATE TABLE Plant (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    iri VARCHAR NOT NULL
);

INSERT INTO Activity (name) VALUES ("watering");
INSERT INTO Activity (name) VALUES ("pruning");
INSERT INTO Activity (name) VALUES ("moving");