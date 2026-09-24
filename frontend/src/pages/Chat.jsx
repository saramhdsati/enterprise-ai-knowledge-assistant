import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

const API = "http://localhost:8000";

function Chat() {
  const [message, setMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConversationId, setActiveConversationId] = useState(null);
  const navigate = useNavigate();

  const username = localStorage.getItem("username");
  const token = localStorage.getItem("token");
  const departments = JSON.parse(localStorage.getItem("departments") || "[]");
  const departmentLabel = departments.includes("ALL")
    ? "All Departments"
    : departments.join(", ") || "No department assigned";

  const authHeader = { Authorization: `Bearer ${token}` };

  const suggestedQuestions = [
    { icon: "📋", title: "HR Policies", description: "Ask about employee policies", question: "What are the main HR policies?" },
    { icon: "🔐", title: "IT Security", description: "Ask about security procedures", question: "What are the company's IT security policies?" },
    { icon: "🏢", title: "Company Info", description: "Learn about the company", question: "Tell me about the company." },
  ];

  const loadConversations = async () => {
    try {
      const res = await fetch(`${API}/conversations`, { headers: authHeader });
      if (res.status === 401) {
        localStorage.clear();
        navigate("/login");
        return;
      }
      if (res.ok) setConversations(await res.json());
    } catch {
      // silent fail — sidebar just stays empty
    }
  };

  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const openConversation = async (id) => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/conversations/${id}`, { headers: authHeader });
      if (!res.ok) throw new Error();
      const data = await res.json();
      setChatHistory(data.messages);
      setActiveConversationId(id);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const startNewConversation = () => {
    setChatHistory([]);
    setActiveConversationId(null);
  };

  const handleSuggestionClick = (question) => setMessage(question);

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  const sendMessage = async () => {
    if (!message.trim() || loading) return;

    const userQuestion = message;
    setChatHistory((prev) => [...prev, { role: "user", text: userQuestion }]);
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch(`${API}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...authHeader,
        },
        body: JSON.stringify({
          question: userQuestion,
          conversation_id: activeConversationId,
        }),
      });

      if (response.status === 401) {
        localStorage.clear();
        navigate("/login");
        return;
      }
      if (!response.ok) throw new Error("API request failed");

      const data = await response.json();
      setChatHistory((prev) => [...prev, { role: "assistant", text: data.answer, sources: data.sources }]);

      const isNewConversation = !activeConversationId;
      setActiveConversationId(data.conversation_id);
      if (isNewConversation) loadConversations();
      else {
        setConversations((prev) =>
          prev.map((c) => (c.id === data.conversation_id ? { ...c, updated_at: new Date().toISOString() } : c))
            .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
        );
      }
    } catch (error) {
      setChatHistory((prev) => [...prev, { role: "assistant", text: "⚠️ Error connecting to the server." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">✦</div>
          <div>
            <h2>NovaBridge AI</h2>
            <span>Enterprise Knowledge</span>
          </div>
        </div>

        <button className="new-chat" onClick={startNewConversation}>
          <span>＋</span> New conversation
        </button>

        <div className="sidebar-section">
          <p className="section-title">RECENT CHATS</p>
          {conversations.length === 0 && (
            <p style={{ color: "#555c69", fontSize: "11px", padding: "0 11px" }}>No conversations yet</p>
          )}
          {conversations.map((c) => (
            <button
              key={c.id}
              className={`conversation ${c.id === activeConversationId ? "active" : ""}`}
              onClick={() => openConversation(c.id)}
            >
              <span>💬</span>
              {c.title}
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">
          <div className="user-avatar">{username?.[0]?.toUpperCase()}</div>
          <div className="user-info">
            <strong>{username}</strong>
            <span>{departmentLabel}</span>
          </div>
          <button className="settings" onClick={handleLogout}>⎋</button>
        </div>
      </aside>

      <main className="chat-area">
        <header className="topbar">
          <div>
            <h1>Knowledge Assistant</h1>
            <p>Enterprise AI-powered knowledge search</p>
          </div>
          <div className="status">
            <span className="status-dot"></span> Online
          </div>
        </header>

        {chatHistory.length === 0 ? (
          <section className="welcome">
            <div className="welcome-icon">✦</div>
            <h2>How can I help you?</h2>
            <p>Ask questions about your company's policies, procedures, and documentation.</p>

            <div className="suggestions">
              {suggestedQuestions.map((item) => (
                <button className="suggestion-card" key={item.title} onClick={() => handleSuggestionClick(item.question)}>
                  <div className="suggestion-icon">{item.icon}</div>
                  <div className="suggestion-content">
                    <strong>{item.title}</strong>
                    <span>{item.description}</span>
                  </div>
                  <span className="arrow">→</span>
                </button>
              ))}
            </div>
          </section>
        ) : (
          <section style={{ flex: 1, overflowY: "auto", padding: "24px 34px" }}>
            {chatHistory.map((msg, i) => (
              <div key={i} style={{ marginBottom: "20px", textAlign: msg.role === "user" ? "right" : "left" }}>
                <div style={{ display: "inline-block", maxWidth: "70%", padding: "12px 16px", borderRadius: "12px", background: msg.role === "user" ? "#8b5cf6" : "#181b24", color: "#f4f5f7", fontSize: "14px", lineHeight: "1.6", textAlign: "left" }}>
                  {msg.text}
                  {msg.sources?.length > 0 && (
                    <div style={{ marginTop: "8px", fontSize: "11px", color: "#858b99" }}>📄 {msg.sources.join(", ")}</div>
                  )}
                </div>
              </div>
            ))}
            {loading && <div style={{ color: "#858b99", fontSize: "13px" }}>Thinking...</div>}
          </section>
        )}

        <div className="input-wrapper">
          <div className="input-box">
            <textarea value={message} onChange={(e) => setMessage(e.target.value)} onKeyDown={handleKeyDown} placeholder="Ask a question about your company..." rows="1" />
            <button className="send-button" disabled={!message.trim() || loading} onClick={sendMessage}>↑</button>
          </div>
          <p className="input-hint">AI responses are based on your company's knowledge base.</p>
        </div>
      </main>
    </div>
  );
}

export default Chat;