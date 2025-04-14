// parseUtils.js
const fs = require('fs');
const csvParser = require('csv-parser');

/**
 * Parses a CSV file into a list of JSON records.
 * @param {string} filePath - Path to the uploaded file.
 * @returns {Promise<array>} Array of row objects.
 */
function parseCsvToJson(filePath) {
  return new Promise((resolve, reject) => {
    const results = [];
    fs.createReadStream(filePath)
      .pipe(csvParser())
      .on('data', (row) => results.push(row))
      .on('end', () => resolve(results))
      .on('error', (err) => reject(err));
  });
}

module.exports = { parseCsvToJson };
