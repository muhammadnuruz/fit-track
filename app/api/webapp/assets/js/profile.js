// Ro'yxatdan o'tgan foydalanuvchi uchun: Dashboard va Profil (ko'rish/tahrirlash)
// ekranlari + avatar yuklash. `state.js`, `i18n.js`, `icons.js` dan keyin
// yuklanishi shart.

let ME = null;

function authHeaders() { return { "X-Init-Data": tg ? tg.initData : "" }; }

function toastMsg(m) {
  toast.textContent = m; toast.classList.add("show");
  clearTimeout(toastMsg._t);
  toastMsg._t = setTimeout(() => toast.classList.remove("show"), 1800);
}

function hideProgress() { const w = document.querySelector(".pwrap"); if (w) w.style.display = "none"; }
function showProgressBar() { const w = document.querySelector(".pwrap"); if (w) w.style.display = ""; }

function closeMenu() {
  menuPanel.classList.remove("open");
  menuBtn.setAttribute("aria-expanded", "false");
}
function showMenu() {
  menuBtn.style.display = "inline-flex";
  profileMenuItem.textContent = L.profile;
  menuBtn.onclick = () => {
    const open = menuPanel.classList.toggle("open");
    menuBtn.setAttribute("aria-expanded", String(open));
  };
  profileMenuItem.onclick = () => { closeMenu(); showProfile("view"); };
}
function hideMenu() {
  closeMenu();
  menuBtn.style.display = "none";
}

// --- Ism: "Ism Familiya" <-> {first, last} ---
function splitName(full) {
  const parts = (full || "").trim().split(/\s+/);
  return { first: parts[0] || "", last: parts.slice(1).join(" ") };
}
function joinName(first, last) { return `${first} ${last}`.trim(); }

// --- Avatar ---
function monogramHTML(name) {
  const ch = ((name || "?").trim().charAt(0) || "?").toUpperCase();
  const color = AV_COLORS[ch.charCodeAt(0) % AV_COLORS.length];
  return `<div class="avatar" style="background:${color}">${esc(ch)}</div>`;
}
function avatarHTML(p) {
  const src = p.avatar_url ? p.avatar_url : (tgUser && tgUser.photo_url ? tgUser.photo_url : null);
  if (src) return `<div class="avatar"><img src="${esc(src)}" alt="" /></div>`;
  return monogramHTML(p.name);
}

async function onAvatarPick(e) {
  const f = e.target.files && e.target.files[0];
  if (!f) return;
  const fd = new FormData(); fd.append("file", f);
  try {
    const r = await fetch("/api/me/avatar", { method: "POST", headers: authHeaders(), body: fd });
    if (!r.ok) throw new Error(String(r.status));
    const j = await r.json();
    ME.profile.avatar_url = j.url;
    const wrap = document.getElementById("avwrap");
    wrap.querySelector(".avatar").outerHTML = avatarHTML(ME.profile);
    toastMsg(L.saved);
  } catch (err) { toastMsg(L.errSend); }
}

// --- Boot: kirishda ro'yxatdan o'tganini tekshiradi ---
async function boot() {
  hideProgress();
  hideMenu();
  nav.innerHTML = "";
  card.innerHTML = `<div class="calc"><div class="ring"></div></div>`;
  try {
    const r = await fetch("/api/me", { headers: authHeaders() });
    ME = r.ok ? await r.json() : { registered: false };
  } catch (e) { ME = { registered: false }; }
  if (ME && ME.registered) return showDashboard();
  showProgressBar();
  step = 0; render();
}

// --- Dashboard ---
function macroRow(plan) {
  if (!plan) return "";
  return `<div class="macros">
    <div><span class="mi">${ICONS.macro_protein}</span><b>${esc(plan.macros.protein_g)}g</b><span>${esc(L.protein)}</span></div>
    <div><span class="mi">${ICONS.macro_carb}</span><b>${esc(plan.macros.carb_g)}g</b><span>${esc(L.carb)}</span></div>
    <div><span class="mi">${ICONS.macro_fat}</span><b>${esc(plan.macros.fat_g)}g</b><span>${esc(L.fat)}</span></div>
  </div>`;
}

function showDashboard() {
  hideProgress();
  card.className = "card dashboard-card";
  showMenu();
  const p = ME.profile, plan = ME.plan;
  const bf = plan && plan.body_fat_pct != null ? `<span class="chip">Body fat ${esc(plan.body_fat_pct)}%</span>` : "";
  const chips = plan ? `<div class="chips"><span class="chip">BMI ${esc(plan.bmi)}</span><span class="chip">TDEE ${esc(plan.tdee)}</span>${bf}</div>` : "";
  card.innerHTML = `<div class="dash">
    <div class="dhead">
      <div class="avwrap" id="avwrap">${avatarHTML(p)}
        <button class="avedit" id="avBtn" title="${esc(L.changePhoto)}">${CAM_SVG}</button>
        <input type="file" id="avFile" accept="image/jpeg,image/png,image/webp" hidden />
      </div>
      <div class="dname">
        <span class="name">${esc(p.name)}</span>
        <div class="tag" style="margin-top:2px">${esc(L.tagline)}</div>
      </div>
    </div>
    <div class="limitCard">
      <div class="kc">${esc(L.kcalLabel)}</div>
      <div class="big">${plan ? esc(plan.target_kcal) : "—"}</div>
      ${macroRow(plan)}
      ${chips}
    </div>
    <div class="ph">${esc(L.comingSoon)}</div>
  </div>`;
  nav.innerHTML = "";
  const rc = document.createElement("button");
  rc.className = "btn cta"; rc.textContent = L.recalc; rc.onclick = () => showProfile("form");
  nav.appendChild(rc);
  document.getElementById("avBtn").onclick = () => document.getElementById("avFile").click();
  document.getElementById("avFile").onchange = onAvatarPick;
}

// --- Profil saqlash ---
async function saveProfile(patch) {
  const p = ME.profile;
  const pick = (k) => (k in patch ? patch[k] : p[k]);
  const body = {
    name: pick("name"), gender: pick("gender"), age: pick("age"),
    height_cm: pick("height_cm"), weight_kg: pick("weight_kg"),
    activity: pick("activity"), goal: pick("goal"),
  };
  try {
    const r = await fetch("/api/me", {
      method: "PATCH",
      headers: { ...authHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(String(r.status));
    ME = await r.json();
    showDashboard(); toastMsg(L.saved);
  } catch (e) { toastMsg(L.errSend); }
}

function numOrNull(id) { const v = document.getElementById(id).value.trim(); return v === "" ? null : parseFloat(v); }
function selVal(id) { const on = document.querySelector(`#${id} .csel.on`); return on ? on.dataset.v : null; }

// --- Profil: ko'rish (o'qish uchun) rejimi ---
function renderProfileView() {
  const p = ME.profile;
  const row = (label, value) => `<div class="erow"><label>${esc(label)}</label><span class="val">${esc(value)}</span></div>`;
  card.innerHTML = `<div class="edit">
    <h1>${esc(L.profile)}</h1>
    ${row(L.nameLabel, p.name)}
    ${row(L.q_gender, p.gender === "male" ? L.male : L.female)}
    ${row(L.q_age, p.age)}
    ${row(L.height, p.height_cm)}
    ${row(L.weight, p.weight_kg == null ? "—" : p.weight_kg)}
    ${row(L.q_activity, L["a_" + p.activity])}
    ${row(L.q_goal, L["g_" + p.goal])}
  </div>`;
  nav.innerHTML = "";
  const back = document.createElement("button");
  back.className = "btn ghost"; back.textContent = L.back; back.onclick = () => showDashboard();
  const editBtn = document.createElement("button");
  editBtn.className = "btn cta"; editBtn.textContent = L.editBtn; editBtn.onclick = () => showProfile("form");
  nav.appendChild(back); nav.appendChild(editBtn);
}

// --- Profil: tahrirlash formasi ---
function renderProfileForm() {
  const p = ME.profile;
  const { first, last } = splitName(p.name);
  const chip = (v, label, cur) => `<button data-v="${v}" class="csel ${cur === v ? "on" : ""}">${esc(label)}</button>`;
  const acts = ["sedentary", "moderate", "active"].map(v => chip(v, L["a_" + v], p.activity)).join("");
  const goals = ["cut", "maintain", "bulk"].map(v => chip(v, L["g_" + v], p.goal)).join("");
  card.innerHTML = `<div class="edit">
    <h1>${esc(L.recalc)}</h1>
    <div class="erow"><label>${esc(L.first)}</label><input id="e_first" type="text" maxlength="64" value="${esc(first)}" /></div>
    <div class="erow"><label>${esc(L.last)}</label><input id="e_last" type="text" maxlength="64" value="${esc(last)}" /></div>
    <div class="erow"><label>${esc(L.q_gender)}</label><div class="chipsel" id="e_gender">
      ${chip("male", L.male, p.gender)}${chip("female", L.female, p.gender)}</div></div>
    <div class="erow"><label>${esc(L.q_age)}</label><input id="e_age" type="number" inputmode="numeric" value="${esc(p.age)}" /></div>
    <div class="erow"><label>${esc(L.height)}</label><input id="e_height" type="number" inputmode="decimal" step="0.1" value="${esc(p.height_cm)}" /></div>
    <div class="erow"><label>${esc(L.weight)}</label><input id="e_weight" type="number" inputmode="decimal" step="0.1" value="${esc(p.weight_kg == null ? "" : p.weight_kg)}" /></div>
    <div class="erow"><label>${esc(L.q_activity)}</label><div class="chipsel" id="e_activity">${acts}</div></div>
    <div class="erow"><label>${esc(L.q_goal)}</label><div class="chipsel" id="e_goal">${goals}</div></div>
  </div>`;
  card.querySelectorAll(".chipsel").forEach(sel => {
    sel.querySelectorAll(".csel").forEach(b => {
      b.onclick = () => {
        sel.querySelectorAll(".csel").forEach(x => x.classList.remove("on"));
        b.classList.add("on");
      };
    });
  });
  nav.innerHTML = "";
  const cancel = document.createElement("button");
  cancel.className = "btn ghost"; cancel.textContent = L.cancel; cancel.onclick = () => showProfile("view");
  const save = document.createElement("button");
  save.className = "btn cta"; save.textContent = L.save; save.onclick = onProfileSave;
  nav.appendChild(cancel); nav.appendChild(save);
}

async function onProfileSave() {
  const first = document.getElementById("e_first").value.trim();
  const last = document.getElementById("e_last").value.trim();
  const patch = {
    name: joinName(first, last),
    gender: selVal("e_gender"),
    age: parseInt(document.getElementById("e_age").value, 10),
    height_cm: parseFloat(document.getElementById("e_height").value),
    weight_kg: parseFloat(document.getElementById("e_weight").value),
    activity: selVal("e_activity"),
    goal: selVal("e_goal"),
  };
  if (!first || !patch.gender || !patch.activity || !patch.goal ||
      !patch.age || !patch.height_cm || !patch.weight_kg) { toastMsg(L.errReq); return; }
  await saveProfile(patch);
}

// mode: "view" (faqat o'qish, ☰ → Profil orqali) yoki "form" (tahrirlash,
// Dashboard'dagi "Qayta hisoblash" orqali to'g'ridan-to'g'ri; "view"dan
// "Tahrirlash" bosilganda ham; "Bekor qilish" har doim "view"ga qaytaradi).
function showProfile(mode) {
  hideProgress();
  closeMenu();
  card.className = "card";
  if (mode === "form") renderProfileForm(); else renderProfileView();
}
