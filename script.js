(function () {
    // Aponte para onde o backend Flask está rodando.
    // Local: http://127.0.0.1:5001 | Produção: https://seudominio.com/api
    const API_URL = "http://127.0.0.1:5001/api/chat";

    const messagesEl = document.getElementById("td-messages");
    const formEl = document.getElementById("td-form");
    const inputEl = document.getElementById("td-input");
    const sendEl = document.getElementById("td-send");

   
    const sessionId =
      sessionStorage.getItem("td-session-id") ||
      (() => {
        const id = "sess-" + Math.random().toString(36).slice(2);
        sessionStorage.setItem("td-session-id", id);
        return id;
      })();

    function addMessage(text, type) {
      const div = document.createElement("div");
      div.className = "td-msg td-msg-" + type;
      div.textContent = text;
      messagesEl.appendChild(div);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return div;
    }

    formEl.addEventListener("submit", async function (e) {
      e.preventDefault();
      const question = inputEl.value.trim();
      if (!question) return;

      addMessage(question, "user");
      inputEl.value = "";
      sendEl.disabled = true;

      const loadingEl = addMessage("digitando...", "loading");

      try {
        const res = await fetch(API_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: question, session_id: sessionId }),
        });

        const data = await res.json();
        loadingEl.remove();

        if (!res.ok) {
          addMessage(data.error || "Erro ao buscar resposta.", "error");
        } else {
          addMessage(data.reply, "bot");
        }
      } catch (err) {
        loadingEl.remove();
        addMessage(
          "Não consegui falar com o servidor. Verifique se o backend está rodando.",
          "error"
        );
      } finally {
        sendEl.disabled = false;
        inputEl.focus();
      }
    });
  })();