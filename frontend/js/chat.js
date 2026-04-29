const CONFIG = {
    API_URL: 'http://localhost:8000/chat',
    HEALTH_URL: 'http://localhost:8000/health',
    TIMEOUT: 30000
};

let state = {
    isWaiting: false,
    isOnline: true,
    userId: 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
};

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    checkConnection();
    setInterval(checkConnection, 5000);
    document.getElementById('userInput').focus();
});

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
        document.documentElement.setAttribute('data-theme', 'dark');
        updateThemeIcon('dark');
    } else {
        document.documentElement.setAttribute('data-theme', 'light');
        updateThemeIcon('light');
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
    const themeIcon = document.querySelector('.theme_icon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
    }
}

async function sendMessage() {
    if (state.isWaiting) return;
    
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    
    if (!text) return;
    
    addMessage(text, 'user');
    input.value = '';
    input.focus();
    
    showTypingIndicator();
    state.isWaiting = true;
    
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.TIMEOUT);
        
        const response = await fetch(CONFIG.API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text, user_id: state.userId }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        removeTypingIndicator();
        
        const confidencePercent = (data.confidence * 100).toFixed(1);
        const reply = data.reply + `<div class="intent_badge">🤖 ${data.intent} (${confidencePercent}%)</div>`;
        addMessage(reply, 'bot');
        
    } catch (error) {
        console.error('Ошибка:', error);
        removeTypingIndicator();
        addMessage('❌ Ошибка: Сервер не запущен. Запустите: python backend\\app.py', 'bot');
        state.isOnline = false;
        updateStatusIndicator(false);
    } finally {
        state.isWaiting = false;
    }
}

function sendSuggestion(text) {
    document.getElementById('userInput').value = text;
    sendMessage();
}

function addMessage(text, sender) {
    const messagesDiv = document.getElementById('messagesArea');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message_${sender}`;
    
    const avatar = sender === 'bot' ? '🤖' : '👤';
    
    const formattedText = text.replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = `
        <div class="message_avatar">${avatar}</div>
        <div class="message_text">${formattedText}</div>
    `;
    
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function showTypingIndicator() {
    removeTypingIndicator();
    const messagesDiv = document.getElementById('messagesArea');
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'message_bot';
    indicatorDiv.id = 'typingIndicator';
    indicatorDiv.innerHTML = `
        <div class="message_avatar">🤖</div>
        <div class="message_content">
            <div class="typing_indicator">
                <span class="typing_dot"></span>
                <span class="typing_dot"></span>
                <span class="typing_dot"></span>
            </div>
        </div>
    `;
    messagesDiv.appendChild(indicatorDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

async function checkConnection() {
    try {
        const response = await fetch(CONFIG.HEALTH_URL, { signal: AbortSignal.timeout(3000) });
        if (response.ok) {
            if (!state.isOnline) {
                state.isOnline = true;
                updateStatusIndicator(true);
                addMessage('✅ Соединение с сервером восстановлено!', 'bot');
            }
            return true;
        }
        throw new Error();
    } catch (error) {
        if (state.isOnline) {
            state.isOnline = false;
            updateStatusIndicator(false);
        }
        return false;
    }
}

function updateStatusIndicator(isOnline) {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    if (isOnline) {
        if (statusDot) statusDot.classList.remove('offline');
        if (statusText) statusText.textContent = 'Онлайн';
    } else {
        if (statusDot) statusDot.classList.add('offline');
        if (statusText) statusText.textContent = 'Офлайн (запусти сервер)';
    }
}

document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});