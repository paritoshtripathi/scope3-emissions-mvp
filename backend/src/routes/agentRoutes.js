const express = require('express');
const router = express.Router();
const { getAgentInsights } = require('../controllers/agentController');
router.get('/insights', getAgentInsights);
module.exports = router;
