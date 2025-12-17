// DataRobot Agent Chat Application

class ChatApp {
    constructor() {
        this.chatForm = document.getElementById('chatForm');
        this.messageInput = document.getElementById('messageInput');
        this.chatMessages = document.getElementById('chatMessages');
        this.sendButton = document.getElementById('sendButton');
        this.configStatus = document.getElementById('configStatus');
        this.statusIndicator = document.getElementById('statusIndicator');
        this.statusText = document.getElementById('statusText');
        
        // Get base path dynamically from current URL
        // DataRobot may host the app at /customApps/{id}/ even if SCRIPT_NAME is empty
        const currentPath = window.location.pathname;
        console.log('Current URL pathname:', currentPath);
        
        // If we're at /customApps/{id}/ or similar, extract that as base path
        let basePath = '';
        if (currentPath !== '/' && currentPath !== '') {
            // Remove trailing slash
            basePath = currentPath.replace(/\/$/, '');
        }
        
        // Also try to get from meta tag (set by backend)
        const metaBasePath = document.querySelector('meta[name="base-path"]')?.content || '';
        if (metaBasePath && metaBasePath !== '/') {
            basePath = metaBasePath.replace(/\/$/, '');
        }
        
        this.apiBase = basePath;
        this.isProcessing = false;
        
        console.log('Detected Base Path:', basePath);
        console.log('API Base:', this.apiBase);
        console.log('Full API URLs:', {
            config: `${this.apiBase}/api/config`,
            chat: `${this.apiBase}/api/chat`,
            health: `${this.apiBase}/api/health`
        });
        
        this.init();
    }
    
    init() {
        // Check configuration status on load
        this.checkConfig();
        
        // Set up event listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Focus input on load
        this.messageInput.focus();
    }
    
    async checkConfig() {
        const configUrl = `${this.apiBase}/api/config`;
        console.log('Checking config at:', configUrl);
        
        try {
            const response = await fetch(configUrl);
            console.log('Config response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('Config data:', data);
            
            if (data.success && data.has_deployment_id && data.has_api_token) {
                this.setStatus('connected', '接続済み');
            } else {
                this.setStatus('warning', '設定が不完全です');
                this.addSystemMessage('警告: DataRobot設定が不完全です。環境変数を確認してください。');
            }
        } catch (error) {
            console.error('Config check error:', error);
            this.setStatus('error', '接続エラー');
            this.addSystemMessage(`エラー: ${error.message}`);
        }
    }
    
    setStatus(status, text) {
        this.statusIndicator.className = `status-indicator status-${status}`;
        this.statusText.textContent = text;
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isProcessing) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        
        // Disable input while processing
        this.setProcessing(true);
        
        const chatUrl = `${this.apiBase}/api/chat`;
        console.log('Sending message to:', chatUrl);
        
        // Add thinking indicator
        const thinkingId = this.addThinkingIndicator();
        
        try {
            // Send message to API for streaming response
            const response = await fetch(chatUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            console.log('Chat response status:', response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            // ストリーミングレスポンスを処理
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = '';
            let messageDiv = null;
            let hasReceivedContent = false;  // コンテンツを受信したかのフラグ
            
            // まだ「考え中」を表示（ハートビート受信中）
            
            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                const chunk = decoder.decode(value, { stream: true });
                const lines = chunk.split('\n');
                
                for (const line of lines) {
                    // SSEコメント（ハートビート）をチェック
                    if (line.startsWith(':')) {
                        // ハートビート受信 - 「考え中」を継続表示
                        console.log('Heartbeat received, agent is processing...');
                        continue;
                    }
                    
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6).trim();
                        
                        if (data === '[DONE]') continue;
                        if (data === '') continue;
                        
                        try {
                            const parsed = JSON.parse(data);
                            
                            if (parsed.error) {
                                throw new Error(parsed.error);
                            }
                            
                            if (parsed.content) {
                                // 最初のコンテンツを受信したら「考え中」を削除
                                if (!hasReceivedContent) {
                                    this.removeThinkingIndicator(thinkingId);
                                    hasReceivedContent = true;
                                }
                                
                                assistantMessage += parsed.content;
                                
                                // メッセージを更新または作成
                                if (!messageDiv) {
                                    messageDiv = this.addMessageForStreaming('', 'bot');
                                }
                                const contentDiv = messageDiv.querySelector('.message-content');
                                contentDiv.innerHTML = `<strong>エージェント:</strong> ${this.formatMessage(assistantMessage)}`;
                                this.scrollToBottom();
                            }
                        } catch (e) {
                            console.error('Parse error:', e, 'Data:', data);
                        }
                    }
                }
            }
            
            // ストリーミングが完了したら「考え中」を削除（念のため）
            this.removeThinkingIndicator(thinkingId);
            
            // ストリーミングが完了したらメッセージを確定
            if (!messageDiv || !assistantMessage) {
                this.addSystemMessage('エラー: レスポンスが空でした。');
            }
            
        } catch (error) {
            console.error('Chat error:', error);
            this.removeThinkingIndicator(thinkingId);
            
            if (error.message.includes('504')) {
                this.addSystemMessage('エラー: サーバーの処理に時間がかかりすぎています。');
            } else {
                this.addSystemMessage(`通信エラー: ${error.message}`);
            }
        } finally {
            this.setProcessing(false);
            this.messageInput.focus();
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const label = sender === 'user' ? 'You' : 'Agent';
        const labelJa = sender === 'user' ? 'あなた' : 'エージェント';
        
        // Format message content (preserve line breaks and markdown-like formatting)
        const formattedContent = this.formatMessage(content);
        
        contentDiv.innerHTML = `<strong>${labelJa}:</strong> ${formattedContent}`;
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addMessageForStreaming(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        const labelJa = sender === 'user' ? 'あなた' : 'エージェント';
        const formattedContent = this.formatMessage(content);
        
        contentDiv.innerHTML = `<strong>${labelJa}:</strong> ${formattedContent}`;
        messageDiv.appendChild(contentDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        return messageDiv;
    }
    
    addSystemMessage(content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = content;
        
        messageDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    addThinkingIndicator() {
        const thinkingDiv = document.createElement('div');
        const thinkingId = `thinking-${Date.now()}`;
        thinkingDiv.id = thinkingId;
        thinkingDiv.className = 'message bot-message thinking';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = '<strong>エージェント:</strong> <span class="thinking-dots">考え中<span>.</span><span>.</span><span>.</span></span>';
        
        thinkingDiv.appendChild(contentDiv);
        this.chatMessages.appendChild(thinkingDiv);
        this.scrollToBottom();
        
        return thinkingId;
    }
    
    removeThinkingIndicator(thinkingId) {
        if (thinkingId) {
            const element = document.getElementById(thinkingId);
            if (element) {
                element.remove();
            }
        } else {
            // Remove any thinking indicator
            const thinking = this.chatMessages.querySelector('.thinking');
            if (thinking) {
                thinking.remove();
            }
        }
    }
    
    formatMessage(content) {
        // Escape HTML
        const div = document.createElement('div');
        div.textContent = content;
        let formatted = div.innerHTML;
        
        // Convert newlines to <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Simple markdown-like formatting
        // Bold: **text** or __text__
        formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        formatted = formatted.replace(/__(.+?)__/g, '<strong>$1</strong>');
        
        // Italic: *text* or _text_
        formatted = formatted.replace(/\*(.+?)\*/g, '<em>$1</em>');
        formatted = formatted.replace(/_(.+?)_/g, '<em>$1</em>');
        
        return formatted;
    }
    
    setProcessing(processing) {
        this.isProcessing = processing;
        this.messageInput.disabled = processing;
        this.sendButton.disabled = processing;
        this.sendButton.textContent = processing ? '送信中...' : '送信';
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
}

// Initialize the chat app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});