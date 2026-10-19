document.addEventListener("DOMContentLoaded", function () {
    const chatContainer = document.getElementById("chat-messages");
    const chatInput = document.getElementById("chat-input");
    const sendBtn = document.getElementById("btn-send-message");
    const quickCmdBtns = document.querySelectorAll(".quick-cmd-btn");
    const contextJobInput = document.getElementById("context-job-id");

    function appendMessage(sender, text, cards = []) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `d-flex mb-3 ${sender === "user" ? "justify-content-end" : "justify-content-start"}`;

        const bubble = document.createElement("div");
        bubble.className = `p-3 rounded-3 ${sender === "user" ? "bg-primary text-white" : "bg-white border text-dark"}`;
        bubble.style.maxWidth = "80%";

        // Convert basic markdown formatting
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\*(.*?)\*/g, "<em>$1</em>")
            .replace(/```text\n([\s\S]*?)```/g, "<pre class='bg-light text-dark p-2 rounded border'><code>$1</code></pre>")
            .replace(/\n/g, "<br>");

        bubble.innerHTML = formatted;

        // Render job cards if any
        if (cards && cards.length > 0) {
            const cardDeck = document.createElement("div");
            cardDeck.className = "mt-3 d-flex flex-column gap-2";
            cards.forEach(card => {
                const cardEl = document.createElement("div");
                cardEl.className = "card p-2 border-start border-4 border-primary shadow-sm";
                cardEl.innerHTML = `
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6 class="mb-0 fw-bold">${card.title}</h6>
                            <small class="text-muted">${card.company} · ${card.location || 'Remote'}</small>
                        </div>
                        ${card.match_score ? `<span class="badge bg-success">${Math.round(card.match_score)}% Match</span>` : ''}
                    </div>
                    ${card.explanation ? `<small class="text-muted mt-1 d-block">${card.explanation}</small>` : ''}
                    <div class="mt-2 d-flex gap-2">
                        <a href="/jobs/${card.id}" class="btn btn-sm btn-outline-secondary">Details</a>
                        <a href="${card.apply_url}" target="_blank" class="btn btn-sm btn-primary">Apply Now <i class="bi bi-box-arrow-up-right"></i></a>
                    </div>
                `;
                cardDeck.appendChild(cardEl);
            });
            bubble.appendChild(cardDeck);
        }

        msgDiv.appendChild(bubble);
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function sendMessage(msgText) {
        const text = msgText || (chatInput ? chatInput.value.trim() : "");
        if (!text) return;

        appendMessage("user", text);
        if (chatInput) chatInput.value = "";

        // Typing indicator
        const typingId = "typing-" + Date.now();
        const typingDiv = document.createElement("div");
        typingDiv.id = typingId;
        typingDiv.className = "d-flex mb-3 justify-content-start";
        typingDiv.innerHTML = `
            <div class="p-3 bg-white border rounded-3 text-muted">
                <span class="spinner-grow spinner-grow-sm me-2" role="status"></span> Thinking...
            </div>
        `;
        chatContainer.appendChild(typingDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;

        const contextJobId = contextJobInput ? contextJobInput.value : null;

        fetch("/assistant/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: text,
                context_job_id: contextJobId ? parseInt(contextJobId) : null
            })
        })
        .then(res => res.json())
        .then(data => {
            const el = document.getElementById(typingId);
            if (el) el.remove();

            if (data.success && data.data) {
                appendMessage("assistant", data.data.reply, data.data.cards);
            } else {
                appendMessage("assistant", "Sorry, I encountered an issue processing that command. Please try again.");
            }
        })
        .catch(err => {
            const el = document.getElementById(typingId);
            if (el) el.remove();
            appendMessage("assistant", "Connection error. Please check your network and try again.");
            console.error(err);
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener("click", () => sendMessage());
    }

    if (chatInput) {
        chatInput.addEventListener("keypress", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    quickCmdBtns.forEach(btn => {
        btn.addEventListener("click", function () {
            const cmd = this.getAttribute("data-cmd");
            if (cmd) sendMessage(cmd);
        });
    });
});
