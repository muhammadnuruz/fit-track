// Onboarding sehrgari: 7 qadam (ism → jins → sana → bo'y → vazn → faollik →
// maqsad) + hisoblash ekrani + serverга yuborish. `state.js`, `i18n.js`,
// `icons.js` dan keyin yuklanishi shart. `submit()` muvaffaqiyatdan keyin
// `boot()` ni chaqiradi (profile.js da e'lon qilinadi).

function showReward(i) {
  const msg = L.rewards[i];
  if (!msg) return;
  toast.textContent = msg;
  toast.classList.add("show");
  clearTimeout(showReward._t);
  showReward._t = setTimeout(() => toast.classList.remove("show"), 1600);
}

function setProgress() {
  const pct = Math.round((step / TOTAL) * 100);
  bar.style.width = pct + "%";
  stepLbl.textContent = `${L.step} ${step + 1} / ${TOTAL}`;
  pctLbl.textContent = `${pct}% ${L.done}`;
}

function go(next) {
  if (next > step && next <= TOTAL) showReward(step);
  step = next; persist(); render();
}

function navBtns(primaryLabel, onPrimary, opts) {
  opts = opts || {};
  nav.innerHTML = "";
  if (step > 0) {
    const b = document.createElement("button");
    b.className = "btn ghost"; b.textContent = L.back;
    b.onclick = () => go(step - 1);
    nav.appendChild(b);
  }
  if (opts.skip) {
    const s = document.createElement("button");
    s.className = "btn ghost"; s.textContent = L.skip; s.onclick = opts.skip;
    nav.appendChild(s);
  }
  const p = document.createElement("button");
  p.className = "btn" + (opts.cta ? " cta" : ""); p.id = "primary";
  p.textContent = primaryLabel; p.onclick = onPrimary;
  if (opts.disabled) p.disabled = true;
  nav.appendChild(p);
  return p;
}

function setPrimaryEnabled(on) { const p = document.getElementById("primary"); if (p) p.disabled = !on; }

function render() {
  setProgress();
  const r = [renderName, renderGender, renderAge, renderHeight, renderWeight, renderActivity, renderGoal][step];
  r();
}

function renderName() {
  card.innerHTML = `<h1>${esc(L.q_name)}</h1><p class="sub">${esc(L.s_name)}</p>
    <div class="field"><label>${esc(L.first)}</label>
      <input id="fn" type="text" maxlength="64" value="${esc(data.first_name)}" autocomplete="given-name" />${TICK}</div>
    <div class="field"><label>${esc(L.last)}</label>
      <input id="ln" type="text" maxlength="64" value="${esc(data.last_name)}" autocomplete="family-name" />${TICK}</div>
    ${L.m_name ? `<p class="micro">${esc(L.m_name)}</p>` : ""}`;
  const fn = document.getElementById("fn"), ln = document.getElementById("ln");
  const ticks = card.querySelectorAll(".tick");
  const check = () => {
    const okF = fn.value.trim().length > 0, okL = ln.value.trim().length > 0;
    fn.classList.toggle("good", okF); ln.classList.toggle("good", okL);
    ticks[0].classList.toggle("show", okF); ticks[1].classList.toggle("show", okL);
    setPrimaryEnabled(okF && okL);
  };
  fn.addEventListener("input", check); ln.addEventListener("input", check);
  navBtns(L.next, () => {
    data.first_name = fn.value.trim(); data.last_name = ln.value.trim();
    if (!data.first_name || !data.last_name) return;
    persist(); go(step + 1);
  }, { disabled: true });
  check();
}

function renderNumber(key, title, sub, label, extraMicro) {
  card.innerHTML = `<h1>${esc(title)}</h1><p class="sub">${esc(sub)}</p>
    <div class="field"><label>${esc(label)}</label>
      <input id="f" type="number" inputmode="decimal" value="${data[key] ?? ""}" />${TICK}
      <div class="ferr" id="fe"></div></div>${extraMicro ? `<p class="micro">${esc(extraMicro)}</p>` : ""}`;
  const f = document.getElementById("f"), fe = document.getElementById("fe"), tick = card.querySelector(".tick");
  const [min, max] = RANGES[key];
  const check = () => {
    const raw = f.value.trim();
    if (raw === "") { f.classList.remove("good", "bad"); tick.classList.remove("show"); fe.textContent = ""; setPrimaryEnabled(false); return; }
    const v = parseFloat(raw);
    const ok = !isNaN(v) && v >= min && v <= max;
    f.classList.toggle("good", ok); f.classList.toggle("bad", !ok);
    tick.classList.toggle("show", ok);
    fe.textContent = ok ? "" : `${L.errRange}: ${min}–${max}`;
    setPrimaryEnabled(ok);
  };
  f.addEventListener("input", check);
  navBtns(L.next, () => {
    const v = parseFloat(f.value); if (isNaN(v) || v < min || v > max) return;
    data[key] = v; persist(); go(step + 1);
  }, { disabled: true });
  check();
}

function calcAgeFromBirthDate(date) {
  const now = new Date();
  const birth = new Date(date.year, date.month - 1, date.day);
  let age = now.getFullYear() - birth.getFullYear();
  const hasBirthdayPassed =
    now.getMonth() > birth.getMonth() ||
    (now.getMonth() === birth.getMonth() && now.getDate() >= birth.getDate());
  if (!hasBirthdayPassed) age -= 1;
  return age;
}

function renderAge() {
  const curYear = new Date().getFullYear();
  let sd = 0, sm = 0, sy = 0;
  const savedMatch = String(data.birth_date || "").match(/^(\d{2})-(\d{2})-(\d{4})$/);
  if (savedMatch) { sd = +savedMatch[1]; sm = +savedMatch[2]; sy = +savedMatch[3]; }

  const opt = (v, label, sel) => `<option value="${v}"${sel ? " selected" : ""}>${esc(label)}</option>`;
  const dayOpts = [`<option value="" disabled${sd ? "" : " selected"}>${esc(L.dob_day)}</option>`];
  for (let d = 1; d <= 31; d++) dayOpts.push(opt(d, String(d).padStart(2, "0"), d === sd));
  const monthOpts = [`<option value="" disabled${sm ? "" : " selected"}>${esc(L.dob_month)}</option>`];
  for (let m = 1; m <= 12; m++) monthOpts.push(opt(m, L.months[m - 1], m === sm));
  const yearOpts = [`<option value="" disabled${sy ? "" : " selected"}>${esc(L.dob_year)}</option>`];
  for (let y = curYear - 10; y >= curYear - 100; y--) yearOpts.push(opt(y, String(y), y === sy));

  card.innerHTML = `<h1>${esc(L.q_age)}</h1><p class="sub">${esc(L.s_age)}</p>
    <div class="dob-grid">
      <div class="dob-box"><label>${esc(L.dob_day)}</label><select id="dob-d">${dayOpts.join("")}</select></div>
      <div class="dob-box"><label>${esc(L.dob_month)}</label><select id="dob-m">${monthOpts.join("")}</select></div>
      <div class="dob-box"><label>${esc(L.dob_year)}</label><select id="dob-y">${yearOpts.join("")}</select></div>
    </div>
    <div class="ferr" id="dob-fe"></div>`;

  const dEl = document.getElementById("dob-d");
  const mEl = document.getElementById("dob-m");
  const yEl = document.getElementById("dob-y");
  const fe = document.getElementById("dob-fe");
  let valid = null;

  const check = () => {
    valid = null;
    const day = +dEl.value, month = +mEl.value, year = +yEl.value;
    if (!day || !month || !year) { fe.textContent = ""; setPrimaryEnabled(false); return; }
    const dt = new Date(year, month - 1, day);
    const real = dt.getFullYear() === year && dt.getMonth() === month - 1 && dt.getDate() === day;
    if (!real) { fe.textContent = `${L.errRange}: ${L.age}`; setPrimaryEnabled(false); return; }
    const age = calcAgeFromBirthDate({ day, month, year });
    if (age < 10 || age > 100) { fe.textContent = `${L.errRange}: 10–100`; setPrimaryEnabled(false); return; }
    valid = { day, month, year, age };
    fe.textContent = "";
    setPrimaryEnabled(true);
  };

  [dEl, mEl, yEl].forEach(el => el.addEventListener("change", check));

  navBtns(L.next, () => {
    if (!valid) return;
    data.birth_date = `${String(valid.day).padStart(2, "0")}-${String(valid.month).padStart(2, "0")}-${valid.year}`;
    data.age = valid.age;
    persist();
    go(step + 1);
  }, { disabled: true });

  check();
}

function renderHeight() { renderNumber("height_cm", L.q_height, L.s_height, L.height); }
function renderWeight() { renderNumber("weight_kg", L.q_weight, L.s_weight, L.weight); }

function choiceStep(key, title, sub, items, finish) {
  card.innerHTML = `<h1>${esc(title)}</h1><p class="sub">${esc(sub)}</p>
    <div class="options">${items.map(it => `
      <div class="opt ${data[key] === it.v ? 'sel' : ''}" data-v="${it.v}">
        ${it.ic ? `<span class="ic">${ICONS[it.ic] || ""}</span>` : ""}
        <span class="txt">${esc(it.t)}${it.d ? `<small>${esc(it.d)}</small>` : ""}</span>
        <span class="rad"></span>
      </div>`).join("")}</div>`;
  card.querySelectorAll(".opt").forEach(el => el.onclick = () => {
    data[key] = el.dataset.v; persist();
    card.querySelectorAll(".opt").forEach(o => o.classList.toggle("sel", o.dataset.v === data[key]));
    setPrimaryEnabled(true);
  });
  navBtns(finish ? L.finish : L.next, () => {
    if (!data[key]) return;
    if (finish) submit(); else go(step + 1);
  }, { disabled: !data[key], cta: !!finish });
}

function renderGender() {
  choiceStep("gender", L.q_gender, L.s_gender, [
    { v: "male", t: L.male, ic: "gender_male" },
    { v: "female", t: L.female, ic: "gender_female" },
  ]);
}

function renderActivity() {
  choiceStep("activity", L.q_activity, L.s_activity,
    ["sedentary", "moderate", "active"].map(v =>
      ({ v, t: L["a_" + v], d: L["a_" + v + "_d"], ic: "act_" + v })));
}

function renderGoal() {
  choiceStep("goal", L.q_goal, L.s_goal, [
    { v: "cut", t: L.g_cut, d: L.g_cut_d, ic: "goal_cut" },
    { v: "maintain", t: L.g_maintain, d: L.g_maintain_d, ic: "goal_maintain" },
    { v: "bulk", t: L.g_bulk, d: L.g_bulk_d, ic: "goal_bulk" },
  ], true);
}

let _calcTimer = null;
let _calcCount = null;
function showCalculating() {
  nav.innerHTML = "";
  card.innerHTML = `<div class="calc">
      <div class="ring"></div>
      <h1>${esc(L.calc_title)}</h1>
      <div class="cstep" id="cstep">${esc(L.calc_steps[0])}</div>
      <div class="cbar"><i id="cbari"></i></div>
    </div>`;
  requestAnimationFrame(() => { const b = document.getElementById("cbari"); if (b) b.style.width = "100%"; });

  // Rag'batlantirish: yuqoridagi progress 100% ga to'ladi
  stepLbl.textContent = "";
  bar.style.width = "100%";
  let pc = Math.round((step / TOTAL) * 100);
  pctLbl.textContent = `${pc}% ${L.done}`;
  _calcCount = setInterval(() => {
    pc = Math.min(100, pc + 2);
    pctLbl.textContent = `${pc}% ${L.done}`;
    if (pc >= 100) { clearInterval(_calcCount); _calcCount = null; }
  }, 45);

  // Bosqich matni silliq almashadi (fade + slide)
  let i = 0;
  const el = document.getElementById("cstep");
  _calcTimer = setInterval(() => {
    i = (i + 1) % L.calc_steps.length;
    if (!el) return;
    el.style.opacity = "0";
    el.style.transform = "translateY(6px)";
    setTimeout(() => {
      el.textContent = L.calc_steps[i];
      el.style.opacity = "1";
      el.style.transform = "translateY(0)";
    }, 300);
  }, 950);
}
function stopCalculating() {
  if (_calcTimer) { clearInterval(_calcTimer); _calcTimer = null; }
  if (_calcCount) { clearInterval(_calcCount); _calcCount = null; }
}

async function submit() {
  showCalculating();
  const minWait = new Promise(r => setTimeout(r, 2400));
  try {
    const initData = tg ? tg.initData : "";
    if (!initData) {
      const reason = !window.Telegram ? "SDK yuklanmadi"
        : !tg ? "WebApp yo'q"
        : (tg.initDataUnsafe && tg.initDataUnsafe.user) ? "imzosiz launch"
        : "kontekst yo'q";
      throw new Error(`initData bo'sh · ${reason} · v${tg?.version || "?"}/${tg?.platform || "?"}`);
    }
    const body = {
      init_data: initData,
      name: (data.first_name + " " + data.last_name).trim(),
      gender: data.gender, age: Math.round(data.age),
      height_cm: data.height_cm, weight_kg: data.weight_kg,
      activity: data.activity, goal: data.goal,
    };
    const res = await fetch("/api/onboarding", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
    });
    const json = await res.json().catch(() => ({}));
    if (!res.ok) {
      const detail = json?.detail;
      const msg = typeof detail === "string"
        ? detail
        : Array.isArray(detail)
          ? (detail[0]?.msg || L.errSend)
          : L.errSend;
      throw new Error(`${res.status} · ${msg}`);
    }
    await minWait;
    stopCalculating();
    clearStore();
    return boot();  // ro'yxatdan o'tgach dashboard'ga o'tamiz
  } catch (e) {
    stopCalculating();
    render();
    toast.textContent = e?.message || L.errSend;
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 2800);
  }
}
