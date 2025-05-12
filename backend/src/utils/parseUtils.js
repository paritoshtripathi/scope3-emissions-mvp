// parseUtils.js
const fs = require('fs');
const csvParser = require('csv-parser');
const path = require('path');

/**
 * Validates file type based on extension
 * @param {string} filename - Name of the file
 * @returns {boolean} Whether file type is supported
 */
function isValidFileType(filename) {
  const validExtensions = ['.csv', '.CSV'];
  const ext = path.extname(filename);
  return validExtensions.includes(ext);
}

/**
 * Parses a CSV file into a list of JSON records.
 * @param {string} filePath - Path to the uploaded file.
 * @returns {Promise<array>} Array of row objects.
 */
async function parseCsvToJson(filePath) {
  if (!isValidFileType(filePath)) {
    throw new Error('Unsupported file type. Please upload a CSV file.');
  }

  return new Promise((resolve, reject) => {
    const results = [];
    let headers = [];
    let rowCount = 0;
    const MAX_ROWS = 10000; // Limit number of rows to prevent memory issues

    fs.createReadStream(filePath)
      .pipe(csvParser())
      .on('headers', (headerRow) => {
        headers = headerRow;
      })
      .on('data', (row) => {
        rowCount++;
        if (rowCount > MAX_ROWS) {
          reject(new Error(`File exceeds maximum limit of ${MAX_ROWS} rows`));
          return;
        }
        // Validate row data
        const validRow = Object.values(row).some(value => value !== '');
        if (validRow) {
          results.push(row);
        }
      })
      .on('end', () => {
        if (results.length === 0) {
          reject(new Error('No valid data found in file'));
          return;
        }
        resolve({
          data: results,
          headers: headers,
          totalRows: results.length
        });
      })
      .on('error', (err) => {
        reject(new Error(`Error parsing file: ${err.message}`));
      });
  });
}

/**
 * Cleans up uploaded file
 * @param {string} filePath - Path to the uploaded file
 */
function cleanupFile(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
  } catch (error) {
    console.error('Error cleaning up file:', error);
  }
}

module.exports = { 
  parseCsvToJson,
  isValidFileType,
  cleanupFile
};