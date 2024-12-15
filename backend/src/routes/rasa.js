const express = require('express');
const axios = require('axios');

const router = express.Router();

// Rasa server URL
const RASA_URL = 'http://rasa:5005/webhooks/rest/webhook';

// Webhook to forward user messages to Rasa
router.post('/', async (req, res) => {
    try {
        const { message } = req.body;

        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        // Forward the user message to Rasa
        const response = await axios.post(RASA_URL, {
            sender: 'user', // Sender identifier (can be dynamic)
            message: message,
        });

        // Return Rasa's response to the frontend
        return res.status(200).json(response.data);
    } catch (error) {
        console.error('Error communicating with Rasa:', error.message);
        return res.status(500).json({ error: 'Failed to connect to Rasa' });
    }
});

module.exports = router;
