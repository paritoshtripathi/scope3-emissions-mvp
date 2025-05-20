const express = require('express');
const router = express.Router();
const ragClient = require('../utils/ragClient');

// Health check
router.get('/health', async (req, res) => {
    try {
        const health = await ragClient.healthCheck();
        res.json(health);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Process documents
router.post('/documents', async (req, res) => {
    try {
        const { documents } = req.body;
        const result = await ragClient.processDocuments(documents);
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Query
router.post('/query', async (req, res) => {
    try {
        const { query, topK } = req.body;
        const result = await ragClient.query(query, topK);
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Save state
router.post('/save', async (req, res) => {
    try {
        const result = await ragClient.saveState();
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Load state
router.post('/load', async (req, res) => {
    try {
        const result = await ragClient.loadState();
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;