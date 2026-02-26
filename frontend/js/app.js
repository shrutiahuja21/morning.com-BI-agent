const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');

const sessionId = 'session_' + Math.random().toString(36).substr(2, 9);
const API_URL = '/query'; // Relative path for Vercel deployment

function appendMessage(role, text, toolCalls = [], notes = []) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}-message`;

    let content = `<div class="text">${text.replace(/\n/g, '<br>')}</div>`;

    if (toolCalls.length > 0) {
        content += `
            <div class="trace-container">
                <div class="trace-header">Action Trace</div>
                ${toolCalls.map(t => `<div class="trace-item">${t}</div>`).join('')}
            </div>
        `;
    }

    if (notes.length > 0) {
        content += `
            <div class="trace-container" style="border-left: 2px solid #e17055;">
                <div class="trace-header" style="color: #e17055;">Data Quality Notes</div>
                ${notes.map(n => `<div class="trace-item" style="color: #fab1a0;">${n}</div>`).join('')}
            </div>
        `;
    }

    msgDiv.innerHTML = content;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message agent-message typing-indicator-container';
    typingDiv.id = 'typing';
    typingDiv.innerHTML = `
        <div class="typing-indicator">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatWindow.appendChild(typingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById('typing');
    if (typing) typing.remove();
}

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    appendMessage('user', query);
    chatInput.value = '';

    showTyping();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query, session_id: sessionId })
        });

        const data = await response.json();
        hideTyping();
        appendMessage('agent', data.answer, data.tool_calls, data.data_quality_notes);
    } catch (error) {
        hideTyping();
        appendMessage('agent', 'Error connecting to the BI Agent. Is the backend running?');
        console.error('Fetch error:', error);
    }
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Initial Welcome
setTimeout(() => {
    appendMessage('agent', 'Hello! I am your Monday.com BI Assistant. I can help you analyze your deals pipeline and work orders.');
}, 500);
