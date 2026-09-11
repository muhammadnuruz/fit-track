// Yandex RTB reklama: natija ekranidagi banner + chiqishdagi fullscreen.
// `telegram.js` dan keyin yuklanishi shart (tg kerak).

// Blok ID Yandex kabinetidan. Bo'sh bo'lsa reklama render bo'lmaydi.
const YA_BLOCK_ID = "R-A-20020837-1";
// Fullscreen (chiqishda) reklama uchun ALOHIDA Yandex unit ID.
const YA_FULLSCREEN_ID = "R-A-20020837-2";

function renderAd(containerId) {
  if (!YA_BLOCK_ID || typeof window.Ya === "undefined") return;
  window.yaContextCb.push(() => {
    try {
      window.Ya.Context.AdvManager.render({ blockId: YA_BLOCK_ID, renderTo: containerId });
    } catch (_) { /* reklama yuklanmasa, ekran buzilmaydi */ }
  });
}

// "Yopish" bosilganda: natija allaqachon ko'rilgan → fullscreen reklama → keyin yopiladi.
let _exitAdShown = false;
function closeWithExitAd() {
  if (!tg) return;
  // Reklama allaqachon ko'rsatilgan bo'lsa (2-bosish) yoki ID yo'q bo'lsa — to'g'ridan-to'g'ri yopamiz.
  if (_exitAdShown || !YA_FULLSCREEN_ID || typeof window.Ya === "undefined") { tg.close(); return; }
  _exitAdShown = true;
  let done = false, rendered = false;
  const finish = () => { if (done) return; done = true; tg.close(); };
  window.yaContextCb.push(() => {
    try {
      const plat = /android|ios|iphone|ipad/i.test((tg && tg.platform) || "") ? "touch"
        : (tg && tg.platform && tg.platform !== "unknown") ? "desktop" : "touch";
      window.Ya.Context.AdvManager.render({
        blockId: YA_FULLSCREEN_ID,
        type: "fullscreen",
        platform: plat,
        onRender: () => { rendered = true; },
        onClose: finish,
        onError: finish,
      });
    } catch (_) { finish(); }
  });
  // Reklama umuman ochilmasa (bloklovchi/tarmoq), 5s dan keyin baribir yopamiz.
  setTimeout(() => { if (!rendered) finish(); }, 5000);
}
