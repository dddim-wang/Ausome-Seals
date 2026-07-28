import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const frontendDir = path.resolve(scriptDir, "..");
const languageDir = path.join(frontendDir, "src", "language");
const outputPath = path.resolve(frontendDir, "..", "backend", "knowledge", "Ausome_Website_Content.rag.json");
const languageFiles = fs.readdirSync(languageDir)
  .filter((name) => /^[a-z]{2}\.js$/.test(name))
  .sort();

function defineLanguage({ meta, site, chat }) {
  return {
    meta,
    site: {
      brandName: "Ausome Seals",
      email: "support@ausomeseals.com",
      phone: "WhatsApp: +86 137-7661-6519",
      messagePlaceholder: "",
      ...site,
    },
    chat,
  };
}

function loadLanguage(fileName) {
  const sourcePath = path.join(languageDir, fileName);
  const source = fs.readFileSync(sourcePath, "utf8")
    .replace(/^import defineLanguage from "\.\/defineLanguage";\s*/m, "")
    .replace("export default defineLanguage(", "globalThis.__language = defineLanguage(");
  const context = vm.createContext({ defineLanguage });
  new vm.Script(source, { filename: sourcePath }).runInContext(context);
  return JSON.parse(JSON.stringify(context.__language));
}

function collectStrings(value, currentPath, lines) {
  if (typeof value === "string") {
    if (value.trim()) lines.push(`${currentPath}: ${value.trim()}`);
    return;
  }
  if (Array.isArray(value)) {
    value.forEach((item, index) => {
      collectStrings(item, `${currentPath}[${index + 1}]`, lines);
    });
    return;
  }
  if (value && typeof value === "object") {
    Object.entries(value).forEach(([key, item]) => {
      collectStrings(item, currentPath ? `${currentPath}.${key}` : key, lines);
    });
  }
}

function chunkSection(language, section, value, nextPage) {
  const lines = [];
  collectStrings(value, section, lines);
  const chunks = [];
  const header = `Ausome website content | language=${language} | section=${section}`;
  let current = header;

  for (const line of lines) {
    if (current.length + line.length + 1 > 1800 && current !== header) {
      chunks.push({ language, page: nextPage(), text: current });
      current = header;
    }
    current += `\n${line}`;
  }
  if (current !== header) {
    chunks.push({ language, page: nextPage(), text: current });
  }
  return chunks;
}

let page = 0;
const nextPage = () => {
  page += 1;
  return page;
};
const chunks = [];

for (const fileName of languageFiles) {
  const language = loadLanguage(fileName);
  const code = language.meta.code;
  chunks.push(...chunkSection(code, "meta", language.meta, nextPage));
  chunks.push(...chunkSection(code, "site", language.site, nextPage));
  chunks.push(...chunkSection(code, "chat", language.chat, nextPage));
}

const payload = {
  version: 1,
  generatedFrom: languageFiles.map((name) => `frontend/src/language/${name}`),
  chunks,
};
const serialized = `${JSON.stringify(payload, null, 2)}\n`;

if (process.argv.includes("--check")) {
  const existing = fs.existsSync(outputPath)
    ? fs.readFileSync(outputPath, "utf8").replace(/\r\n/g, "\n")
    : "";
  if (existing !== serialized) {
    throw new Error("Website RAG content is out of date. Run: npm run knowledge:export");
  }
} else {
  fs.writeFileSync(outputPath, serialized, "utf8");
  console.log(`Exported ${chunks.length} website knowledge chunks to ${outputPath}`);
}
