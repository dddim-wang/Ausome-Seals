import de from "./de";
import en from "./en";
import es from "./es";
import fr from "./fr";
import id from "./id";
import ja from "./ja";
import ru from "./ru";
import zh from "./zh";

const languages = [en, zh, es, fr, de, ja, id, ru];

export const languageOptions = languages.map(({ meta }) => meta);

export const translations = Object.fromEntries(
  languages.map(({ meta, site }) => [meta.code, site]),
);

export const chatTranslations = Object.fromEntries(
  languages.map(({ meta, chat }) => [meta.code, chat]),
);

export function getLanguageMeta(code) {
  return languageOptions.find((language) => language.code === code) || en.meta;
}

export function isSupportedLanguage(code) {
  return languageOptions.some((language) => language.code === code);
}
