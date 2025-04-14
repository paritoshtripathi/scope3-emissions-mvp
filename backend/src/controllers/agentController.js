const { invokeAgents } = require('../utils/agentInvoker');
exports.getAgentInsights = async (req, res) => {
  try {
    const persona = req.query.persona || 'CXO';
    const fileId = req.query.fileId || '';
    const insights = await invokeAgents(persona, fileId);
    res.json({ persona, insights });
  } catch (err) {
    res.status(500).json({ error: 'Failed to fetch insights', details: err.message });
  }
};
