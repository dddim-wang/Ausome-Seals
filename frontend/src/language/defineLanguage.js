export default function defineLanguage({ meta, site, chat }) {
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
