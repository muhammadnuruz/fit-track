// Umumiy DOM referenslar va onboarding holati. Boshqa hamma modul shu
// yerdagi doimiylarni ishlatadi — `i18n.js` dan keyin yuklanishi shart.

const card = document.getElementById("card");
const nav = document.getElementById("nav");
const menuBtn = document.getElementById("menuBtn");
const menuPanel = document.getElementById("menuPanel");
const profileMenuItem = document.getElementById("profileMenuItem");
const bar = document.getElementById("bar");
const stepLbl = document.getElementById("stepLbl");
const pctLbl = document.getElementById("pctLbl");
const toast = document.getElementById("toast");

document.getElementById("tagline").textContent = L.tagline;

function esc(s) { const d = document.createElement("div"); d.textContent = s; return d.innerHTML; }

const TOTAL = 7;
const RANGES = { age: [10, 100], height_cm: [100, 250], weight_kg: [30, 350] };

const data = {
  first_name: "", last_name: "",
  gender: null, age: null, height_cm: null, weight_kg: null,
  activity: "moderate", goal: null,
};
let step = 0;

// Saqlash o'chirilgan: har safar (birinchi hisob ham, recalculate ham) toza,
// ismdan boshlanadi. Eski saqlangan qiymatlar bo'lsa tozalab yuboramiz.
const LS_KEY = "fittrack_onb_" + (tgUser.id || "anon");
try { localStorage.removeItem(LS_KEY); } catch (e) { /* localStorage yo'q — muammo emas */ }

function persist() { /* saqlash o'chirilgan */ }
function clearStore() { try { localStorage.removeItem(LS_KEY); } catch (e) { /* noop */ } }
