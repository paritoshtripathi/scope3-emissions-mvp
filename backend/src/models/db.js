const { Pool } = require('pg');

const pool = new Pool({
    user: process.env.POSTGRES_USER || 'postgres',
    host: process.env.POSTGRES_HOST || 'postgres',  // Use Docker service name
    database: process.env.POSTGRES_DB || 'scope3',
    password: process.env.POSTGRES_PASSWORD || 'P@ssw0rd',
    port: parseInt(process.env.POSTGRES_PORT || '5433', 10),  // Use standard Postgres port
});

// Add error handling
pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err);
    process.exit(-1);
});

module.exports = pool;