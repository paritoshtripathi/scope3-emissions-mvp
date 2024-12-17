const express = require('express');
const cors = require('cors'); // Import the CORS middleware
const pool = require('./src/models/db'); // Import PostgreSQL connection
const rasaRoutes = require('./src/routes/rasa'); // Import Rasa routes
const langchainRoutes = require("./src/routes/langchain"); // Import Langchain routes
const dataRoutes = require("./src/routes/data"); // Import Data Ingestion routes

const app = express();

// Allow CORS for all origins (for development purposes)
app.use(cors());

// Parse JSON requests
app.use(express.json());

// Root route
app.get("/", (req, res) => res.send("Scope 3 Backend API is running!"));

// Sample data route (Frontend integration)
app.use('/api', require('./src/routes/sample'));

// AI/ML routes for testing the microservice
app.use('/api/ai-ml', require('./src/routes/ai-ml')); 

// Rasa route for chatbot integration
app.use('/api/rasa', rasaRoutes);

// Langchain route for chatbot integration
app.use("/langchain", langchainRoutes);

// Data ingestion route
app.use('/api/data', dataRoutes);


// Add a database test route
app.get('/db-test', async (req, res) => {
    try {
        const result = await pool.query('SELECT NOW()'); // Test query
        res.json({ success: true, timestamp: result.rows[0].now });
    } catch (error) {
        console.error('Database connection error:', error.message);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Start the server
app.listen(3000, () => {
    console.log('Backend running on port 3000');
});

module.exports = app;
