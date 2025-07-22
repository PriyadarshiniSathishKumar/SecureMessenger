/**
 * Chat JavaScript Functionality
 * Handles real-time messaging updates and UI interactions
 */

class ChatManager {
    constructor() {
        this.currentRoom = null;
        this.messageContainer = null;
        this.messageInput = null;
        this.isRefreshing = false;
        
        this.init();
    }
    
    init() {
        // Get DOM elements
        this.messageContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        
        // Extract room ID from URL or form
        const roomInput = document.querySelector('input[name="room_id"]');
        if (roomInput) {
            this.currentRoom = roomInput.value;
        }
        
        // Bind events
        this.bindEvents();
        
        // Start auto-refresh
        this.startAutoRefresh();
        
        console.log('ChatManager initialized for room:', this.currentRoom);
    }
    
    bindEvents() {
        // Message form submission
        const messageForm = document.getElementById('messageForm');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => {
                this.handleMessageSubmit(e);
            });
        }
        
        // Enter key handling
        if (this.messageInput) {
            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    messageForm.submit();
                }
            });
        }
        
        // Refresh button
        const refreshBtn = document.querySelector('[onclick="refreshMessages()"]');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.refreshMessages();
            });
        }
        
        // Handle window focus for refresh
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden) {
                this.refreshMessages();
            }
        });
    }
    
    handleMessageSubmit(e) {
        const message = this.messageInput.value.trim();
        if (!message) {
            e.preventDefault();
            return false;
        }
        
        // Disable input during submission
        this.messageInput.disabled = true;
        
        // Re-enable after a short delay (form will submit)
        setTimeout(() => {
            if (this.messageInput) {
                this.messageInput.disabled = false;
                this.messageInput.value = '';
            }
        }, 100);
        
        return true;
    }
    
    async refreshMessages() {
        if (this.isRefreshing || !this.currentRoom) {
            return;
        }
        
        this.isRefreshing = true;
        const refreshIcon = document.getElementById('refresh-icon');
        
        try {
            // Show loading state
            if (refreshIcon) {
                refreshIcon.style.animation = 'spin 1s linear infinite';
            }
            
            // Fetch latest messages
            const response = await fetch(`/api/messages/${this.currentRoom}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            if (data.messages) {
                this.updateMessages(data.messages);
            }
            
        } catch (error) {
            console.error('Failed to refresh messages:', error);
            // Show error indicator
            this.showError('Failed to refresh messages');
        } finally {
            // Remove loading state
            if (refreshIcon) {
                refreshIcon.style.animation = '';
            }
            this.isRefreshing = false;
        }
    }
    
    updateMessages(messages) {
        if (!this.messageContainer || !messages) {
            return;
        }
        
        const currentScrollPos = this.messageContainer.scrollTop;
        const isScrolledToBottom = currentScrollPos >= 
            (this.messageContainer.scrollHeight - this.messageContainer.clientHeight - 50);
        
        // Clear existing messages
        this.messageContainer.innerHTML = '';
        
        if (messages.length === 0) {
            this.showEmptyState();
            return;
        }
        
        // Add messages
        messages.forEach(message => {
            this.addMessageElement(message);
        });
        
        // Restore scroll position or scroll to bottom
        if (isScrolledToBottom) {
            this.scrollToBottom();
        } else {
            this.messageContainer.scrollTop = currentScrollPos;
        }
    }
    
    addMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_own ? 'message-own' : 'message-other'}`;
        
        let html = '';
        
        // Add sender name for other users' messages
        if (!message.is_own) {
            html += `<div class="message-sender">${this.escapeHtml(message.sender)}</div>`;
        }
        
        // Add message content
        html += `<div class="message-content">${this.escapeHtml(message.content)}</div>`;
        
        // Add timestamp
        const timestamp = new Date(message.timestamp);
        const timeStr = timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        html += `<div class="message-time">${timeStr}</div>`;
        
        messageDiv.innerHTML = html;
        this.messageContainer.appendChild(messageDiv);
    }
    
    showEmptyState() {
        this.messageContainer.innerHTML = `
            <div class="text-center text-muted py-5">
                <i data-feather="message-circle" style="width: 48px; height: 48px;" class="mb-3"></i>
                <p>No messages yet. Start the conversation!</p>
            </div>
        `;
        
        // Re-initialize feather icons for the new content
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show';
        errorDiv.innerHTML = `
            <i data-feather="alert-circle" class="me-2"></i>
            ${this.escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at top of page
        const container = document.querySelector('.container-fluid');
        if (container) {
            container.insertBefore(errorDiv, container.firstChild);
            
            // Re-initialize feather icons
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.remove();
                }
            }, 5000);
        }
    }
    
    scrollToBottom() {
        if (this.messageContainer) {
            this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
        }
    }
    
    startAutoRefresh() {
        // Refresh every 15 seconds when page is visible
        setInterval(() => {
            if (!document.hidden && !this.isRefreshing) {
                this.refreshMessages();
            }
        }, 15000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize chat manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatManager = new ChatManager();
});

// Global functions for backward compatibility
function refreshMessages() {
    if (window.chatManager) {
        window.chatManager.refreshMessages();
    }
}
