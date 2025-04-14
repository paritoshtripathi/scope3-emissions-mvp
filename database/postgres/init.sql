
--CREATE ROLE postgres WITH LOGIN PASSWORD 'password';
--CREATE DATABASE scope3 OWNER postgres;

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    tenant_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS  emissions_data (
    id SERIAL PRIMARY KEY,
    category VARCHAR(255), -- e.g., "Employee Commuting"
    source_type VARCHAR(255), -- e.g., "Diesel Vehicles"
    current_emissions FLOAT, -- CO2 in tons
    potential_reduction FLOAT, -- CO2 in tons
    reduction_strategy VARCHAR(255), -- e.g., "Switch to EVs"
    predicted_emissions FLOAT, -- Projected emissions after reduction
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ingestion_log (
  id SERIAL PRIMARY KEY,
  filename TEXT NOT NULL,
  source TEXT,
  upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

