-- Migration: add ExHave / ExWant for existing databases
-- Fresh installs already get these from schema.sql

CREATE TABLE IF NOT EXISTS ex_have (
    student_id  TEXT PRIMARY KEY REFERENCES student (student_id) ON DELETE CASCADE,
    charm       TEXT
);

CREATE TABLE IF NOT EXISTS ex_want (
    student_id  TEXT PRIMARY KEY REFERENCES student (student_id) ON DELETE CASCADE,
    charm       TEXT
);
