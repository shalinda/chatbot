const express = require('express');
const path = require('path');
const axios = require('axios');
const app = express();
const port = 3000;

// Serve static files (like index.html)
app.use(express.static(path.join(__dirname, 'public')));

// Helper function to send SSE response
const sendSSE = (res, text) => {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  const jsonMessage = JSON.stringify({ text });
  res.write(`data: ${jsonMessage}\n\n`);
  res.flushHeaders();
};

// SSE route for echo functionality
app.get('/echo', async (req, res) => {
  const { message, kb } = req.query;
  console.log(`Received kb: ${kb}, message: ${message}`);

  const endpoint = kb ? '/ask1' : '/generate';
  const payload = kb
    ? { kb, question: message }
    : { prompt: message };

  try {
    const response = await axios.post(`http://llm_app:3001${endpoint}`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    const responseData = kb ? response.data.answer : response.data.generated_text;
    console.log(`Response: ${responseData}`);

    sendSSE(res, responseData);

    setTimeout(() => res.end(), 1000);
  } catch (error) {
    console.error(`Error calling ${endpoint}:`, error.message || error);
    res.status(500).send('Error processing request');
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});
