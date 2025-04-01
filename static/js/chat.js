document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = messageForm ? messageForm.querySelector('button[type="submit"]') : null;

    if (messageForm && messageInput && sendButton) {
        // Function to send message
        const sendMessage = async () => {
            const content = messageInput.value.trim();
            if (!content) return;

            // Disable input and button while sending
            messageInput.disabled = true;
            sendButton.disabled = true;

            try {
                const formData = new FormData(messageForm);
                const response = await fetch(messageForm.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                if (data.status === 'success') {
                    // Clear input
                    messageInput.value = '';
                    
                    // Add message to chat
                    const messageHtml = `
                        <div class="chat-message mb-3 chat-message-self">
                            <div class="d-flex align-items-start">
                                <div class="ms-auto">
                                    <div class="message-content p-2 rounded bg-primary text-white">
                                        ${data.message.content}
                                    </div>
                                    <div class="message-info d-flex justify-content-between align-items-center mt-1">
                                        <small class="text-muted">${data.message.user_name}</small>
                                        <small class="text-muted">${new Date(data.message.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</small>
                                    </div>
                                </div>
                                <img src="/static/images/profiles/${data.message.user_profile_pic || 'default.png'}" class="rounded-circle ms-2" width="32" height="32" alt="${data.message.user_name}">
                            </div>
                        </div>
                    `;
                    chatMessages.insertAdjacentHTML('beforeend', messageHtml);
                    
                    // Scroll to bottom
                    chatMessages.scrollTop = chatMessages.scrollHeight;
                }
            } catch (error) {
                console.error('Error sending message:', error);
                alert('Failed to send message. Please try again.');
            } finally {
                // Re-enable input and button
                messageInput.disabled = false;
                sendButton.disabled = false;
                messageInput.focus();
            }
        };

        // Handle enter key press
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Handle form submission
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });

        // Setup periodic refresh for new messages
        let lastMessageTime = '';
        const fetchNewMessages = async () => {
            try {
                const response = await fetch(`${messageForm.action.replace('/send/', '/messages/')}?last_time=${encodeURIComponent(lastMessageTime)}`);
                const data = await response.json();
                
                if (data.status === 'success' && data.messages.length > 0) {
                    lastMessageTime = data.messages[data.messages.length - 1].created_at;
                    data.messages.forEach(message => {
                        if (message.user_id !== parseInt(messageForm.dataset.currentUserId)) {
                            const messageHtml = `
                                <div class="chat-message mb-3">
                                    <div class="d-flex align-items-start">
                                        <img src="/static/images/profiles/${message.user_profile_pic || 'default.png'}" 
                                             class="rounded-circle me-2" width="32" height="32" alt="${message.user_name}">
                                        <div>
                                            <div class="message-content p-2 rounded bg-light">
                                                ${message.content}
                                            </div>
                                            <div class="message-info d-flex justify-content-between align-items-center mt-1">
                                                <small class="text-muted">${message.user_name}</small>
                                                <small class="text-muted">${new Date(message.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</small>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;
                            chatMessages.insertAdjacentHTML('beforeend', messageHtml);
                            chatMessages.scrollTop = chatMessages.scrollHeight;
                        }
                    });
                }
            } catch (error) {
                console.error('Error fetching messages:', error);
            }
        };

        // Poll for new messages every 3 seconds
        setInterval(fetchNewMessages, 3000);
    }
});