
CREATE ROLE postgres WITH LOGIN PASSWORD 'password';
CREATE DATABASE scope3 OWNER postgres;

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tenant_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE emissions_data (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    emission_type VARCHAR(50) NOT NULL, -- e.g., CO2, NOx
    value DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL, -- e.g., kg, tonnes
    recorded_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
