const axios = require('axios');
exports.invokeAgents = async (persona, fileId) => {
  const responses = await Promise.all([
    axios.get('http://localhost:5001/insights'),
    axios.get('http://localhost:5002/narrative')
  ]);
  return responses.map(res => res.data).flat();
};
