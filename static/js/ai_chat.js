/**
 * TVHUB — AI Movie Recommendation Chat
 */
var _chatOpen = false;

function toggleChat() {
    _chatOpen = !_chatOpen;
    var win = document.getElementById('ai-chat-window');
    var btn = document.getElementById('ai-chat-toggle');
    if (_chatOpen) {
        win.style.display = 'block';
        btn.innerHTML = '<i class="bi bi-x-lg"></i>';
        document.getElementById('ai-msg-input').focus();
    } else {
        win.style.display = 'none';
        btn.innerHTML = '<i class="bi bi-robot"></i>';
    }
}

function appendMessage(role, html) {
    var container = document.getElementById('ai-chat-messages');
    var wrapper = document.createElement('div');
    wrapper.className = role === 'user' ? 'user-msg' : 'ai-msg';
    var bubble = document.createElement('div');
    bubble.className = 'msg-bubble ' + role;
    bubble.innerHTML = html;
    wrapper.appendChild(bubble);
    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
    return wrapper;
}

function showTyping() {
    var container = document.getElementById('ai-chat-messages');
    var wrapper = document.createElement('div');
    wrapper.className = 'ai-msg';
    wrapper.id = 'typing-indicator';
    wrapper.innerHTML = '<div class="msg-bubble ai"><div class="typing-dots"><span></span><span></span><span></span></div></div>';
    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
}

function hideTyping() {
    var el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

function sendAiMessage() {
    var input = document.getElementById('ai-msg-input');
    var msg = (input.value || '').trim();
    if (!msg) return;

    // Show user message
    appendMessage('user', escapeHtml(msg));
    input.value = '';
    input.disabled = true;
    document.getElementById('ai-send-btn').disabled = true;

    showTyping();

    fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
    })
        .then(function (r) { return r.json(); })
        .then(function (data) {
            hideTyping();
            if (data.error) {
                appendMessage('ai', '❌ ' + escapeHtml(data.error));
            } else {
                // Build nice response
                var html = '';
                if (data.intro) {
                    html += '<p>' + escapeHtml(data.intro) + '</p>';
                }
                if (data.recommendations && data.recommendations.length) {
                    data.recommendations.forEach(function (rec) {
                        html += '<div class="rec-card">';
                        html += '<strong>🎬 ' + escapeHtml(rec.title) + '</strong>';
                        if (rec.rating) html += ' ⭐ ' + rec.rating;
                        html += '<br>';
                        if (rec.reason) html += '<small>' + escapeHtml(rec.reason) + '</small><br>';
                        if (rec.slug) {
                            html += '<a href="/reviews/movies/' + encodeURIComponent(rec.slug) + '">อ่านรีวิว →</a>';
                        }
                        html += '</div>';
                    });
                }
                if (data.outro) {
                    html += '<p class="mt-2">' + escapeHtml(data.outro) + '</p>';
                }
                if (!html) html = escapeHtml(JSON.stringify(data));
                appendMessage('ai', html);
            }
        })
        .catch(function (err) {
            hideTyping();
            appendMessage('ai', '❌ เกิดข้อผิดพลาด: ' + escapeHtml(err.message));
        })
        .finally(function () {
            input.disabled = false;
            document.getElementById('ai-send-btn').disabled = false;
            input.focus();
        });
}

function escapeHtml(t) {
    if (!t) return '';
    var d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}

// Enter key to send
document.addEventListener('DOMContentLoaded', function () {
    var input = document.getElementById('ai-msg-input');
    if (input) {
        input.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') sendAiMessage();
        });
    }
});
