/* Round 5 interface: the glitch reveal, the upload bar with its countdown,
   and a noisy live feed. Loaded by index.html. Uses the page globals
   window.s5 (countdown from the server) and window.flags. */
(function(){
  "use strict";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const $q = id => document.getElementById(id);
  const css = document.createElement("style");
  css.textContent = `
    #dts5{position:sticky;top:0;z-index:50;background:var(--ink);padding:6px 0 2px}
    body.s4 main,body.s5on main{max-width:1500px}
    body.s4 .grid,body.s5on .grid{grid-template-columns:1.8fr 1fr}
    body.s4 .tbl span,body.s5on .tbl span{white-space:normal;overflow:visible;text-overflow:clip;word-break:break-word}
    body.s4 .tbl .tr,body.s4 .tbl .th,body.s5on .tbl .tr,body.s5on .tbl .th{font-size:12.5px}
    body.s5on .tbl{max-height:380px}
    .s5bar{border:1px solid var(--red);border-radius:6px;background:#1a0507;padding:12px 16px;margin-bottom:16px}
    .s5top{display:flex;justify-content:space-between;align-items:baseline;gap:12px}
    .s5top b{color:var(--red);font:700 16px var(--mono);letter-spacing:2px}
    #s5c{font:700 40px var(--mono);color:var(--red)}
    .s5track{height:14px;background:#2a0709;border-radius:7px;overflow:hidden;margin:6px 0}
    #s5f{height:100%;width:60%;background:var(--red);transition:width .3s}
    #s5feed{height:84px;overflow:hidden;font:12px/1.4 var(--mono);color:#a04a4a}
    .s5bar.halt{border-color:var(--ok);background:#04150e}
    .s5bar.halt .s5top b,.s5bar.halt #s5c{color:var(--ok)}
    .s5bar.halt #s5f{background:var(--ok)}
    body.s5panic::after{background:radial-gradient(ellipse at center,transparent 40%,rgba(255,0,0,.4));animation:s5p .9s infinite}
    @keyframes s5p{50%{opacity:.4}}
    #s5ov{position:fixed;inset:0;z-index:90;background:#000;display:flex;align-items:center;justify-content:center;padding:24px;text-align:center}
    #s5ov.shake .s5in{animation:s5s .12s infinite}
    @keyframes s5s{0%{transform:translate(-8px,3px)}33%{transform:translate(7px,-4px)}66%{transform:translate(-4px,-6px)}100%{transform:translate(5px,5px)}}
    #s5ov .s5noise{position:absolute;inset:0;background:repeating-linear-gradient(0deg,rgba(255,0,0,.12) 0 2px,transparent 2px 5px);animation:s5n .1s steps(2) infinite}
    @keyframes s5n{50%{transform:translateY(3px);opacity:.5}}
    .s5in{position:relative;max-width:1000px}
    .s5in .l{opacity:0;font:900 clamp(30px,7vw,88px)/1.1 var(--ui);color:var(--red);letter-spacing:2px;margin:10px 0;
      text-shadow:4px 0 #38e1ff,-4px 0 #ff0000}
    .s5in .l.on{opacity:1;animation:s5f .12s steps(2) 8}
    @keyframes s5f{50%{opacity:.3;transform:translateX(6px)}}
    .s5in .l3{font:600 clamp(15px,2.2vw,24px) var(--mono);color:#c9d6df;text-shadow:none;letter-spacing:0}
    #s5go{margin-top:22px;font-size:20px;padding:14px 34px}
  `;
  document.head.appendChild(css);

  let built = false, frozen = null;
  const R = n => Math.floor(Math.random() * n);
  const P2 = n => String(n).padStart(2, "0");
  const WORDS = ["sync", "tx", "rx", "auth", "flush", "chunk", "proxy", "retry", "cache", "dns", "tls", "ack"];

  function build(){
    $q("dts5").innerHTML =
      '<div class="s5bar" id="s5box"><div class="s5top"><b id="s5t">UPLOAD IN PROGRESS</b>' +
      '<span id="s5c">--:--</span></div><div class="s5track"><div id="s5f"></div></div>' +
      '<div id="s5feed"></div></div>';
    built = true;
  }

  function tick(){
    if(!built || !window.s5 || window.s5.left == null) return;
    const s = window.s5, total = s.total || 480;
    const left = Math.max(0, s.left - (Date.now() - s.at) / 1000);
    const blocked = (window.flags || []).indexOf("5:ip_blocked") >= 0;
    let pct = Math.min(100, 60 + 39 * (1 - left / total));
    if(blocked){ if(frozen === null) frozen = pct; pct = frozen; } else { frozen = null; }
    $q("s5f").style.width = pct + "%";
    $q("s5c").textContent = P2(Math.floor(left / 60)) + ":" + P2(Math.floor(left % 60));
    $q("s5box").classList.toggle("halt", blocked);
    $q("s5t").textContent = blocked ? "UPLOAD HALTED. NOW FIND THE INSIDER."
      : (left <= 0 ? "DATA LOST" : "UPLOAD IN PROGRESS " + Math.floor(pct) + "%");
    document.body.classList.toggle("s5panic", !blocked && left > 0 && left < 60 && !reduce);
  }

  function noise(){
    const f = $q("s5feed");
    if(!built || !f || (window.flags || []).indexOf("5:ip_blocked") >= 0) return;
    const d = document.createElement("div");
    d.textContent = P2(R(24)) + ":" + P2(R(60)) + ":" + P2(R(60)) + " " + WORDS[R(12)] + " " +
      (R(2) ? "10.0.4." : "151." + R(250) + ".") + R(250) + " " + WORDS[R(12)] + " " + R(9999) + "b";
    f.appendChild(d);
    while(f.children.length > 6) f.removeChild(f.firstChild);
  }

  setInterval(tick, 250);
  setInterval(noise, 160);

  window.DTS5 = {
    render: function(m){
      const on = m.stage === 5;
      document.body.classList.toggle("s5on", on);
      $q("dts5").classList.toggle("hidden", !on);
      if(on && !built) build();
      if(!on) document.body.classList.remove("s5panic");
    },
    reveal: function(){
      if($q("s5ov")) return;
      const ov = document.createElement("div");
      ov.id = "s5ov"; ov.className = "shake";
      ov.innerHTML = '<div class="s5noise"></div><div class="s5in"><div class="l l1"></div>' +
        '<div class="l l2"></div><div class="l l3"></div><button class="hidden" id="s5go">FIGHT BACK</button></div>';
      document.body.appendChild(ov);
      const say = (sel, text, ms) => setTimeout(() => {
        const e = ov.querySelector(sel); e.textContent = text; e.classList.add("on");
      }, reduce ? 0 : ms);
      setTimeout(() => ov.classList.remove("shake"), reduce ? 0 : 1300);
      say(".l1", "THANKS FOR KILLING HYDRA.", 1500);
      say(".l2", "YOU JUST GAVE ME THE TIME I NEEDED.", 3600);
      say(".l3", "> upload started. NovaCorp's data is leaving. Stop it before the bar hits 100%.", 6000);
      setTimeout(() => {
        const b = $q("s5go"); b.classList.remove("hidden");
        b.onclick = () => ov.remove();
      }, reduce ? 0 : 6400);
    }
  };
})();