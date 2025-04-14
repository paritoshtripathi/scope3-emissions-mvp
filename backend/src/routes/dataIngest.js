const express = require('express');
const multer = require('multer');
const csv = require('csv-parser');
const fs = require('fs');
const path = require('path');
const pool = require('../models/db');
const { insertEmissionsData } = require("../models/emissionsModel"); // Correct import path
const axios = require("axios");
const { parseCsvToJson } = require('../utils/parseUtils');


const router = express.Router();

// File storage
const uploadDir = path.join(__dirname, '..', 'uploads');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);


// Multer config
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, `${Date.now()}-${file.originalname}`)
});
const upload = multer({ storage });

router.post('/ingest', upload.single('file'), async (req, res) => {
  try {
    const filePath = req.file.path;
    const originalName = req.file.originalname;
    const category = req.body.category || 'Uncategorized';
    const source = req.body.s3Url || 'upload';

    // Insert metadata into ingestion_log
    const result = await pool.query(
      `INSERT INTO ingestion_log (filename, category, source, file_path) 
       VALUES ($1, $2, $3, $4) RETURNING id`,
      [originalName, category, source, filePath]
    );
    const fileId = result.rows[0].id;

    // Parse and insert rows
    const rows = await parseCsvToJson(filePath);
    for (const row of rows) {
      await pool.query(
        `INSERT INTO uploaded_records (file_id, data) VALUES ($1, $2)`,
        [fileId, row]
      );
    }

    res.json({
      message: 'File uploaded and data saved successfully.',
      fileId,
      totalRecords: rows.length,
      preview: rows.slice(0, 5),
      columns: rows.length ? Object.keys(rows[0]) : []
    });
  } catch (err) {
    console.error('Error during ingestion:', err);
    res.status(500).json({ error: 'File ingestion failed.' });
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

// Get all uploaded file history
router.get('/history', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT id, filename, category, source, upload_time FROM ingestion_log ORDER BY upload_time DESC`
    );
    res.json(result.rows);
  } catch (err) {
    console.error('Failed to fetch ingestion history:', err);
    res.status(500).json({ error: 'Unable to fetch file history' });
  }
});

// Get ingested records by file ID
router.get('/query/:fileId', async (req, res) => {
  const { fileId } = req.params;
  try {
    const result = await pool.query(
      `SELECT data FROM uploaded_records WHERE file_id = $1 ORDER BY id LIMIT 100`,
      [fileId]
    );
    const records = result.rows.map(row => row.data);
    const columns = records.length ? Object.keys(records[0]) : [];

    res.json({
      fileId,
      totalRecords: records.length,
      columns,
      preview: records
    });
  } catch (err) {
    console.error('Error querying data:', err);
    res.status(500).json({ error: 'Failed to fetch data for this file' });
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

module.exports = router;
