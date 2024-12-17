const EmissionsData = require("../models/emissionsModel");

// Endpoint to ingest data
exports.ingestData = async (req, res) => {
  try {
    const { data } = req.body;

    if (!data || !Array.isArray(data)) {
      return res.status(400).json({ message: "Invalid data format. Provide an array of records." });
    }

    // Validate and insert each record
    const records = await EmissionsData.bulkCreate(data, { validate: true });
    return res.status(201).json({ message: "Data ingested successfully", records });
  } catch (error) {
    console.error("Data ingestion error:", error);
    return res.status(500).json({ message: "Failed to ingest data", error });
  }
};
