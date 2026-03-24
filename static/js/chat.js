class Chatbot {
    constructor() {
        this.currentLanguage = 'en';
        this.isOnline = false;
        this.isTyping = false;
        
        this.initializeElements();
        this.loadLanguages();
        this.checkInternetStatus();
        this.setupEventListeners();
        this.loadGreeting();
        
        // Auto-check internet every 30 seconds
        setInterval(() => this.checkInternetStatus(), 30000);
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.languageSelect = document.getElementById('languageSelect');
        this.statusDot = document.getElementById('statusDot');
        this.statusText = document.getElementById('statusText');
        this.welcomeMessageDiv = document.getElementById('welcomeMessage');
    }
    
    async loadLanguages() {
        try {
            const response = await fetch('/api/languages');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.languageSelect.innerHTML = '';
                data.languages.forEach(lang => {
                    const option = document.createElement('option');
                    option.value = lang.code;
                    option.textContent = lang.name;
                    if (lang.code === data.default) {
                        option.selected = true;
                        this.currentLanguage = lang.code;
                    }
                    this.languageSelect.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading languages:', error);
        }
    }
    
    async checkInternetStatus() {
        try {
            const response = await fetch('/api/check_internet');
            const data = await response.json();
            
            this.isOnline = data.online;
            
            if (data.online) {
                this.statusDot.className = 'status-dot online';
                this.statusText.textContent = 'Online (AI Mode)';
            } else {
                this.statusDot.className = 'status-dot offline';
                this.statusText.textContent = 'Offline (Database Mode)';
            }
        } catch (error) {
            console.error('Error checking internet:', error);
            this.isOnline = false;
            this.statusDot.className = 'status-dot offline';
            this.statusText.textContent = 'Offline (Database Mode)';
        }
    }
    
    async loadGreeting() {
        try {
            const response = await fetch(`/api/greeting?language=${this.currentLanguage}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                const greetingText = `${data.greeting}<br><small style="font-size: 0.85rem; opacity: 0.8;">${data.mode_message}</small>`;
                this.welcomeMessageDiv.innerHTML = greetingText;
            }
        } catch (error) {
            console.error('Error loading greeting:', error);
            this.welcomeMessageDiv.textContent = 'Welcome to the chatbot!';
        }
    }
    
    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.languageSelect.addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            this.loadGreeting();
            this.addSystemMessage(`Language changed to ${e.target.options[e.target.selectedIndex].text}`);
        });
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message to chat
        this.addUserMessage(message);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        this.isTyping = true;
        this.sendButton.disabled = true;
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    language: this.currentLanguage
                })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.hideTypingIndicator();
            
            if (data.status === 'success') {
                const mode = data.mode === 'online' ? '🤖 AI' : '💾 Database';
                const responseText = `${data.response}<br><small style="font-size: 0.7rem; opacity: 0.6;">Source: ${mode}</small>`;
                this.addBotMessage(responseText);
            } else {
                this.addBotMessage('Sorry, an error occurred. Please try again.');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addBotMessage('Network error. Please check your connection.');
        } finally {
            this.isTyping = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    }
    
    addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user';
        messageDiv.innerHTML = `<div class="message-content">${this.escapeHtml(message)}</div>`;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addBotMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot';
        messageDiv.innerHTML = `<div class="message-content">${message}</div>`;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';
        messageDiv.innerHTML = `<div class="message-content">${this.escapeHtml(message)}</div>`;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        `;
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Chatbot();
});