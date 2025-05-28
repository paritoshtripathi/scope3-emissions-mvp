const express = require("express");
const axios = require("axios");
const router = express.Router();

/**
 * @swagger
 * components:
 *   schemas:
 *     PredictionRequest:
 *       type: object
 *       required:
 *         - text
 *       properties:
 *         text:
 *           type: string
 *           description: Query text for prediction
 *         context:
 *           type: object
 *           description: Additional context for prediction
 *         options:
 *           type: object
 *           properties:
 *             use_moe:
 *               type: boolean
 *               description: Whether to use mixture of experts
 *             max_tokens:
 *               type: integer
 *               description: Maximum tokens to generate
 *             temperature:
 *               type: number
 *               description: Sampling temperature
 *     PredictionResponse:
 *       type: object
 *       properties:
 *         response:
 *           type: string
 *           description: Generated response
 *         expert_responses:
 *           type: object
 *           description: Responses from different experts
 *         analysis:
 *           type: object
 *           properties:
 *             reasoning:
 *               type: array
 *               items:
 *                 type: string
 *             scope3:
 *               type: object
 *         metadata:
 *           type: object
 *           properties:
 *             experts_used:
 *               type: array
 *               items:
 *                 type: string
 *             confidence:
 *               type: number
 */

/**
 * @swagger
 * /api/ai-ml/predict:
 *   post:
 *     summary: Get AI/ML prediction
 *     description: Send a query to the AI/ML service for prediction using RAG
 *     tags: [AI/ML]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             $ref: '#/components/schemas/PredictionRequest'
 *     responses:
 *       200:
 *         description: Prediction successful
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/PredictionResponse'
 *       500:
 *         description: AI/ML service error
 */
router.post("/predict", async (req, res) => {
    try {
        // Forward request to RAG API
        const response = await axios.post("http://rag-api:5000/api/v1/rag/query", {
            text: req.body.text,
            context: req.body.context || {},
            options: {
                use_moe: true,
                max_tokens: 250,
                temperature: 0.2,
                ...req.body.options
            }
        });

        res.json(response.data);
    } catch (error) {
        console.error("AI/ML service error:", error.message);
        res.status(500).json({ 
            success: false, 
            error: "Failed to fetch prediction",
            details: error.response?.data || error.message
        });
    }
});

/**
 * @swagger
 * /api/ai-ml/health:
 *   get:
 *     summary: Check AI/ML service health
 *     description: Check if the AI/ML service is running and ready
 *     tags: [AI/ML]
 *     responses:
 *       200:
 *         description: Health check successful
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   enum: [healthy, initializing]
 *                 pipeline_ready:
 *                   type: boolean
 *       500:
 *         description: Health check failed
 */
router.get("/health", async (req, res) => {
    try {
        const response = await axios.get("http://rag-api:5000/api/v1/rag/health");
        res.json(response.data);
    } catch (error) {
        console.error("Health check error:", error.message);
        res.status(500).json({ 
            status: "error",
            error: "Failed to check AI/ML service health",
            details: error.response?.data || error.message
        });
    }
});

/**
 * @swagger
 * /api/ai-ml/models:
 *   get:
 *     summary: Get available AI models
 *     description: Get list of available models and their capabilities
 *     tags: [AI/ML]
 *     responses:
 *       200:
 *         description: Models retrieved successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 models:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       name:
 *                         type: string
 *                       description:
 *                         type: string
 *                       capabilities:
 *                         type: array
 *                         items:
 *                           type: string
 *       500:
 *         description: Failed to retrieve models
 */
router.get("/models", async (req, res) => {
    try {
        const response = await axios.get("http://rag-api:5000/api/v1/inference/models");
        res.json(response.data);
    } catch (error) {
        console.error("Models retrieval error:", error.message);
        res.status(500).json({ 
            success: false, 
            error: "Failed to retrieve models",
            details: error.response?.data || error.message
        });
    }
});

module.exports = router;