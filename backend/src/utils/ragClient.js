const axios = require('axios');
const FormData = require('form-data');

class RAGClient {
    constructor(baseURL = process.env.RAG_API_URL || 'http://localhost:5000') {
        this.client = axios.create({
            baseURL,
            timeout: 30000
        });
    }

    async healthCheck() {
        try {
            const response = await this.client.get('/health');
            return response.data;
        } catch (error) {
            console.error('RAG health check failed:', error);
            throw error;
        }
    }

    async processFile(formData) {
        try {
            const response = await this.client.post('/process-file', formData, {
                headers: {
                    ...formData.getHeaders()
                }
            });
            return response.data;
        } catch (error) {
            console.error('File processing failed:', error);
            throw error;
        }
    }

    async chat(context) {
        try {
            const response = await this.client.post('/chat', {
                message: context,
                context: {
                    type: 'scope3',
                    domain: 'emissions'
                }
            });
            return response.data;
        } catch (error) {
            console.error('Chat query failed:', error);
            throw error;
        }
    }
}

module.exports = new RAGClient();