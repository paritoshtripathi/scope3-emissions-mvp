const express = require('express');
const cors = require('cors');
const swaggerJsdoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');
const pool = require('./src/models/db');
const dataRoutes = require("./src/routes/dataIngest");
const authroutes = require('./src/routes/auth');
const aimlroutes = require('./src/routes/ai-ml');
const ragRoutes = require('./src/routes/rag');

const app = express();

// Swagger definition
const swaggerOptions = {
    definition: {
        openapi: '3.0.0',
        info: {
            title: 'Scope3 Backend API',
            version: '1.0.0',
            description: 'Backend API for Scope3 Emissions Analysis',
            contact: {
                name: 'API Support',
                url: 'https://scope3-emissions.com/support'
            }
        },
        servers: [
            {
                url: 'http://localhost:3000',
                description: 'Development server'
            }
        ],
        components: {
            securitySchemes: {
                bearerAuth: {
                    type: 'http',
                    scheme: 'bearer',
                    bearerFormat: 'JWT'
                }
            }
        },
        security: [{
            bearerAuth: []
        }]
    },
    apis: [
        './src/routes/*.js',
        './src/models/*.js',
        './src/controllers/*.js'
    ]
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);

// Allow CORS for all origins (for development purposes)
app.use(cors());

// Parse JSON requests
app.use(express.json());

// Serve Swagger documentation
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// Root route
/**
 * @swagger
 * /:
 *   get:
 *     summary: Check if API is running
 *     description: Returns a simple message to confirm the API is running
 *     responses:
 *       200:
 *         description: API is running
 *         content:
 *           text/plain:
 *             schema:
 *               type: string
 *               example: Scope 3 Backend API is running!
 */
app.get("/", (req, res) => res.send("Scope 3 Backend API is running!"));

// data route
app.use('/api/rag', ragRoutes);

// data route
app.use('/api/data', dataRoutes);

// AI/ML routes for testing the microservice
app.use('/api/ai-ml', aimlroutes); 

// Auth routes
app.use('/api/auth', authroutes);

// Add a database test route
/**
 * @swagger
 * /db-test:
 *   get:
 *     summary: Test database connection
 *     description: Tests the connection to the PostgreSQL database
 *     responses:
 *       200:
 *         description: Database connection successful
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 *       500:
 *         description: Database connection error
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: false
 *                 error:
 *                   type: string
 */
app.get('/db-test', async (req, res) => {
    try {
        const result = await pool.query('SELECT NOW()');
        res.json({ success: true, timestamp: result.rows[0].now });
    } catch (error) {
        console.error('Database connection error:', error.message);
        res.status(500).json({ success: false, error: error.message });
    }
});

// Start the server
app.listen(3000, () => {
    console.log('Backend running on port 3000');
    console.log('API Documentation available at http://localhost:3000/api-docs');
});

module.exports = app;