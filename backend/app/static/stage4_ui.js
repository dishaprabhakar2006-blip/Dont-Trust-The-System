/* Round 4 interface: process/network tables, dial lock, order lock and the
   QR tile board. Loaded by index.html. It uses these globals from the page:
   S (session), $ (getElementById), submit(questionId, value). */
(function(){
  "use strict";

  const CSS = `
    body.s4 .evidence{max-height:46vh}
    .tbl{border:1px solid var(--line);border-radius:4px;background:#0b0e14;max-height:320px;overflow:auto;margin-bottom:12px;scrollbar-color:#3a4155 #0b0e14}
    .tbl::-webkit-scrollbar{width:10px}
    .tbl::-webkit-scrollbar-track{background:#0b0e14}
    .tbl::-webkit-scrollbar-thumb{background:#3a4155;border-radius:5px}
    .tbl .th,.tbl .tr{display:grid;gap:8px;padding:7px 12px;align-items:center;font:13px var(--mono)}
    .tbl .th{color:var(--dim);font-size:12px;border-bottom:1px solid var(--line);position:sticky;top:0;background:#0b0e14}
    .tbl .tr{border-bottom:1px solid #151a26}
    .tbl .tr:hover{background:#1b2030}
    .tbl .tr span,.tbl .th span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
    .tbl button{padding:3px 10px;font-size:12px;background:#8a1f1f}
    .bd{--m:12px;display:inline-block;margin:6px 0}
    .bd.scan{--m:18px;background:#fff;padding:24px}
    .bdGrid{display:grid;grid-template-columns:repeat(3,calc(var(--m) * 10))}
    .bdCell{width:calc(var(--m) * 10);height:calc(var(--m) * 15);background:#0b0e14;cursor:pointer;
      display:flex;align-items:center;justify-content:center;font-size:22px}
    .bdCell.locked{background:#10131a;border:1px dashed var(--line);box-sizing:border-box;cursor:pointer}
    .bdCell.sel{outline:3px solid var(--amber);outline-offset:-3px}
    .bdCell img{width:100%;height:100%;display:block;image-rendering:pixelated}
    .bdBar{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
    .dial{display:flex;gap:10px;align-items:center;margin-right:8px}
    .dialCol{display:flex;flex-direction:column;align-items:center;gap:2px}
    .dialCol button{padding:1px 14px;font-size:12px;background:#23304a;color:var(--text)}
    .dialCol b{font:700 26px var(--mono);color:var(--amber);min-width:30px;text-align:center}
    .order{flex-basis:100%;display:flex;flex-direction:column;gap:6px;margin-bottom:4px}
    .order button.card{text-align:left;background:#0b0e14;border:1px solid var(--line);color:var(--text);font-weight:500}
    .order button.card.used{border-color:var(--amber);color:var(--amber)}
  `;
  const style = document.createElement("style");
  style.textContent = CSS;
  document.head.appendChild(style);

  /* ---------------- helpers ---------------- */
  const el = (tag, cls, text) => {
    const e = document.createElement(tag);
    if(cls) e.className = cls;
    if(text !== undefined) e.textContent = text;
    return e;
  };
  const teamKey = id => (S.team_id || "") + ":" + id;

  /* ---------------- tables ---------------- */
  let tablesEl = null, boardEl = null;

  function drawTables(m){
    tablesEl.innerHTML = "";
    const tables = m.tables || [];
    tablesEl.classList.toggle("hidden", !tables.length);
    tables.forEach(t => {
      tablesEl.appendChild(el("h3", "", t.title));
      const box = el("div", "tbl");
      const live = !!(t.pick && m.questions.some(q => q.id === t.pick.question && !q.answered));
      const cols = "repeat(" + t.columns.length + ", minmax(0,1fr))" + (live ? " 110px" : "");
      const head = el("div", "th"); head.style.gridTemplateColumns = cols;
      t.columns.concat(live ? [""] : []).forEach(c => head.appendChild(el("span", "", c)));
      box.appendChild(head);
      t.rows.forEach(r => {
        const row = el("div", "tr"); row.style.gridTemplateColumns = cols;
        r.cells.forEach(c => { const s = el("span", "", c); s.title = c; row.appendChild(s); });
        if(live){
          const b = el("button", "", t.pick.label);
          b.onclick = () => { if(confirm(t.pick.confirm || "Are you sure?")) submit(t.pick.question, r.id); };
          row.appendChild(b);
        }
        box.appendChild(row);
      });
      tablesEl.appendChild(box);
    });
  }

  /* ---------------- QR tile board ---------------- */
  const tileUrl = {};
  const tileBusy = {};
  let board = null;      // {team, slots, rot, sel, scan}
  let avail = [];        // tile ids that are unlocked right now

  function rng(seed){
    let h = 1779033703 ^ seed.length;
    for(let i = 0; i < seed.length; i++){
      h = Math.imul(h ^ seed.charCodeAt(i), 3432918353);
      h = (h << 13) | (h >>> 19);
    }
    let a = h >>> 0;
    return function(){
      a = (a + 0x6D2B79F5) | 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  function scramble(teamId){
    const rnd = rng("board:" + teamId);
    let slots, rot;
    do{
      slots = [0, 1, 2, 3, 4, 5];
      for(let i = 5; i > 0; i--){
        const j = Math.floor(rnd() * (i + 1));
        const tmp = slots[i]; slots[i] = slots[j]; slots[j] = tmp;
      }
      rot = [0, 0, 0, 0, 0, 0].map(() => (rnd() < 0.5 ? 180 : 0));
    }while(slots.filter((p, i) => p === i).length > 1 || rot.filter(r => r === 180).length < 2);
    return {slots, rot};
  }
  function saveBoard(){
    try{ sessionStorage.setItem("dts_board_" + board.team, JSON.stringify({slots: board.slots, rot: board.rot})); }catch(e){}
  }
  function loadBoard(){
    const team = S.team_id;
    let st = null;
    try{ st = JSON.parse(sessionStorage.getItem("dts_board_" + team) || "null"); }catch(e){}
    if(!st || !Array.isArray(st.slots) || st.slots.length !== 6 || !Array.isArray(st.rot) || st.rot.length !== 6) st = scramble(team);
    board = {team, slots: st.slots, rot: st.rot, sel: null, scan: false};
  }
  function fetchTile(id){
    const k = teamKey(id);
    if(tileUrl[k] || tileBusy[k]) return;
    tileBusy[k] = true;
    fetch("/teams/" + S.team_id + "/asset/" + encodeURIComponent(id) + "?player_id=" + encodeURIComponent(S.player_id))
      .then(r => { if(!r.ok) throw new Error("tile"); return r.blob(); })
      .then(b => { tileUrl[k] = URL.createObjectURL(b); tileBusy[k] = false; drawBoard(); })
      .catch(() => { tileBusy[k] = false; setTimeout(() => { if(avail.indexOf(id) >= 0) fetchTile(id); }, 3000); });
  }
  function clickCell(i){
    if(board.scan) return;
    if(board.sel === null){ board.sel = i; }
    else if(board.sel === i){ board.sel = null; }
    else{
      const t = board.slots[board.sel]; board.slots[board.sel] = board.slots[i]; board.slots[i] = t;
      board.sel = null; saveBoard();
    }
    drawBoard();
  }
  function drawBoard(){
    if(!boardEl || !board) return;
    boardEl.innerHTML = "";
    boardEl.appendChild(el("h3", "", "Core Dump board"));
    boardEl.appendChild(el("p", "",
      "Rebuild the QR code. Click a tile, then click another tile to swap them. " +
      "Rotate turns the selected tile upside down. The three big squares sit in three " +
      "corners, and the outer edge of the code is white. When it looks right, press " +
      "Scan view and point your phone at the screen."));
    const wrap = el("div", "bd" + (board.scan ? " scan" : ""));
    const grid = el("div", "bdGrid");
    board.slots.forEach((piece, i) => {
      const id = "tile" + (piece + 1);
      const url = avail.indexOf(id) >= 0 ? tileUrl[teamKey(id)] : null;
      const cell = el("div", "bdCell" + (url ? "" : " locked") + (board.sel === i && !board.scan ? " sel" : ""));
      if(url){
        const img = el("img");
        img.src = url; img.alt = ""; img.draggable = false;
        img.style.transform = board.rot[piece] ? "rotate(180deg)" : "none";
        cell.appendChild(img);
      }else{
        cell.textContent = "\uD83D\uDD12";
      }
      cell.onclick = () => clickCell(i);
      grid.appendChild(cell);
    });
    wrap.appendChild(grid);
    boardEl.appendChild(wrap);
    const bar = el("div", "bdBar");
    const rotate = el("button", "ghost", "Rotate selected tile");
    rotate.onclick = () => {
      if(board.sel === null || board.scan) return;
      const p = board.slots[board.sel];
      board.rot[p] = board.rot[p] ? 0 : 180; saveBoard(); drawBoard();
    };
    const scan = el("button", "", board.scan ? "Back to editing" : "Scan view");
    scan.onclick = () => { board.scan = !board.scan; board.sel = null; drawBoard(); };
    const reset = el("button", "ghost", "Shuffle again");
    reset.onclick = () => { const s = scramble(board.team + ":" + Date.now()); board.slots = s.slots; board.rot = s.rot; board.sel = null; saveBoard(); drawBoard(); };
    bar.append(rotate, scan, reset);
    boardEl.appendChild(bar);
  }
  function drawBoardFor(m){
    avail = (m.assets || []).filter(a => a.id.indexOf("tile") === 0).map(a => a.id);
    boardEl.classList.toggle("hidden", !avail.length);
    if(!avail.length) return;
    if(!board || board.team !== S.team_id) loadBoard();
    avail.forEach(fetchTile);
    drawBoard();
  }

  /* ---------------- question widgets ---------------- */
  const dialVals = {};
  const orderSeq = {};

  function dialWidget(q, row, hb){
    const n = q.digits || 3;
    const k = teamKey(q.id);
    const vals = dialVals[k] || (dialVals[k] = new Array(n).fill(0));
    const wrap = el("div", "dial");
    for(let i = 0; i < n; i++){
      const col = el("div", "dialCol");
      const num = el("b", "", String(vals[i]));
      const up = el("button", "", "\u25B2"), down = el("button", "", "\u25BC");
      up.onclick = () => { vals[i] = (vals[i] + 1) % 10; num.textContent = String(vals[i]); };
      down.onclick = () => { vals[i] = (vals[i] + 9) % 10; num.textContent = String(vals[i]); };
      col.append(up, num, down);
      wrap.appendChild(col);
    }
    const go = el("button", "", "Try this combination");
    go.onclick = () => submit(q.id, vals.join("-"));
    row.append(wrap, go, hb);
  }

  function orderWidget(q, row, hb){
    const k = teamKey(q.id);
    const seq = orderSeq[k] || (orderSeq[k] = []);
    const wrap = el("div", "order");
    function draw(){
      wrap.innerHTML = "";
      q.cards.forEach(c => {
        const pos = seq.indexOf(c.id);
        const b = el("button", "card" + (pos >= 0 ? " used" : ""), (pos >= 0 ? (pos + 1) + ". " : "") + c.text);
        b.onclick = () => { if(seq.indexOf(c.id) < 0){ seq.push(c.id); draw(); } };
        wrap.appendChild(b);
      });
      const bar = el("div", "bdBar");
      const reset = el("button", "ghost", "Start over");
      reset.onclick = () => { seq.length = 0; draw(); };
      const go = el("button", "", "Submit this order");
      go.onclick = () => {
        if(seq.length !== q.cards.length){
          const m = $("msg-" + q.id);
          if(m){ m.className = "msg bad"; m.textContent = "Click all " + q.cards.length + " events first."; }
          return;
        }
        submit(q.id, seq.join(","));
      };
      bar.append(go, reset, hb);
      wrap.appendChild(bar);
    }
    draw();
    row.appendChild(wrap);
  }

  /* ---------------- public API ---------------- */
  window.DTS4 = {
    render: function(m){
      const root = $("dts4");
      if(!root) return;
      if(!tablesEl){
        tablesEl = el("div", "hidden");
        boardEl = el("div", "hidden");
        tablesEl.style.marginTop = "16px"; boardEl.style.marginTop = "8px";
        root.append(tablesEl, boardEl);
      }
      document.body.classList.toggle("s4", m.stage === 4);
      drawTables(m);
      drawBoardFor(m);
    },
    question: function(q, row, hb){
      if(q.kind === "dial"){ dialWidget(q, row, hb); return true; }
      if(q.kind === "order"){ orderWidget(q, row, hb); return true; }
      return false;
    }
  };
})();