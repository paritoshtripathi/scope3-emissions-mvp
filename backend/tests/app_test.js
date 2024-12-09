// backend/tests/app.test.js
const request = require('supertest');
const app = require('../app');

test('GET / responds with 200 and a message', async () => {
    const response = await request(app).get('/');
    expect(response.statusCode).toBe(200);
    expect(response.text).toBe('Scope 3 Backend API is running!');
});
