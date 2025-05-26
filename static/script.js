// Initialize Plotly for mood chart
let moodChart;

// Map emotions to icons
class Emotion {
    constructor(name, color, icon) {
        this.name = name;
        this.color = color;
        this.icon = icon;
    }
}

const EMOTIONS = {
    happy: new Emotion('Happy', '#FFD700', '😊'),
    sad: new Emotion('Sad', '#ADD8E6', '😔'),
    angry: new Emotion('Angry', '#FF4500', '😡'),
    anxious: new Emotion('Anxious', '#FFB6C1', '😢'),
    excited: new Emotion('Excited', '#FFA500', '🤩')
};

// Initialize mood chart
async function initializeMoodChart() {
    const moodData = await fetch('/mood_history').then(response => response.json());
    updateMoodChart(moodData);
}

function updateMoodChart(data) {
    const dates = data.map(entry => entry.date);
    const emotions = data.map(entry => entry.emotion);
    const colors = data.map(entry => entry.color);

    const trace = {
        x: dates,
        y: emotions,
        type: 'scatter',
        mode: 'markers',
        marker: {
            color: colors,
            size: 20
        }
    };

    const layout = {
        title: 'Your Mood History',
        xaxis: {
            title: 'Date',
            tickangle: -45
        },
        yaxis: {
            title: 'Emotion',
            tickmode: 'array',
            tickvals: Object.keys(EMOTIONS),
            ticktext: Object.keys(EMOTIONS).map(key => EMOTIONS[key].name)
        },
        height: 400,
        margin: { t: 40, b: 100 }
    };

    Plotly.newPlot('moodChart', [trace], layout);
}

// Handle journal entry submission
let currentConversationId = null;

async function sendMessage() {
    const input = document.getElementById('chatInput').value.trim();
    if (!input) return;

    try {
        const response = await fetch('/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                text: input,
                conversation_id: currentConversationId
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Failed to submit message');
        }

        if (data.error) {
            alert(data.error);
            return;
        }

        currentConversationId = data.conversation_id;

        // Create user message element
        const userMessage = document.createElement('div');
        userMessage.className = 'user-message flex justify-end mb-4';
        userMessage.innerHTML = `
            <div class="bg-blue-100 px-4 py-2 rounded-l-lg rounded-r-lg max-w-[80%]">
                ${input}
            </div>
        `;
        document.getElementById('chatContainer').appendChild(userMessage);

        // Create AI response element
        const aiMessage = document.createElement('div');
        aiMessage.className = 'ai-message flex justify-start mb-4';
        aiMessage.innerHTML = `
            <div class="bg-gray-100 px-4 py-2 rounded-l-lg rounded-r-lg max-w-[80%]">
                <div class="flex items-center gap-2 mb-2">
                    <span class="text-xl">${EMOTIONS[data.emotion].icon}</span>
                    <span class="font-semibold">${EMOTIONS[data.emotion].name}</span>
                </div>
                ${data.response}
            </div>
        `;
        document.getElementById('chatContainer').appendChild(aiMessage);

        // Clear input and scroll to bottom
        document.getElementById('chatInput').value = '';
        document.getElementById('chatContainer').scrollTop = document.getElementById('chatContainer').scrollHeight;
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to send message. Please try again.');
    }
}

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initializeMoodChart();
});
