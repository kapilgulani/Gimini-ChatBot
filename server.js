const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const { Sequelize, DataTypes } = require('sequelize');
const { GoogleGenerativeAI } = require('@google/generative-ai');

// Set up Express app
const app = express();
app.use(cors());
app.use(bodyParser.json());

// Set up Sequelize with SQLite for saving chat history
const sequelize = new Sequelize('sqlite:chatHistory.db');

const ChatHistory = sequelize.define('ChatHistory', {
    taxPrompt: {
        type: DataTypes.TEXT,
        allowNull: false
    },
    response: {
        type: DataTypes.TEXT,
        allowNull: false
    }
});

// Sync database
ChatHistory.sync();

// API Key for Google Generative AI
const apiKey = 'YOUR_API_KEY'; // I have not pushed my google cloud api key
const genAI = new GoogleGenerativeAI(apiKey);
const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

// Endpoint to generate content using Gemini API
app.post('/generate-content', async (req, res) => {
    try {
        const promptText = req.body.prompt;
        console.log('Prompt received:', promptText);

        // Send prompt to Gemini API using the correct format from the documentation
        const result = await model.generateContent(promptText);

        // Assuming response.text() holds the generated content
        const generatedText = result.response.text();
        console.log('Response from API:', generatedText);

        res.json({ response: generatedText });
    } catch (error) {
        console.error('Error generating content:', error);
        res.status(500).json({ error: error.message });
    }
});

// Endpoint to save a chat to the SQLite database
app.post('/save-chat', async (req, res) => {
    try {
        const { prompt, response } = req.body;

        const chatEntry = await ChatHistory.create({
            taxPrompt: prompt,
            response: response
        });

        res.json({ id: chatEntry.id });
    } catch (error) {
        console.error('Error saving chat:', error);
        res.status(500).json({ error: error.message });
    }
});

// Endpoint to get chat history by ID
app.get('/get-chat-history/:id', async (req, res) => {
    try {
        const chatId = req.params.id;

        // Find chat by ID
        const chatEntry = await ChatHistory.findByPk(chatId);

        if (!chatEntry) {
            return res.status(404).json({ error: 'Chat entry not found' });
        }

        // Respond with the chat entry
        res.json(chatEntry);
    } catch (error) {
        console.error('Error fetching chat:', error);
        res.status(500).json({ error: error.message });
    }
});

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});