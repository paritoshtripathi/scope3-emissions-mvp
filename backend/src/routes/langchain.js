const express = require("express");
const axios = require("axios");
const router = express.Router();

router.post("/query", async (req, res) => {
    const { question } = req.body;
    if (!question) {
        return res.status(400).json({ error: "Question is required" });
    }

    try {
        const response = await axios.post("http://ai-ml:5000/query", { question });
        res.json(response.data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

module.exports = router;
