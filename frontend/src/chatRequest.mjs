export const MAX_CHAT_REQUEST_BYTES = 28_000;
export const MAX_CHAT_HISTORY_MESSAGES = 20;

const encoder = new TextEncoder();

function requestSize(payload) {
  return encoder.encode(JSON.stringify(payload)).length;
}

function makePayload(messages, conversationId) {
  return {
    ...(conversationId ? { conversation_id: conversationId } : {}),
    messages,
  };
}

export function buildChatPayload(history, conversationId = "") {
  const messages = history.map(({ role, content }) => ({ role, content }));
  let start = Math.max(0, messages.length - MAX_CHAT_HISTORY_MESSAGES);

  if (messages[start]?.role === "assistant" && start < messages.length - 1) {
    start += 1;
  }

  let payload = makePayload(messages.slice(start), conversationId);
  while (
    requestSize(payload) > MAX_CHAT_REQUEST_BYTES
    && start < messages.length - 1
  ) {
    start += 1;
    if (messages[start]?.role === "assistant" && start < messages.length - 1) {
      start += 1;
    }
    payload = makePayload(messages.slice(start), conversationId);
  }

  return payload;
}

export function isChatPayloadTooLarge(payload) {
  return requestSize(payload) > MAX_CHAT_REQUEST_BYTES;
}
