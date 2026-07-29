import assert from "node:assert/strict";

import {
  buildChatPayload,
  isChatPayloadTooLarge,
  MAX_CHAT_REQUEST_BYTES,
} from "../src/chatRequest.mjs";

const encoder = new TextEncoder();

const shortHistory = [{ role: "user", content: "hello" }];
const shortPayload = buildChatPayload(shortHistory, "short-conversation");
assert.deepEqual(shortPayload.messages, shortHistory);

const longHistory = [];
for (let index = 0; index < 18; index += 1) {
  longHistory.push({
    role: index % 2 ? "assistant" : "user",
    content: "x".repeat(1_900),
  });
}
longHistory.push({ role: "user", content: "latest question" });

const trimmedPayload = buildChatPayload(longHistory, "long-conversation");
const payloadBytes = encoder.encode(JSON.stringify(trimmedPayload)).length;
assert.ok(payloadBytes <= MAX_CHAT_REQUEST_BYTES);
assert.ok(trimmedPayload.messages.length < longHistory.length);
assert.equal(trimmedPayload.messages[0].role, "user");
assert.equal(trimmedPayload.messages.at(-1).content, "latest question");
assert.equal(isChatPayloadTooLarge(trimmedPayload), false);

console.log(`Chat payload checks passed (${payloadBytes}/${MAX_CHAT_REQUEST_BYTES} bytes).`);
