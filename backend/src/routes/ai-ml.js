// backend/src/routes/aiMl.js
const express = require("express");
const axios = require("axios");
const router = express.Router();

// Route to call AI/ML microservice
router.post("/predict", async (req, res) => {
    try {
        const response = await axios.post("http://localhost:5000/predict", req.body);
        res.json(response.data);
    } catch (error) {
        console.error("AI/ML service error:", error.message);
        res.status(500).json({ success: false, error: "Failed to fetch prediction" });
    }
});

module.exports = router;
