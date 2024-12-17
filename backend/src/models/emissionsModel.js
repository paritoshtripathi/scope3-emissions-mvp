const pool = require("./db"); // Use the correct path to db.js

const insertEmissionsData = async (data) => {
    const client = await pool.connect();
    try {
        const query = `
            INSERT INTO emissions_data (category, source_type, current_emissions, potential_reduction, reduction_strategy, predicted_emissions)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *;
        `;
        const promises = data.map(row => 
            client.query(query, [
                row.category,
                row.source_type,
                row.current_emissions,
                row.potential_reduction,
                row.reduction_strategy || null,
                row.predicted_emissions || null
            ])
        );
        const results = await Promise.all(promises);
        return results.map(res => res.rows[0]);
    } catch (error) {
        console.error("Error inserting emissions data:", error.message);
        throw error;
    } finally {
        client.release();
    }
};

module.exports = { insertEmissionsData }; // Properly export the function
