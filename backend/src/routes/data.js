const express = require("express");
const router = express.Router();
const { insertEmissionsData } = require("../models/emissionsModel"); // Correct import path
const pool = require('../models/db');
const axios = require("axios");

// Data ingestion route
router.post("/ingestemissions", async (req, res) => {
    try {
        const { data } = req.body;

        if (!data || !Array.isArray(data)) {
            return res.status(400).json({ message: "Invalid data format. Provide an array of records." });
        }

        const insertedRecords = await insertEmissionsData(data);
        return res.status(201).json({
            message: "Data ingested successfully",
            records: insertedRecords
        });
    } catch (error) {
        console.error("Data ingestion error:", error.message);
        res.status(500).json({ message: "Failed to ingest data", error: error.message });
    }
});

// Fetch emission insights
router.get("/insights", async (req, res) => {
    try {
        const query = `
            SELECT 
                category, 
                SUM(current_emissions) AS total_emissions,
                SUM(potential_reduction) AS total_reduction
            FROM emissions_data
            GROUP BY category;
        `;
        const { rows } = await pool.query(query);
        res.status(200).json({ insights: rows });
    } catch (error) {
        console.error("Error fetching insights:", error.message);
        res.status(500).json({ message: "Failed to fetch insights", error: error.message });
    }
});

// Predict emission reductions
router.post("/predict", async (req, res) => {
    try {
        const { category, reduction_percentage } = req.body;

        if (!category || !reduction_percentage) {
            return res.status(400).json({ message: "Category and reduction percentage are required." });
        }

        const query = `
            SELECT SUM(current_emissions) AS total_emissions
            FROM emissions_data
            WHERE category = $1;
        `;
        const { rows } = await pool.query(query, [category]);

        if (rows.length === 0 || rows[0].total_emissions === null) {
            return res.status(404).json({ message: "Category not found." });
        }

        const totalEmissions = parseFloat(rows[0].total_emissions);
        const predictedReduction = (reduction_percentage / 100) * totalEmissions;

        res.status(200).json({
            category,
            total_emissions: totalEmissions,
            reduction_percentage,
            predicted_reduction: predictedReduction,
            new_emissions: totalEmissions - predictedReduction
        });
    } catch (error) {
        console.error("Error calculating predictions:", error.message);
        res.status(500).json({ message: "Failed to predict emissions", error: error.message });
    }
});

// Generate explanation route
router.post('/generateExplanation', async (req, res) => {
  const { context } = req.body;
  console.log('IN GENERATE EXPLANATION', context);
  const prompt = `
    You are a maritime sustainability expert specializing in Scope 3 emissions. 
    Based on the following data: ${JSON.stringify(context)}, generate actionable insights and reduction strategies.
  `;
  console.log('Generating explanation with prompt...1',prompt);
  try {
    console.log('Generating explanation with prompt...2',prompt);
    const response = await axios.post('http://localhost:5000/predict_with_template', { prompt });
    res.json(response.data.result); // Result from Llama 3
  } catch (error) {
    console.log('Generating explanation with prompt...3',prompt);
    console.error('Error generating explanation:', error);
    res.status(500).send('Internal Server Error');
  }
});

module.exports = router;
