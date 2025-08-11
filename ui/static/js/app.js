// AI Sales Agent - Modern Chat UI JavaScript

class ChatApp {
    constructor() {
        this.socket = io();
        this.messageCount = 0;
        this.extractionCount = 0;
        this.isTyping = false;
        this.currentTab = 'chat';
        this.messages = [];
        this.extractions = [];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadSystemStatus();
        this.initializeCharts();
        this.setupSocketEvents();
        this.autoResizeTextarea();
    }

    setupEventListeners() {
        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => {
            this.toggleTheme();
        });

        // Tab navigation
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        // Message sending
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Control buttons
        document.getElementById('newConversation').addEventListener('click', () => {
            this.newConversation();
        });

        document.getElementById('newChatBtn').addEventListener('click', () => {
            this.newConversation();
        });

        document.getElementById('summarizeBtn').addEventListener('click', () => {
            this.summarizeConversation();
        });

        document.getElementById('exportChat').addEventListener('click', () => {
            this.exportChat();
        });

        // Model controls
        document.getElementById('temperature').addEventListener('input', (e) => {
            document.getElementById('tempValue').textContent = e.target.value;
        });

        document.getElementById('maxTokens').addEventListener('input', (e) => {
            document.getElementById('tokensValue').textContent = e.target.value;
        });

        // Quick prompts
        document.querySelectorAll('.prompt-chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                const prompt = e.target.dataset.prompt;
                this.sendQuickMessage(prompt);
            });
        });

        // Scenario buttons
        document.querySelectorAll('.scenario-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const scenario = e.target.dataset.scenario;
                this.sendQuickMessage(scenario);
            });
        });
    }

    setupSocketEvents() {
        this.socket.on('connect', () => {
            console.log('Connected to server');
            this.showStatus('Connected to AI Sales Agent', 'success');
        });

        this.socket.on('disconnect', () => {
            console.log('Disconnected from server');
            this.showStatus('Disconnected from server', 'error');
        });

        this.socket.on('typing', (data) => {
            this.showTypingIndicator(data.isTyping);
        });
    }

    async loadSystemStatus() {
        try {
            const response = await fetch('/api/system-status');
            const status = await response.json();
            
            if (response.ok) {
                this.updateSystemStatus(status);
            } else {
                console.error('Failed to load system status:', status.error);
            }
        } catch (error) {
            console.error('Error loading system status:', error);
        }
    }

    updateSystemStatus(status) {
        const statusCards = document.querySelectorAll('.status-card .status-value');
        
        if (statusCards[0]) {
            statusCards[0].textContent = status.llm?.provider?.toUpperCase() || 'Unknown';
        }
        
        if (statusCards[1]) {
            statusCards[1].textContent = `${status.agents?.total || 0} Active`;
        }
        
        if (statusCards[2]) {
            statusCards[2].textContent = status.system?.toUpperCase() || 'Unknown';
            statusCards[2].className = `status-value ${status.system === 'operational' ? 'success' : 'warning'}`;
        }
    }

    async sendMessage() {
        const input = document.getElementById('messageInput');
        const message = input.value.trim();
        
        if (!message) return;

        // Clear input
        input.value = '';
        this.autoResizeTextarea();

        // Add user message to chat
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator(true);
        this.showLoading(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();

            if (response.ok) {
                // Hide typing indicator
                this.showTypingIndicator(false);
                
                // Add AI response
                this.addMessage('assistant', data.response, data.timestamp);
                
                // Handle extraction data
                if (data.extraction) {
                    this.addExtraction(data.extraction);
                }
                
                this.updateStats();
            } else {
                this.showError('Failed to send message: ' + data.error);
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.showError('Network error occurred');
        } finally {
            this.showLoading(false);
            this.showTypingIndicator(false);
        }
    }

    sendQuickMessage(message) {
        document.getElementById('messageInput').value = message;
        this.sendMessage();
    }

    addMessage(role, content, timestamp = null) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        
        const time = timestamp ? new Date(timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        }) : new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const avatar = role === 'user' ? 'You' : 'AI';
        const roleClass = role === 'user' ? 'user' : 'assistant';
        
        // Convert markdown to HTML
        const htmlContent = this.renderMarkdown(content);
        
        messageDiv.className = `msg ${roleClass}`;
        messageDiv.innerHTML = `
            <div class="avatar">${avatar[0]}</div>
            <div class="bubble">
                ${htmlContent}
                <div class="meta">${avatar} • ${time}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.messages.push({ role, content, timestamp: time });
        this.messageCount++;
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    renderMarkdown(text) {
        // Basic markdown to HTML conversion
        let html = text;
        
        // Code blocks
        html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>');
        
        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Bold
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
        
        // Links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
        
        // Headers
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
        
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }

    addExtraction(extraction) {
        this.extractions.push(extraction);
        this.extractionCount++;
        this.updateEntitiesTab(extraction);
    }

    updateEntitiesTab(extraction) {
        const entitiesContent = document.getElementById('entitiesContent');
        
        if (this.extractions.length === 1) {
            // Clear empty state
            entitiesContent.innerHTML = '';
        }

        const extractionDiv = document.createElement('div');
        extractionDiv.className = 'extraction-result';
        extractionDiv.innerHTML = `
            <div class="extraction-header">
                <h4>Latest Extraction</h4>
                <span class="confidence">${Math.round(extraction.confidence * 100)}% confidence</span>
            </div>
            <div class="entities-grid">
                ${Object.entries(extraction.entities).map(([key, value]) => 
                    value ? `<div class="entity-item"><strong>${key}:</strong> ${value}</div>` : ''
                ).join('')}
            </div>
            <div class="extraction-meta">
                Method: ${extraction.method} • ${new Date(extraction.timestamp).toLocaleString()}
            </div>
        `;

        entitiesContent.appendChild(extractionDiv);
    }

    showTypingIndicator(show) {
        const chatMessages = document.getElementById('chatMessages');
        let typingIndicator = document.getElementById('typingIndicator');

        if (show && !typingIndicator) {
            typingIndicator = document.createElement('div');
            typingIndicator.id = 'typingIndicator';
            typingIndicator.className = 'msg assistant';
            typingIndicator.innerHTML = `
                <div class="avatar">AI</div>
                <div class="bubble">
                    <div class="typing-indicator">
                        <span class="typing-dots">AI is thinking</span>
                    </div>
                </div>
            `;
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        } else if (!show && typingIndicator) {
            typingIndicator.remove();
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        overlay.classList.toggle('show', show);
    }

    showStatus(message, type = 'info') {
        // Simple status notification (could be enhanced with toast notifications)
        console.log(`[${type.toUpperCase()}] ${message}`);
    }

    showError(message) {
        this.showStatus(message, 'error');
        // Could add toast notification here
    }

    updateStats() {
        document.getElementById('messageCount').textContent = this.messageCount;
        document.getElementById('extractionCount').textContent = this.extractionCount;
    }

    toggleTheme() {
        const body = document.body;
        const currentTheme = body.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        body.setAttribute('data-theme', newTheme);
        
        // Update icon
        const icon = document.querySelector('#themeToggle i');
        icon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
        
        // Save preference
        localStorage.setItem('theme', newTheme);
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}Tab`);
        });

        this.currentTab = tabName;

        // Load tab-specific content
        if (tabName === 'analytics') {
            this.updateCharts();
        }
    }

    newConversation() {
        // Clear messages
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.innerHTML = `
            <div class="welcome-message">
                <div class="msg assistant">
                    <div class="avatar">AI</div>
                    <div class="bubble">
                        <p>👋 Hello! I'm your AI recruiting assistant. How can I help you today?</p>
                        <div class="meta">AI • Welcome</div>
                    </div>
                </div>
            </div>
        `;

        // Reset counters
        this.messages = [];
        this.extractions = [];
        this.messageCount = 0;
        this.extractionCount = 0;
        this.updateStats();

        // Clear entities tab
        document.getElementById('entitiesContent').innerHTML = 
            '<p class="empty-state">No entities extracted yet. Start chatting to see extracted information.</p>';
    }

    async summarizeConversation() {
        if (this.messages.length === 0) {
            this.showStatus('No conversation to summarize', 'warning');
            return;
        }
        try {
            this.showStatus('Generating summary...', 'info');
            const resp = await fetch('/api/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ messages: this.messages })
            });
            const data = await resp.json();
            if(!resp.ok){
                this.showStatus(data.error || 'Summary failed', 'error');
                return;
            }
            this.addMessage('assistant', `📝 **Conversation Summary:**\n\n${data.summary || '(no summary)'}`);
            this.showStatus('Summary added', 'success');
        } catch(e){
            this.showStatus(e.message, 'error');
        }
    }

    exportChat() {
        if (this.messages.length === 0) {
            this.showStatus('No conversation to export', 'warning');
            return;
        }

        const exportData = {
            messages: this.messages,
            extractions: this.extractions,
            exported: new Date().toISOString()
        };

        // Create download
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-export-${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showStatus('Chat exported successfully', 'success');
    }

    autoResizeTextarea() {
        const textarea = document.getElementById('messageInput');
        textarea.style.height = '20px';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    initializeCharts() {
        // Placeholder for chart initialization
        // In a real app, you'd use Chart.js or similar
    }

    updateCharts() {
        // Update analytics charts with current data
        if (this.currentTab === 'analytics') {
            // Sample data for demonstration
            const conversationData = {
                x: Array.from({length: 7}, (_, i) => `Day ${i + 1}`),
                y: [5, 8, 12, 15, 18, 22, 25],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Daily Conversations'
            };

            const accuracyData = {
                x: Array.from({length: 7}, (_, i) => `Day ${i + 1}`),
                y: [85, 87, 90, 92, 95, 97, 99],
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Extraction Accuracy'
            };

            if (window.Plotly) {
                Plotly.newPlot('conversationChart', [conversationData], {
                    title: 'Daily Conversations',
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent'
                });

                Plotly.newPlot('accuracyChart', [accuracyData], {
                    title: 'Extraction Accuracy',
                    paper_bgcolor: 'transparent',
                    plot_bgcolor: 'transparent'
                });
            }
        }
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', savedTheme);
    
    const themeIcon = document.querySelector('#themeToggle i');
    if (themeIcon) {
        themeIcon.className = savedTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }

    // Initialize chat app
    window.chatApp = new ChatApp();
});
