const { Pool } = require('pg');

const pool = new Pool({
    user: process.env.POSTGRES_USER || 'postgres',
    host: process.env.POSTGRES_HOST || 'localhost',
    database: process.env.POSTGRES_DB || 'scope3',
    password: process.env.POSTGRES_PASSWORD || 'P@ssw0rd',
    port: 5433,
});

module.exports = pool;