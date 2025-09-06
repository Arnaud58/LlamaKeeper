// Backend Configuration
const BACKEND_URL = window.BACKEND_URL || 'http://localhost:8000';

// API Utility Functions
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${BACKEND_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API call to ${endpoint} failed:`, error);
        throw error;
    }
}

// WebSocket Connection Management
class StoryWebSocket {
    constructor(onMessageCallback) {
        this.socket = null;
        this.onMessageCallback = onMessageCallback;
        this.subscriptions = new Set();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        // Construct WebSocket URL dynamically
        const backendUrl = new URL(BACKEND_URL);
        const protocol = backendUrl.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = backendUrl.host;
        const wsUrl = `${protocol}//${host}/ws/stories`;

        this.socket = new WebSocket(wsUrl);

        this.socket.onopen = () => {
            console.log('WebSocket connection established');
            this.reconnectAttempts = 0;
            
            // Resubscribe to previous stories
            this.subscriptions.forEach(storyId => {
                this.subscribeToStory(storyId);
            });
        };

        this.socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                // Handle different message types
                switch(data.type) {
                    case 'story_update':
                        this.onMessageCallback(data);
                        break;
                    case 'subscription_confirmed':
                        console.log(`Subscribed to story ${data.story_id}`);
                        break;
                    case 'unsubscription_confirmed':
                        console.log(`Unsubscribed from story ${data.story_id}`);
                        break;
                    default:
                        console.log('Received unknown message type:', data);
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        this.socket.onclose = (event) => {
            console.log('WebSocket connection closed:', event);
            
            // Attempt reconnection with exponential backoff
            if (this.reconnectAttempts < this.maxReconnectAttempts) {
                const timeout = Math.pow(2, this.reconnectAttempts) * 1000;
                this.reconnectAttempts++;
                
                setTimeout(() => {
                    console.log(`Attempting to reconnect (Attempt ${this.reconnectAttempts})`);
                    this.connect();
                }, timeout);
            } else {
                console.error('Max reconnection attempts reached');
            }
        };

        this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    subscribeToStory(storyId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'subscribe',
                story_id: storyId
            }));
            this.subscriptions.add(storyId);
        }
    }

    unsubscribeFromStory(storyId) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'unsubscribe',
                story_id: storyId
            }));
            this.subscriptions.delete(storyId);
        }
    }

    sendStoryAction(storyId, actionData) {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'action',
                story_id: storyId,
                action: actionData
            }));
        }
    }

    close() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

// Global WebSocket instance
let storyWebSocket = null;

// Initialize WebSocket on page load
document.addEventListener('DOMContentLoaded', () => {
    storyWebSocket = new StoryWebSocket((message) => {
        // Global message handler
        console.log('Received story update:', message);
        
        // Example: Update UI based on story update
        const storyUpdateEvent = new CustomEvent('story-update', { 
            detail: message 
        });
        document.dispatchEvent(storyUpdateEvent);
    });

    storyWebSocket.connect();
});

// Expose WebSocket methods globally for use in other scripts
window.storyWebSocket = {
    subscribe: (storyId) => storyWebSocket.subscribeToStory(storyId),
    unsubscribe: (storyId) => storyWebSocket.unsubscribeFromStory(storyId),
    sendAction: (storyId, actionData) => storyWebSocket.sendStoryAction(storyId, actionData)
};