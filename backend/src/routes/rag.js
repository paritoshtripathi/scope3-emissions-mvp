const express = require('express');
const router = express.Router();
const axios = require('axios');
const logger = require('../utils/logger');

// RAG API endpoint from environment variable
const RAG_API_URL = process.env.RAG_API_URL || 'http://ai-ml:5000';

/**
 * Process chat query through RAG pipeline
 */
router.post('/query', async (req, res) => {
    try {
        const { text, context, options } = req.body;

        if (!text) {
            return res.status(400).json({
                error: 'Query text is required'
            });
        }

        // Call RAG API
        const response = await axios.post(`${RAG_API_URL}/rag/query`, {
            text,
            context,
            options
        });

        // Transform response for frontend
        const ragResponse = response.data;
        const transformedResponse = {
            answer: ragResponse.answer,
            sources: ragResponse.sources || [],
            confidence: ragResponse.confidence,
            metadata: {
                experts: ragResponse.metadata?.experts_used || [],
                reasoning: ragResponse.metadata?.reasoning_paths || [],
                categories: ragResponse.metadata?.scope3_categories || []
            }
        };

        res.json(transformedResponse);

    } catch (error) {
        logger.error('Error in RAG query:', error);
        res.status(500).json({
            error: 'Failed to process query',
            details: error.message
        });
    }
});

/**
 * Get RAG system health status
 */
router.get('/health', async (req, res) => {
    try {
        const response = await axios.get(`${RAG_API_URL}/rag/health`);
        res.json(response.data);
    } catch (error) {
        logger.error('Error checking RAG health:', error);
        res.status(500).json({
            error: 'Failed to check RAG system health',
            details: error.message
        });
    }
});

module.exports = router;