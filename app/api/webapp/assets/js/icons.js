// Ilova bo'ylab ishlatiladigan statik SVG ikonalar. Mantiq yo'q — faqat belgilar.

const TICK = '<svg class="tick" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="11" fill="var(--green)"/><path d="M7 12.5l3.2 3.2L17 9" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

const CAM_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"/><circle cx="12" cy="13" r="4"/></svg>';
const PEN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>';

const AV_COLORS = ["#2d9b62", "#1e4c9a", "#c7562f", "#b3902a", "#2f7fae", "#6a4dab"];

// Onboarding qadamlarida (jins/faollik/maqsad) va dashboard makrolarida
// ishlatiladigan chiziqli ikonalar. Mono uslub: struktura — ink, urg'u — accent (yashil).
const ICONS = {
  gender_male: '<svg viewBox="0 0 24 24" fill="none"><circle cx="10" cy="14" r="5.2" fill="none" stroke="var(--ink)" stroke-width="2"/><path d="M14.5 9.5 20 4" stroke="var(--ink)" stroke-width="2" stroke-linecap="round"/><path d="M15.5 4H20v4.5" stroke="var(--ink)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
  gender_female: '<svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8.5" r="5.2" fill="none" stroke="var(--ink)" stroke-width="2"/><path d="M12 13.7V21" stroke="var(--ink)" stroke-width="2" stroke-linecap="round"/><path d="M8.5 17.5h7" stroke="var(--ink)" stroke-width="2" stroke-linecap="round"/></svg>',
  act_sedentary: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M5 11V9a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v2"/><path d="M3 13.5A1.5 1.5 0 0 1 4.5 12H6a1.5 1.5 0 0 1 1.5 1.5V15h9v-1.5A1.5 1.5 0 0 1 18 12h1.5A1.5 1.5 0 0 1 21 13.5V17a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1Z"/><path d="M6 18v1.5M18 18v1.5"/></svg>',
  act_light: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 16.5v-3l3.5-1 2.2 1.4c1 .6 2.1.9 3.3 1l4.5.4c1.6.1 2.5.9 2.5 2.2v.5H4a1 1 0 0 1-1-1Z"/><path d="M7 12.8v1.7M10 14v1.6"/></svg>',
  act_moderate: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="5.5" cy="17" r="3.2"/><circle cx="18.5" cy="17" r="3.2"/><path d="M5.5 17h5l3.5-6.5"/><path d="M9 10.5h5.5L18.5 17"/><path d="M13.5 7.5H16"/></svg>',
  act_active: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.8" stroke-linejoin="round"><path d="M13 2 4 13.5h6l-1 8.5 9-11.5h-6l1-8.5Z"/></svg>',
  act_very_active: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.8" stroke-linejoin="round"><path d="M13 2 4 13.5h6l-1 8.5 9-11.5h-6l1-8.5Z"/></svg>',
  goal_cut: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="m19 12-7 7-7-7"/><path d="M12 19V5"/></svg>',
  goal_maintain: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"/></svg>',
  goal_bulk: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--ink)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M12 19V5m-7 7 7-7 7 7"/></svg>',
  macro_protein: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4.2a5 5 0 0 1 4 8 3 3 0 0 1-3.4 4.3 3 3 0 0 1-4.1-4.2A5 5 0 0 1 14 4.2Z"/><path d="m10.4 13.6-4.2 4.2"/><path d="M6.2 17.8 4 18.1l.3-2.2M6.2 17.8 6 20l2.2-.3"/></svg>',
  macro_carb: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 11.5h17a8.5 8.5 0 0 1-17 0Z"/><path d="M2.5 11.5h19"/><path d="M8.5 8.2c.8-1.2 2-1.9 3.5-1.9s2.7.7 3.5 1.9"/><path d="M12 5.4v1.3"/></svg>',
  macro_fat: '<svg viewBox="0 0 24 24" fill="none" stroke="var(--green)" stroke-width="1.8" stroke-linejoin="round"><path d="M12 3.2c3.2 0 5.3 2.9 5.3 7.3 0 4.6-2.6 9.8-5.3 9.8s-5.3-5.2-5.3-9.8C6.7 6.1 8.8 3.2 12 3.2Z"/><circle cx="12" cy="13.8" r="2.6"/></svg>',
};
