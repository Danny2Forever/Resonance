
document.addEventListener('DOMContentLoaded', () => {

    let currentChatId = null;

    const currentUserId = JSON.parse(document.getElementById('current-user-id').textContent);

    const messagesContainer = document.getElementById('messagesContainer');
    const emptyState = document.getElementById('emptyState');
    const chatWindow = document.getElementById('chatWindow');
    const chatNameEl = document.getElementById('chatName');
    const chatAvatarEl = document.getElementById('chatAvatar');
    const messageInput = document.getElementById('messageInput');
    const messageForm = document.querySelector('footer form');
    const chatListContainer = document.getElementById('chat-list-container');

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function renderMessage(message) {
        const messageDiv = document.createElement('div');
        const isSent = message.sender_id === currentUserId;
        messageDiv.className = isSent ? 'flex justify-end' : 'flex justify-start';

        const messageBubble = document.createElement('div');
        messageBubble.className = isSent 
            ? 'bg-green-600 text-white rounded-2xl rounded-br-none p-4 max-w-xs'
            : 'bg-[#1a1f3a] text-white rounded-2xl rounded-bl-none p-4 max-w-xs';
        
        if (message.message_type === 'text') {
            messageBubble.textContent = message.content;
        } else if (message.message_type === 'song') {
            messageBubble.innerHTML = `<strong>Shared a song:</strong> ${message.content}`;
        }
        
        messageDiv.appendChild(messageBubble);
        messagesContainer.appendChild(messageDiv);
    }

    function selectChat(chatElement) {
        const chatId = chatElement.dataset.chatId;
        const name = chatElement.dataset.chatName;
        const avatar = chatElement.dataset.chatAvatar;

        currentChatId = chatId;

        chatNameEl.textContent = name;
        chatAvatarEl.src = avatar;

        messagesContainer.innerHTML = '<p class="text-center text-gray-400">Loading messages...</p>';

        fetch(`/chat/api/${chatId}/`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to fetch messages.');
                return response.json();
            })
            .then(messages => {
                messagesContainer.innerHTML = '';
                messages.forEach(renderMessage);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            })
            .catch(error => {
                messagesContainer.innerHTML = `<p class="text-red-500 text-center">${error.message}</p>`;
            });

        document.querySelectorAll('.chat-item').forEach(item => {
            item.classList.remove('bg-green-600/20');
        });
        chatElement.classList.add('bg-green-600/20');

        emptyState.classList.add('hidden');
        chatWindow.classList.remove('hidden');
    }

    async function sendMessage(event) {
        event.preventDefault();
        if (!currentChatId) return;

        const messageText = messageInput.value.trim();
        if (!messageText) return;

        const messageData = {
            content: messageText,
            message_type: 'text'
        };

        try {
            const response = await fetch(`/chat/api/${currentChatId}/send/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(messageData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                console.error('Validation Error:', errorData);
                throw new Error('Failed to send message.');
            }
            
            const newMessage = await response.json();
            renderMessage(newMessage);
            messageInput.value = '';
            messagesContainer.scrollTop = messagesContainer.scrollHeight;

        } catch (error) {
            console.error(error);
        }
    }

    chatListContainer.addEventListener('click', (event) => {
        const chatButton = event.target.closest('.chat-item');
        if (chatButton) {
            selectChat(chatButton);
        }
    });

    messageForm.addEventListener('submit', sendMessage);
});