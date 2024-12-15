const express = require('express');
const router = express.Router();

router.get('/sample', (req, res) => {
    res.json({
        message: 'Hello from the backend!',
        data: [1, 2, 3, 4, 5],
    });
});

module.exports = router;
