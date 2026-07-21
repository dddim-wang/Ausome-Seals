import React, { useEffect, useRef, useState } from "react";
import {
  MessageCircle,
  SendHorizontal,
  Sparkles,
  Square,
  X,
} from "lucide-react";

import "./chat.css";


const API_BASE = (import.meta.env.VITE_API_BASE || "").replace(/\/$/, "");

const copy = {
  en: {
    open: "Ask Ausome AI",
    close: "Close AI assistant",
    title: "Ausome AI Assistant",
    subtitle: "Seal selection support",
    greeting: "Hello! Tell me the seal size, equipment, medium, pressure, and temperature. I’ll help you narrow down the options.",
    placeholder: "Describe your sealing requirement…",
    send: "Send message",
    stop: "Stop response",
    thinking: "Reviewing your requirements…",
    error: "The AI assistant is unavailable right now. Please try again.",
    disclaimer: "AI guidance is for reference. Final selection should be confirmed against operating conditions.",
  },
  zh: {
    open: "咨询 Ausome AI",
    close: "关闭 AI 助手",
    title: "Ausome AI 助手",
    subtitle: "密封选型支持",
    greeting: "您好！请告诉我密封件尺寸、设备、介质、压力和温度，我会协助您缩小选型范围。",
    placeholder: "描述您的密封需求…",
    send: "发送消息",
    stop: "停止回答",
    thinking: "正在分析您的需求…",
    error: "AI 助手暂时不可用，请稍后重试。",
    disclaimer: "AI 建议仅供参考，最终选型需结合实际工况确认。",
  },
};

function parseSseEvent(block) {
  let event = "message";
  const data = [];

  block.split(/\r?\n/).forEach((line) => {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    if (line.startsWith("data:")) data.push(line.slice(5).trim());
  });

  return { event, data: data.join("\n") };
}

function makeId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export default function ChatWidget({ lang }) {
  const t = copy[lang] || copy.en;
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState("");
  const abortRef = useRef(null);
  const inputRef = useRef(null);
  const panelRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const shouldAutoScrollRef = useRef(true);

  useEffect(() => {
    if (isOpen) inputRef.current?.focus();
  }, [isOpen]);

  useEffect(() => {
    const container = messagesContainerRef.current;
    if (!container || !shouldAutoScrollRef.current) return undefined;

    const animationFrame = window.requestAnimationFrame(() => {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: isStreaming ? "auto" : "smooth",
      });
    });

    return () => window.cancelAnimationFrame(animationFrame);
  }, [messages, isStreaming, isOpen]);

  useEffect(() => () => abortRef.current?.abort(), []);

  useEffect(() => {
    if (!isOpen) return undefined;

    const panel = panelRef.current;
    const handleWheel = (event) => {
      const messagesContainer = messagesContainerRef.current;
      if (!messagesContainer) return;

      event.preventDefault();
      event.stopPropagation();
      messagesContainer.scrollTop += event.deltaY;
    };

    panel?.addEventListener("wheel", handleWheel, { passive: false });
    return () => panel?.removeEventListener("wheel", handleWheel);
  }, [isOpen]);

  const stopStreaming = () => {
    abortRef.current?.abort();
  };

  const appendDelta = (assistantId, content) => {
    setMessages((current) => current.map((message) => (
      message.id === assistantId
        ? { ...message, content: message.content + content }
        : message
    )));
  };

  async function sendMessage(event) {
    event?.preventDefault();
    const content = input.trim();
    if (!content || isStreaming) return;

    shouldAutoScrollRef.current = true;
    const userMessage = { id: makeId("user"), role: "user", content };
    const assistantId = makeId("assistant");
    const history = [...messages, userMessage];
    setMessages([...history, {
      id: assistantId,
      role: "assistant",
      content: "",
      pending: true,
    }]);
    setInput("");
    setError("");
    setIsStreaming(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(`${API_BASE}/api/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...(conversationId ? { conversation_id: conversationId } : {}),
          messages: history.map(({ role, content: messageContent }) => ({
            role,
            content: messageContent,
          })),
        }),
        signal: controller.signal,
      });

      if (!response.ok || !response.body) {
        throw new Error("Unable to start AI stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        buffer += decoder.decode(value || new Uint8Array(), { stream: !done });
        const blocks = buffer.split(/\r?\n\r?\n/);
        buffer = blocks.pop() || "";

        for (const block of blocks) {
          if (!block.trim()) continue;
          const parsed = parseSseEvent(block);
          const data = parsed.data ? JSON.parse(parsed.data) : {};

          if (parsed.event === "meta" && data.conversation_id) {
            setConversationId(data.conversation_id);
            if (Array.isArray(data.sources)) {
              setMessages((current) => current.map((message) => (
                message.id === assistantId
                  ? { ...message, sources: data.sources }
                  : message
              )));
            }
          } else if (parsed.event === "delta" && data.content) {
            appendDelta(assistantId, data.content);
          } else if (parsed.event === "error") {
            throw new Error(data.message || "AI stream interrupted");
          }
        }

        if (done) break;
      }
    } catch (streamError) {
      if (streamError.name !== "AbortError") {
        setError(t.error);
      }
    } finally {
      setMessages((current) => current.map((message) => (
        message.id === assistantId ? { ...message, pending: false } : message
      )).filter((message) => message.id !== assistantId || message.content));
      setIsStreaming(false);
      abortRef.current = null;
    }
  }

  return (
    <div className={isOpen ? "ai-chat open" : "ai-chat"}>
      <section
        className="ai-chat-panel"
        ref={panelRef}
        role="dialog"
        aria-label={t.title}
        aria-hidden={!isOpen}
        inert={!isOpen}
      >
          <header className="ai-chat-header">
            <span className="ai-chat-mark" aria-hidden="true">
              <Sparkles size={33} />
            </span>
            <div>
              <strong>{t.title}</strong>
              <span>{t.subtitle}</span>
            </div>
            <button type="button" onClick={() => setIsOpen(false)} aria-label={t.close}>
              <X size={19} />
            </button>
          </header>

          <div
            className="ai-chat-messages"
            aria-live="polite"
            ref={messagesContainerRef}
            onScroll={(event) => {
              const container = event.currentTarget;
              const distanceFromBottom = (
                container.scrollHeight - container.scrollTop - container.clientHeight
              );
              shouldAutoScrollRef.current = distanceFromBottom < 56;
            }}
          >
            <div className="ai-message assistant">
              <span>{t.greeting}</span>
            </div>
            {messages.map((message) => (
              <div className={`ai-message ${message.role}`} key={message.id}>
                {message.content && <span>{message.content}</span>}
                {message.sources?.length > 0 && (
                  <div className="ai-message-sources" aria-label="Knowledge sources">
                    {message.sources.map((source) => (
                      <small key={`${source.source}-${source.page}`}>
                        {source.source.replace(/\.pdf$/i, "")} · p.{source.page}
                      </small>
                    ))}
                  </div>
                )}
                {message.pending && !message.content && (
                  <span className="ai-typing">
                    <i /> <i /> <i />
                    <em>{t.thinking}</em>
                  </span>
                )}
              </div>
            ))}
            {error && <p className="ai-chat-error" role="alert">{error}</p>}
          </div>

          <form className="ai-chat-composer" onSubmit={sendMessage}>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  sendMessage(event);
                }
              }}
              placeholder={t.placeholder}
              maxLength={2000}
              rows={1}
              disabled={isStreaming}
            />
            <button
              type={isStreaming ? "button" : "submit"}
              onClick={isStreaming ? stopStreaming : undefined}
              disabled={!isStreaming && !input.trim()}
              aria-label={isStreaming ? t.stop : t.send}
              title={isStreaming ? t.stop : t.send}
            >
              {isStreaming ? <Square size={17} /> : <SendHorizontal size={18} />}
            </button>
          </form>
          <p className="ai-chat-disclaimer">{t.disclaimer}</p>
      </section>

      <button
        className="ai-chat-toggle"
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        aria-expanded={isOpen}
        aria-label={isOpen ? t.close : t.open}
        title={isOpen ? t.close : t.open}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={25} />}
        {!isOpen && <span>{t.open}</span>}
      </button>
    </div>
  );
}
