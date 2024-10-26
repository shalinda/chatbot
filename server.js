const express = require('express');
const path = require('path');
const axios = require('axios');  // Import axios for HTTP requests
const app = express();
const port = 3000;

// Serve static files (like index.html)
app.use(express.static(path.join(__dirname, 'public')));

// SSE route for echo functionality
app.get('/echo', async (req, res) => {
  const message = req.query.message;
  console.log(`Received message: ${message}`);

  try {
    // Make a POST request to the /generate endpoint on port 3001
    const response = await axios.post('http://llm_app:3001/generate', {
      prompt: message
    }, {
      headers: { 'Content-Type': 'application/json' }
    });

    const generatedResponse = response.data.generated_text;
    console.log(`Generated response: ${generatedResponse}`);

    // Send the response back to the HTTP client
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    const jsonMessage = JSON.stringify({ text: generatedResponse });
    res.write(`data: ${jsonMessage}\n\n`);
    res.flushHeaders();

    setTimeout(() => {
      res.end();
    }, 1000);

  } catch (error) {
    console.error('Error calling /generate:', error);
    res.status(500).send('Error generating text');
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server running on http://localhost:${port}`);
});

