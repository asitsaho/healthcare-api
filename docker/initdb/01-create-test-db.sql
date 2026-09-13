-- Creates a separate database for the test suite so tests never touch
-- the development database. Runs automatically on first container start.
CREATE DATABASE healthcare_api_test OWNER healthcare;
