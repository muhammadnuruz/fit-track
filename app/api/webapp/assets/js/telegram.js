// Telegram WebApp SDK bootstrap: shu fayldan keyingi barcha skriptlar
// `tg`, `tgUser` va `LANG` ni ishlatadi.
const tg = window.Telegram ? window.Telegram.WebApp : null;
if (tg) { tg.ready(); tg.expand(); }

const params = new URLSearchParams(location.search);
const tgUser = (tg && tg.initDataUnsafe && tg.initDataUnsafe.user) ? tg.initDataUnsafe.user : {};
const LANG = ["uz", "ru", "en"].includes(params.get("lang")) ? params.get("lang")
  : (["uz", "ru", "en"].includes(tgUser.language_code) ? tgUser.language_code : "uz");
