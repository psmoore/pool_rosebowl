// The Rose Bowl Aquatics Center's two pools, read live from Pool Relay: which is open now and for what, the week
// pool by pool, and every lap swim hour, rec swim session, water fitness class, practice, closure and early closing the
// pages print. A closure booked on one pool clears only that pool; one booked on the center clears both.
// A notice can be timed ("Closed for UCLA football", 2–10pm; "Closes at 2pm: Christmas Eve"): it reads as a changed day,
// not a closed one. A short closure on one pool ("Pool change (closed)") stays in that pool's day as a closed block.
//
//   <div id="finder" data-view="TOKENS" data-origin="[lat,lng]">  the board on the pool page
//   <div id="today" data-view="TOKENS" data-pool="slug">           one pool's day (also any .today-board)
//   <div id="week" data-view="TOKENS">                             this week's hours, pool by pool
//
// Pool facts come from window.POOLS; an entry with `pool` reads that one pool of its facility.
(function () {
  const TZ = "America/Los_Angeles";
  const POOLS = window.POOLS || [];
  const API = "https://www.poolrelay.com/api/public/views/";

  // ── Time, in the pools' own zone ─────────────────────────────────────────────
  const parts = (d) => Object.fromEntries(new Intl.DateTimeFormat("en-US", {
    timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hourCycle: "h23",
  }).formatToParts(d).map((p) => [p.type, p.value]));
  const P = parts(new Date());
  const TODAY = `${P.year}-${P.month}-${P.day}`;
  const NOW = +P.hour * 60 + +P.minute;
  const addDays = (iso, n) => { const d = new Date(iso + "T12:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
  const mins = (hhmm) => { const [h, m] = hhmm.split(":").map(Number); return h * 60 + m; };
  const clock = (hhmm) => {
    let [h, m] = hhmm.split(":").map(Number); const ap = h >= 12 && h < 24 ? "pm" : "am"; h = h % 12 || 12;
    return m ? `${h}:${String(m).padStart(2, "0")}${ap}` : `${h}${ap}`;
  };
  const span = (a, b) => {
    const ap = (t) => (+t.split(":")[0] >= 12 ? "pm" : "am");
    return ap(a) === ap(b) ? `${clock(a).replace(/[ap]m$/, "")}–${clock(b)}` : `${clock(a)}–${clock(b)}`;
  };
  const LOC = (window.LANG || "en") === "es" ? "es-US" : "en-US";
  const weekday = (iso, style = "long") => new Date(iso + "T12:00:00Z").toLocaleDateString(LOC, { weekday: style, timeZone: "UTC" });
  const monthDay = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString(LOC, { month: "short", day: "numeric", timeZone: "UTC" });
  const LANG = window.LANG || "en";
  const T = (s) => (LANG === "es" && window.I18N && window.I18N[s]) || s;
  const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // ── Closures and modified days ───────────────────────────────────────────────
  // A closure is an all-day booking whose title says closed. "Closes at 1:00pm" is a modified day, not a closure.
  const isClosure = (o) => o.allDay && !o.partial && /clos/i.test(o.orig || o.title) && !/^closes (early|at)/i.test(o.orig || o.title);
  // A timed notice names its hours unless its title already does ("Closes at 2pm").
  const noticeText = (o) => (o.partial && !/\d/.test(o.title) ? `${o.title} (${span(o.start, o.end)})` : o.title);
  const isModified = (o) => o.allDay && !isClosure(o);
  // "Closed until further notice": its end date in the schedule is a placeholder, so never print it.
  const openEnded = (o) => /until (further notice|a reopening date is announced)/i.test(`${o.orig || o.title} ${o.description || ""}`);
  let IGNORE_OPEN = false; // read a program's published hours as if an open-ended closure weren't there
  const covers = (o, d) => o.date <= d && (o.endDate || o.date) >= d;
  // The closure holding a session's water on a day: one on the whole center, or one on the pool the session is in.
  // `where` null: any closure at all.
  const closureOn = (evs, d, where) => (evs || []).find((c) => isClosure(c) && covers(c, d) &&
    (c.where === "" || where == null || c.where === where) && !(IGNORE_OPEN && openEnded(c)));
  const modifiedOn = (evs, d) => (evs || []).find((c) => isModified(c) && covers(c, d));
  // Only the pool a POOLS entry stands for (plus closures and notices on the whole center).
  // Within one pool's list the pool goes without saying, so its sessions drop the name.
  const evsFor = (byFac, p) => (byFac[p.facility] || []).filter((o) => !p.pool || o.where === p.pool || (o.allDay && o.where === ""))
    .map((o) => (p.pool ? { ...o, hideWhere: true } : o));
  const whereOf = (o) => (o.hideWhere ? "" : o.where);

  // ── What a session is, for filtering and color ───────────────────────────────
  const KINDS = {
    lap: { label: "Lap swim" },
    rec: { label: "Family rec swim" },
    fit: { label: "Water fitness" },
    learn: { label: "Teams & lessons" },
  };
  function kindsOf(o, groupName) {
    const names = (o.groupIds || []).map((g) => groupName[g] || "").join(" ") + " " + o.title;
    const ks = [];
    if (/^closes (early|at)/i.test(o.title)) return ["other"];
    if (/lesson|learn|level|parent|team|polo|splash ball|masters|adult swim|lifeguard|swim test|academy|training|conditioning|diving|workout|swimming & diving|novice|varsity|senior|competitive|swim club|age group/i.test(names)) ks.push("learn");
    if (/water fitness|aerobic|aqua (fit|zumba|exercise|blast|kickboxing)|water exercise|deep water|twinges|sculpt|aqua jog|aquafit|gentlefit|deepfit/i.test(names)) ks.push("fit");
    if (/lap/i.test(names) && !ks.includes("learn")) ks.push("lap");
    if (/rec swim|recreation swim|open swim|public swim|family swim|family rec|wading|splash pad/i.test(names)) ks.push("rec");
    return ks.length ? ks : ["other"];
  }
  const swatch = (ks) => ks.length > 1
    ? `style="background:linear-gradient(90deg,var(--${ks[0]}) 50%,var(--${ks[1]}) 50%)"`
    : `style="background:var(--${ks[0]})"`;

  // ── Reading the schedule ─────────────────────────────────────────────────────
  // A board can read several schedules (comma-separated tokens) and merge them by pool.
  async function load(views, from, to) {
    const all = await Promise.all(String(views).split(",").map((v) => loadOne(v.trim(), from, to)));
    return Object.assign({}, ...all);
  }
  async function loadOne(view, from, to) {
    // ?preview reads a local copy of the planned schedule instead of the live one.
    const r = await fetch(/[?&]preview\b/.test(location.search) ? new URL("preview-data.json", document.querySelector('script[src*="finder.js"]').src).href
      : `${API}${view}/project?from=${from}&to=${to}`);
    if (!r.ok) throw new Error(String(r.status));
    const { occurrences, facilities, groups } = await r.json();
    // Which facility and pool every area belongs to, and how many lanes each pool has.
    // Lanes are counted per layout: a 50 m pool has 20 short-course lanes OR 8 long-course ones.
    const facOf = {}, poolOf = {}, poolName = {}, isLane = {}, lanesIn = {}, layoutOf = {}, lanesUnder = {};
    const walk = (n, fac, pool, parent) => {
      facOf[n.id] = fac; if (pool) poolOf[n.id] = pool;
      // A booking on the whole pool (water polo, no lane lines) is in that pool too.
      if (n.type === "pool") poolOf[n.id] = n.id;
      if (n.type === "pool") poolName[n.id] = n.longName;
      if (n.type === "lane") { isLane[n.id] = true; layoutOf[n.id] = parent; lanesIn[parent] = (lanesIn[parent] || 0) + 1; }
      // A booking on a whole layout (Long Course) holds every lane in it; the pool's own lanes for a pool without layouts.
      if (n.type === "config" || n.type === "pool") lanesUnder[n.id] = (n.children || []).filter((c) => c.type === "lane").map((c) => c.id);
      (n.children || []).forEach((c) => walk(c, fac, n.type === "pool" ? n.id : pool, n.id));
    };
    (facilities || []).forEach((f) => walk(f, f.longName, null, null));
    // A facility with one pool doesn't name it ("Pool 2 of 6 lanes" says nothing the page doesn't).
    const poolsAt = {};
    for (const id in poolName) poolsAt[facOf[id]] = (poolsAt[facOf[id]] || 0) + 1;
    // Pool Relay geocodes each facility from its address; use that for the map pin.
    for (const f of facilities || []) {
      POOLS.filter((x) => x.facility === f.longName).forEach((p) => { if (f.latitude != null) { p.lat = f.latitude; p.lng = f.longitude; } });
    }
    const groupName = {};
    const groupPath = {};
    const gwalk = (g, up) => { groupName[g.id] = g.longName; groupPath[g.id] = up ? `${up} / ${g.longName}` : g.longName; (g.children || []).forEach((c) => gwalk(c, groupPath[g.id])); };
    (groups || []).forEach((g) => gwalk(g, ""));
    // One program booked as several overlapping blocks on different lanes (Lap Swim on lanes 4–5 and 11–13 at once)
    // is one session: cut it at every start and end, and give each slice the lanes any of its blocks hold.
    const laneIds = (o) => o.areaIds.flatMap((a) => (isLane[a] ? [a] : lanesUnder[a] || []));
    const sliced = [], bundles = {};
    for (const o of occurrences) {
      const ls = laneIds(o);
      if (o.allDay || !ls.length) { sliced.push(o); continue; }
      (bundles[`${o.date}|${o.title}|${poolOf[o.areaIds[0]]}|${layoutOf[ls[0]]}`] ||= []).push(o);
    }
    for (const list of Object.values(bundles)) {
      const overlap = list.some((x, i) => list.some((y, j) => i !== j && x.start < y.end && y.start < x.end));
      if (!overlap) { sliced.push(...list); continue; }
      const cuts = [...new Set(list.flatMap((x) => [x.start, x.end]))].sort();
      let run = null;
      for (let i = 0; i < cuts.length - 1; i++) {
        const [t0, t1] = [cuts[i], cuts[i + 1]];
        const on = list.filter((x) => x.start <= t0 && x.end >= t1);
        const ls = [...new Set(on.flatMap(laneIds))].sort();
        const key = ls.join(",");
        if (run && run.key === key && run.end === t0 && ls.length) { run.end = t1; continue; }
        if (run) sliced.push(run);
        run = ls.length ? { ...on[0], start: t0, end: t1, areaIds: ls, key } : null;
      }
      if (run) sliced.push(run);
    }
    const byFac = {};
    for (const o of sliced) {
      const fac = facOf[o.areaIds?.[0]]; if (!fac) continue;
      const lanes = o.areaIds.flatMap((a) => (isLane[a] ? [a] : lanesUnder[a] || []));
      const pool = poolOf[o.areaIds[0]];
      const total = lanes.length ? lanesIn[layoutOf[lanes[0]]] || 0 : 0;
      // A timed notice on the whole center ("Closed for UCLA football", "Closes at 2pm: …") is a notice, not a session.
      const timedNotice = !o.allDay && !pool && /^clos/i.test(o.title);
      const ev = {
        ...o, fac, allDay: o.allDay || timedNotice, partial: timedNotice,
        kinds: o.allDay || timedNotice ? [] : /\(closed\)/i.test(o.title) ? ["shut"] : kindsOf(o, groupName),
        groupPaths: (o.groupIds || []).map((g) => groupPath[g] || ""),
        // Which pool; only a booking on the whole center has none.
        where: pool && poolsAt[fac] > 1 ? poolName[pool] : "", wanted: lanes.length, total,
        title: T(o.title), orig: o.title,
        laneText: !lanes.length || !total ? "" : lanes.length >= total ? T("all") + ` ${total} ` + T("lanes") : `${lanes.length} ` + T("of") + ` ${total} ` + T("lanes"),
      };
      (byFac[fac] ||= []).push(ev);
    }
    // One row per session: a booking on several lanes arrives once; drop exact repeats.
    for (const f in byFac) {
      const seen = new Set();
      byFac[f] = byFac[f].filter((o) => { const k = `${o.date}|${o.start}|${o.end}|${o.title}|${o.where}`; if (seen.has(k)) return false; seen.add(k); return true; })
        .sort((a, b) => (a.date + a.start).localeCompare(b.date + b.start));
      // A session whose lane count changes as lessons come and go is stored as back-to-back
      // blocks. A swimmer reads it as one session: "3–6pm, 4 to 8 lanes".
      const merged = [];
      for (const o of byFac[f]) {
        const prev = merged.findLast?.((p) => p.date === o.date && p.title === o.title && p.where === o.where && !p.allDay) ?? null;
        // Back-to-back on the same lanes is a second session (two Masters workouts), not one session changing lanes.
        if (prev && !o.allDay && prev.end === o.start && prev.parts[prev.parts.length - 1].laneText !== o.laneText) {
          prev.end = o.end; prev.parts.push(o);
        } else merged.push({ ...o, parts: [o] });
      }
      for (const m of merged) {
        if (m.parts.length < 2) continue;
        const counts = m.parts.map((p) => +(p.laneText.match(/^(\d+)|^\S+ (\d+)/) || []).slice(1).find(Boolean) || 0);
        const total = (m.parts[0].laneText.match(/(\d+) \S+$/) || [])[1];
        const lo = Math.min(...counts), hi = Math.max(...counts);
        if (total && lo !== hi) m.laneText = `${lo}–${hi} ` + T("of") + ` ${total} ` + T("lanes");
      }
      byFac[f] = merged.sort((a, b) => (a.date + a.start).localeCompare(b.date + b.start));
    }
    return byFac;
  }

  // Which sessions a pool has on a day, and what that means for a swimmer.
  function dayOf(pool, events, day, kind) {
    const evs = events || [];
    // "Anything" still means anything a member of the public can join: when a pool has lap or
    // open swim, a class doesn't count as the pool being open.
    const pub = (o) => o.kinds.includes("lap") || o.kinds.includes("rec");
    const publicPool = kind === "any" && evs.some((o) => !o.allDay && pub(o));
    const fits = (o) => (kind === "any" ? !publicPool || pub(o) : o.kinds.includes(kind));
    const closure = closureOn(evs, day, pool && pool.pool);
    const mod = modifiedOn(evs, day);
    const all = closure ? [] : evs.filter((o) => !o.allDay && o.date === day && (kind === "any" || o.kinds.includes(kind)));
    const sessions = all;          // the day's list shows everything, classes included
    const open = all.filter(fits); // the status line counts what the public can join
    const isToday = day === TODAY;
    // When several sessions are on at once, name the one most swimmers come for.
    const rank = (o) => (o.kinds.includes("lap") || o.kinds.includes("rec") ? 0 : o.kinds.includes("fit") ? 1 : 2);
    const byInterest = (a, b) => mins(a.start) - mins(b.start) || rank(a) - rank(b);
    const live = (isToday ? open.filter((o) => mins(o.start) <= NOW && NOW < mins(o.end)) : []).sort((a, b) => rank(a) - rank(b));
    const later = (isToday ? open.filter((o) => mins(o.start) > NOW) : open).slice().sort(byInterest);
    let state, line;
    const shutNow = isToday && mod && mod.partial && /^closed/i.test(mod.title) && mins(mod.start) <= NOW && NOW < mins(mod.end) ? mod : null;
    const first = evs.filter((o) => !o.allDay).reduce((m, o) => (o.date < m ? o.date : m), "9999");
    if (shutNow) {
      state = "shut";
      line = `${shutNow.title}, ${T("until")} ${clock(shutNow.end)}`;
    } else if (closure) {
      state = "shut";
      // An open-ended closure is stored with a placeholder end; say so rather than print it.
      const until = openEnded(closure) ? ", no reopening date yet" : closure.endDate && closure.endDate !== closure.date ? ` ${T("through")} ${monthDay(closure.endDate)}` : "";
      line = `${closure.title}${until}`;
    } else if (live.length) {
      state = "open";
      const o = live[0];
      const part = (o.parts || [o]).find((p) => mins(p.start) <= NOW && NOW < mins(p.end)) || o;
      const pools = live.map((x) => { const p = (x.parts || [x]).find((q) => mins(q.start) <= NOW && NOW < mins(q.end)) || x; return [whereOf(x), p.laneText].filter(Boolean).join(" "); }).filter(Boolean);
      const uniq = [...new Set(pools)];
      const classes = live.length > 1 && !live.some(pub);
      line = `${T("In the water now")}: ${classes ? `${live.length} ${T("classes")}` : o.title}${!classes && uniq.length ? ` (${uniq.join("; ")})` : ""}, ${T("until")} ${clock(live.reduce((m, x) => (x.end > m ? x.end : m), o.end))}`;
    } else if (later.length) {
      state = isToday ? "soon" : "open";
      const o = later[0];
      line = isToday ? `${T("Opens")} ${clock(o.start)}: ${o.title}` : `${o.title} ${T("from")} ${clock(o.start)}`;
    } else {
      state = "shut";
      const any = evs.some((o) => !o.allDay);
      const next = evs.find((o) => !o.allDay && o.date > day && fits(o));
      const what = kind === "any" ? "" : ` ${KINDS[kind].label.toLowerCase()}`; // eslint-disable-line
      line = !any ? T("No hours published")
        : day < first ? `${T("This day isn't in the published schedule yet")}. ${T("First published day")}: ${weekday(first)}, ${monthDay(first)}`
        : isToday && sessions.length ? `${T("Done for today")}${next ? `. ${T("Next")}: ${weekday(next.date)} ${clock(next.start)}` : ""}`
        : `${T("Nothing scheduled")} ${isToday ? T("today") : weekday(day)}${next ? `. ${T("Next")}: ${weekday(next.date)} ${clock(next.start)}` : ""}`;
    }
    if (mod && !closure && !shutNow) line += ` · ${isToday ? T("Today") : weekday(day)}: ${noticeText(mod)}`;
    return { state, line, sessions, live, closure };
  }

  // A day as a bar from 5am to 10pm, so pools can be compared at a glance.
  const T0 = 5 * 60, T1 = 22 * 60;
  function timeline(sessions, day) {
    const pct = (m) => Math.max(0, Math.min(100, ((m - T0) / (T1 - T0)) * 100));
    const bars = sessions.map((o) => {
      const l = pct(mins(o.start)), w = pct(mins(o.end)) - l;
      const ks = o.kinds;
      const bg = ks.length > 1 ? `linear-gradient(180deg,var(--${ks[0]}) 50%,var(--${ks[1]}) 50%)` : `var(--${ks[0]})`;
      return `<i style="left:${l}%;width:${w}%;background:${bg}" title="${esc(o.title)} ${span(o.start, o.end)}"></i>`;
    }).join("");
    const now = day === TODAY && NOW > T0 && NOW < T1 ? `<span class="nowline" style="left:${pct(NOW)}%"></span>` : "";
    return `<div class="tl" aria-hidden="true">${bars}${now}</div>`;
  }

  // Lesson slots come every half hour; unless someone is looking for lessons, one line says it.
  const LESSON = /lesson|academy|private|parent|mighty fish|mini fish|super fish|big fish|starfish|seahorse|otter|stroke and conditioning|adult swim (basics|refinement)/i;
  function foldLessons(sessions) {
    const les = sessions.filter((o) => LESSON.test(o.orig || o.title) && !/team|aquatics –/i.test(o.orig || o.title));
    if (les.length < 3) return sessions;
    const a = les.reduce((m, o) => (o.start < m ? o.start : m), "99:99"), b = les.reduce((m, o) => (o.end > m ? o.end : m), "00:00");
    const row = { title: `${T("Swim lessons")} · ${les.length} ${T("classes")}`, start: a, end: b, kinds: ["learn"], laneText: "", parts: les, folded: true };
    return sessions.filter((o) => !les.includes(o)).concat(row).sort((x, y) => x.start.localeCompare(y.start));
  }
  function sessionList(sessions, day, kind = "any") {
    if (kind !== "learn") sessions = foldLessons(sessions);
    return `<ul class="sess">${sessions.map((o) => {
      const cls = o.folded ? "" : day === TODAY ? (mins(o.end) <= NOW ? "past" : mins(o.start) <= NOW ? "now" : "") : "";
      return `<li class="${cls}"><span class="t">${span(o.start, o.end)}</span><span class="k" ${swatch(o.kinds)}></span>` +
        `<span>${esc(o.title)}${whereOf(o) || o.laneText ? ` <span class="n">${esc([whereOf(o), o.laneText].filter(Boolean).join(", "))}</span>` : ""}</span></li>`;
    }).join("")}</ul>`;
  }

  const miles = (a, b) => {
    const R = 3958.8, rad = Math.PI / 180;
    const dLat = (b.lat - a.lat) * rad, dLng = (b.lng - a.lng) * rad;
    const h = Math.sin(dLat / 2) ** 2 + Math.cos(a.lat * rad) * Math.cos(b.lat * rad) * Math.sin(dLng / 2) ** 2;
    return 2 * R * Math.asin(Math.sqrt(h));
  };

  // ── Schedule facts in the page's text, computed from the live schedule ──────
  // No hours, days or dates are typed into these pages. Each element with data-live fills in from
  // the same feed as the calendar, so a change in Pool Relay changes the text too.
  //   data-live="when" data-title="Lap Swim|…"  one program's week: "Mon–Fri 6:30–9:30am and 5–7:30pm; Sat 8:30–11:30am"
  //   data-live="hours"                          the pool's week, every session; data-format="dl" for a list by day
  //   data-live="swims"                          lap and rec swim by week, and what else runs there
  //   data-live="closures"                       coming closures; the element hides when there are none
  // Each also needs data-view (the feed) and data-pool (a slug in window.POOLS).
  const AHEAD = 28; // a "regular week" is read from the next four weeks
  const feeds = {};
  const feed = (view) => (feeds[view] ||= load(view, TODAY, addDays(TODAY, 120)));
  const dow = (iso) => (new Date(iso + "T12:00:00Z").getUTCDay() + 6) % 7; // Monday = 0
  const LOCALE = (window.LANG || "en") === "es" ? "es-US" : "en-US";
  const dayName = (i, style) => { const s = weekday(addDays("2024-01-01", i), style).replace(/\.$/, ""); return s[0].toUpperCase() + s.slice(1); };
  const hhmm = (m) => `${String(Math.floor(m / 60)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
  const closedOn = (evs, d, o) => !!closureOn(evs, d, o ? o.where : null);
  // A day's hours: each stretch with someone in the water, or (whole) first session to last.
  let MERGE_GAP = 15;
  function hoursOf(list, whole) {
    const iv = list.map((o) => [mins(o.start), mins(o.end)]).sort((a, b) => a[0] - b[0]);
    if (whole) return span(hhmm(iv[0][0]), hhmm(Math.max(...iv.map((x) => x[1]))));
    const out = [];
    // Back-to-back classes with a changeover of 15 minutes or less read as one stretch.
    for (const [a, b] of iv) { if (out.length && a <= out[out.length - 1][1] + MERGE_GAP) out[out.length - 1][1] = Math.max(out[out.length - 1][1], b); else out.push([a, b]); }
    const parts = out.map(([a, b]) => span(hhmm(a), hhmm(b)));
    return parts.length > 2 ? `${parts.slice(0, -1).join(", ")} ${T("and")} ${parts[parts.length - 1]}` : parts.join(` ${T("and")} `);
  }
  // A program's regular week: each weekday it runs in at least half its weeks, with that weekday's most common hours.
  // `season` reads the whole scheduled season instead of four weeks: a pool's regular hours
  // shouldn't turn "Closed" because a few Saturdays in a row are closures.
  function weekly(evs, pick, whole, season, fn) {
    const last = evs.filter((o) => !o.allDay && pick(o)).reduce((m, o) => (o.date > m ? o.date : m), TODAY);
    const end = season ? last : addDays(TODAY, AHEAD - 1);
    const byDate = {};
    // Holidays and modified days aren't regular hours: leave them out, and don't count them against a weekday.
    const odd = (d) => modifiedOn(evs, d) || evs.some((c) => isClosure(c) && covers(c, d) && c.where === "");
    for (const o of evs) if (!o.allDay && o.date >= TODAY && o.date <= end && pick(o) && !closedOn(evs, o.date, o) && !odd(o.date)) (byDate[o.date] ||= []).push(o);
    const dates = Object.keys(byDate).sort();
    if (!dates.length) return null;
    // How many of each weekday the program could have run on, between its first and last day in the window.
    const avail = Array(7).fill(0);
    for (let d = dates[0]; d <= dates[dates.length - 1]; d = addDays(d, 1)) if (!odd(d)) avail[dow(d)]++;
    const seen = Array.from({ length: 7 }, () => ({}));
    for (const d of dates) { const h = fn ? fn(byDate[d]) : hoursOf(byDate[d], whole); seen[dow(d)][h] = (seen[dow(d)][h] || 0) + 1; }
    const hours = seen.map((c, i) => {
      const n = Object.values(c).reduce((s, x) => s + x, 0);
      return n && n >= Math.ceil(avail[i] / 2) ? Object.entries(c).sort((a, b) => b[1] - a[1])[0][0] : "";
    });
    return { hours, first: dates[0], last: dates[dates.length - 1], end };
  }
  // Weekdays with the same hours, as "Mon–Fri" or "Mon/Wed/Fri".
  function dayGroups(hours, style) {
    const groups = [];
    hours.forEach((h, i) => { if (h === "") return; const g = groups.find((x) => x.h === h); g ? g.days.push(i) : groups.push({ h, days: [i] }); });
    return groups.map(({ h, days }) => {
      const runs = [];
      for (const d of days) { const r = runs[runs.length - 1]; r && d === r[r.length - 1] + 1 ? r.push(d) : runs.push([d]); }
      return { h, label: runs.map((r) => (r.length >= 3 ? `${dayName(r[0], style)}–${dayName(r[r.length - 1], style)}` : r.map((d) => dayName(d, style)).join("/\u200b"))).join("/\u200b") };
    });
  }
  function whenText(evs, pick) {
    const w = weekly(evs, pick);
    const groups = w ? dayGroups(w.hours, "short") : [];
    if (!groups.length) {
      const next = evs.find((o) => !o.allDay && o.date >= TODAY && pick(o) && !closedOn(evs, o.date, o));
      return next ? `${T("Next")}: ${weekday(next.date)} ${monthDay(next.date)}, ${span(next.start, next.end)}` : T("Nothing scheduled in the next four weeks");
    }
    let s = groups.map((g) => `${g.label} ${g.h}`).join("; ");
    if (w.first > addDays(TODAY, 6)) s = `${T("Starts")} ${monthDay(w.first)}: ${s}`;
    // "through" only when the program really ends: a holiday at the end of the window isn't its last day.
    // ...and not when the whole published schedule simply ends (the City publishes a month at a time).
    const schedLast = evs.filter((o) => !o.allDay).reduce((m, o) => (o.date > m ? o.date : m), TODAY);
    if (w.last < addDays(w.end, -6) && w.last < addDays(schedLast, -7) && !evs.some((o) => !o.allDay && o.date > w.end && pick(o))) s += `, ${T("through")} ${monthDay(w.last)}`;
    return s;
  }
  const dateRange = (a, b) => new Intl.DateTimeFormat(LOCALE, { month: "short", day: "numeric", timeZone: "UTC" })
    .formatRange(new Date(a + "T12:00:00Z"), new Date(b + "T12:00:00Z")).replace(/\s*–\s*/, "–");
  function closureList(evs, ahead = 90) {
    const seen = new Set();
    return evs.filter((o) => isClosure(o) && (o.endDate || o.date) >= TODAY && o.date <= addDays(TODAY, ahead))
      .filter((o) => { const k = `${o.orig || o.title}|${o.date}`; if (seen.has(k)) return false; seen.add(k); return true; })
      .map((o) => {
        const last = o.endDate || o.date;
        if (o.date <= TODAY) {
          // Ongoing: "Closed for the season, no reopening date yet" / "Pool closed for replastering through Nov 29".
          const open = openEnded(o);
          return `${o.title}${open ? `, ${T("no reopening date yet")}` : ` ${T("through")} ${monthDay(last)}`}`;
        }
        const when = last !== o.date ? dateRange(o.date, last) : monthDay(o.date);
        const why = o.title.replace(/^(closed|cerrado)\s*[:–—-]\s*/i, "");
        return /^(closed|cerrado)$/i.test(why.trim()) ? when : `${when} (${why})`;
      });
  }
  // Lanes a program is short of the whole pool: "4:30–6:30pm (10 of 20 lanes)". Empty when it has every lane.
  function limitedOf(list) {
    const segs = [];
    for (const o of list) for (const p of o.parts || [o]) {
      if (!p.total || p.wanted >= p.total) continue;
      const last = segs[segs.length - 1];
      if (last && last.b === p.start && last.n === p.wanted) last.b = p.end;
      else segs.push({ a: p.start, b: p.end, n: p.wanted, t: p.total });
    }
    return segs.sort((x, y) => x.a.localeCompare(y.a)).map((s) => `${span(s.a, s.b)} (${s.n} ${T("of")} ${s.t} ${T("lanes")})`).join(", ");
  }
  // An open-ended closure ("Competition Pool closed until further notice") that holds every coming session of a program.
  function heldBy(evs, pick) {
    const c = evs.find((x) => isClosure(x) && openEnded(x) && covers(x, TODAY));
    if (!c) return null;
    const up = evs.filter((o) => !o.allDay && o.date >= TODAY && pick(o));
    return up.length && up.every((o) => c.where === "" || o.where === c.where) ? c : null;
  }
  const heldNote = (c) => `<b class="held">${esc(T("On hold"))}</b> ${esc(c.title)}${openEnded(c) ? `, ${esc(T("no reopening date yet"))}` : ""}. ${esc(T("Published hours"))}: `;
  const dayLabel = (d) => `${weekday(d, "short")}, ${monthDay(d)}`;
  document.querySelectorAll("[data-live]").forEach((el) => {
    const pool = POOLS.find((p) => p.slug === el.dataset.pool.split("|")[0]);
    // data-title narrows to sessions with these exact titles ("Lap Swim (50 m)|Lap Swim (25 yd)").
    const only = el.dataset.title ? el.dataset.title.split("|") : null;
    // data-group picks a program by its group ("Coronado Aquatics / Lap Swim"): every booking under it, whatever its title.
    const grp = el.dataset.group ? el.dataset.group.split("|") : null;
    const inGroup = (o) => grp && grp.some((g) => (o.groupPaths || []).some((p) => p === g || p.endsWith(` / ${g}`) || p.includes(`${g} / `)));
    const inProgram = (o) => (grp ? inGroup(o) && (!only || only.includes(o.orig || o.title)) : !only || only.includes(o.orig || o.title));
    feed(el.dataset.view).then((byFac) => {
      const evs = evsFor(byFac, pool);
      const mode = el.dataset.live;
      // A program whose pool is closed until further notice still shows its published hours, marked on hold.
      const held = ["when", "hours", "limited", "exceptions", "held"].includes(mode) ? heldBy(evs, inProgram) : null;
      IGNORE_OPEN = !!held;
      try {
        if (mode === "held") {
          // A line saying the program is on hold, or nothing.
          el.hidden = !held;
          if (held) el.innerHTML = `<b class="held">${esc(T("On hold"))}</b> ${esc(held.title)}${openEnded(held) ? `, ${esc(T("no reopening date yet"))}` : ""}. ${esc(el.dataset.text || "")}`;
        } else if (mode === "when") {
          // data-gap="-1": list each class on its own instead of reading back-to-back classes as one stretch.
          if (el.dataset.gap !== undefined) MERGE_GAP = +el.dataset.gap;
          const t = whenText(evs, inProgram);
          MERGE_GAP = 15;
          el.innerHTML = (held && el.dataset.quiet === undefined ? heldNote(held) : "") + esc(t);
          if (held) el.classList.add("is-held");
        } else if (mode === "hours") {
          // data-whole="0": each stretch ("6am–1pm and 3–8pm") instead of first session to last.
          const w = weekly(evs, (o) => inProgram(o) && !o.allDay, el.dataset.whole !== "0", true);
          const hours = (w ? w.hours : Array(7).fill("")).map((h) => h || T("Closed"));
          const groups = dayGroups(hours, el.dataset.format === "dl" ? "long" : "short");
          el.innerHTML = (held ? `<p class="small" style="margin:0 0 6px">${heldNote(held)}</p>` : "") + (el.dataset.format === "dl"
            ? `<dl>${groups.map((g) => `<dt>${esc(g.label)}</dt><dd>${esc(g.h)}</dd>`).join("")}</dl>`
            : esc(groups.map((g) => `${g.label} ${g.h}`).join("; ")));
        } else if (mode === "limited") {
          // When a program has fewer than all the pool's lanes, weekday by weekday.
          // data-compact: just the fewest and most lanes each weekday ("3–17 of 20 lanes"), for a pool whose count moves all day.
          const compact = (list) => {
            const ps = list.flatMap((o) => o.parts || [o]).filter((p) => p.total);
            if (!ps.length || ps.every((p) => p.wanted >= p.total)) return "";
            const lo = Math.min(...ps.map((p) => p.wanted)), hi = Math.max(...ps.map((p) => p.wanted)), t = ps[0].total;
            return lo === hi ? `${lo} ${T("of")} ${t} ${T("lanes")}` : `${lo}–${hi} ${T("of")} ${t} ${T("lanes")}`;
          };
          const w = weekly(evs, inProgram, false, false, el.dataset.compact !== undefined ? compact : limitedOf);
          const groups = w ? dayGroups(w.hours, "short") : [];
          el.innerHTML = groups.length ? `<ul>${groups.map((g) => `<li><b>${esc(g.label)}:</b> ${esc(g.h)}</li>`).join("")}</ul>`
            : esc(el.dataset.empty || T("Every lane, all published hours."));
        } else if (mode === "exceptions") {
          // Days whose hours differ from that weekday's regular hours: closures and modified days.
          const w = weekly(evs, inProgram, true, true);
          const open = evs.filter((o) => !o.allDay && inProgram(o));
          const wheres = new Set(open.map((o) => o.where));
          const lastDay = open.map((o) => o.date).filter((d) => d <= addDays(TODAY, 90)).reduce((m, d) => (d > m ? d : m), TODAY);
          const rows = [];
          // Start where the published schedule does: a day it doesn't reach yet isn't a closed day.
          const firstPub = evs.filter((o) => !o.allDay).reduce((m, o) => (o.date < m ? o.date : m), "9999");
          for (let d = firstPub > TODAY ? firstPub : TODAY; d <= lastDay && rows.length < 12; d = addDays(d, 1)) {
            // A closure on one pool closes the day only for a program that runs in no other pool.
            const cls = evs.filter((c) => isClosure(c) && covers(c, d) && !(IGNORE_OPEN && openEnded(c)));
            const closure = cls.find((c) => c.where === "") || (wheres.size && [...wheres].every((w) => cls.some((c) => c.where === w)) ? cls[0] : null);
            const mod = modifiedOn(evs, d);
            const on = open.filter((o) => o.date === d && !closedOn(evs, d, o));
            const regular = w ? w.hours[dow(d)] : "";
            const h = closure ? (regular || on.length ? T("Closed") : "") : on.length ? hoursOf(on, true) : regular ? T("Closed") : "";
            if ((h !== regular && (h || regular)) || (mod && (regular || on.length))) {
              const prev = rows[rows.length - 1];
              if (prev && prev.h === h && h === T("Closed") && prev.to === addDays(d, -1) && prev.why === (closure ? closure.title.replace(/^closed( for|:)?\s*/i, "") : "")) prev.to = d;
              else rows.push({ from: d, to: d, h, why: closure ? closure.title.replace(/^closed( for|:)?\s*/i, "") : mod ? mod.title : "" });
            }
          }
          el.hidden = !rows.length;
          el.innerHTML = `<ul>${rows.map((r) => `<li><b>${esc(r.from === r.to ? dayLabel(r.from) : `${dayLabel(r.from)} – ${dayLabel(r.to)}`)}:</b> ${esc(r.h)}${r.why && r.why.toLowerCase() !== r.h.toLowerCase() ? ` (${esc(r.why)})` : ""}</li>`).join("")}</ul>`;
        } else if (mode === "alerts") {
          // Every closure and modified day from today on, the ongoing ones first: what the Alert Center and Holiday Hours page say.
          const ahead = +(el.dataset.ahead || 90);
          const seen = new Set();
          const list = evs.filter((o) => o.allDay && (o.endDate || o.date) >= TODAY && o.date <= addDays(TODAY, ahead))
            .filter((o) => { const k = `${o.orig}|${o.date}`; if (seen.has(k)) return false; seen.add(k); return true; })
            // Two one-day closures in a row with one name ("Closed for Thanksgiving") read as one closure.
            .reduce((acc, o) => { const p = acc[acc.length - 1]; if (p && !o.partial && !p.partial && p.orig === o.orig && addDays(p.endDate || p.date, 1) === o.date) acc[acc.length - 1] = { ...p, endDate: o.endDate || o.date }; else acc.push(o); return acc; }, []);
          el.hidden = !list.length;
          if (!list.length) return;
          const when = (o) => {
            const last = o.endDate || o.date;
            if (o.date <= TODAY) return openEnded(o) ? `${T("Since")} ${dayLabel(o.date)}, ${T("no reopening date yet")}` : last === TODAY ? T("Today") : `${T("Now")}, ${T("through")} ${dayLabel(last)}`;
            return last !== o.date ? `${dayLabel(o.date)} – ${dayLabel(last)}` : dayLabel(o.date);
          };
          el.innerHTML = `<ul>${list.map((o) => `<li class="${isClosure(o) ? "cl" : "mod"}"><b>${esc(when(o))}</b><span>${esc(noticeText(o))}${o.where ? "" : ` <span class="muted">(${esc(T("whole center"))})</span>`}</span></li>`).join("")}</ul>`;
        } else if (mode === "dates") {
          const list = evs.filter((o) => !o.allDay && o.date >= TODAY && inProgram(o) && !closedOn(evs, o.date, o));
          el.innerHTML = list.length ? esc(list.map((o) => `${dayLabel(o.date)}, ${span(o.start, o.end)}`).join("; "))
            : esc(el.dataset.empty || T("Nothing scheduled in the next four weeks"));
        } else if (mode === "closures") {
          const list = closureList(evs, +(el.dataset.ahead || 90));
          el.hidden = !list.length;
          if (!list.length) return;
          const label = T(el.dataset.label || "Closed");
          el.innerHTML = list[0].toLowerCase().startsWith(label.toLowerCase()) ? `${esc(list.join("; "))}.` : `<b>${esc(label)}:</b> ${esc(list.join("; "))}.`;
        }
      } finally { IGNORE_OPEN = false; }
    }).catch(() => { el.textContent = T("See the calendar for times."); });
  });

  // ── One pool's day ──────────────────────────────────────────────────────────
  // <div id="today" data-view data-pool="slug">: right now and the rest of today, one pool.
  document.querySelectorAll("#today, .today-board").forEach((single) => {
    const pool = POOLS.find((p) => p.slug === single.dataset.pool);
    load(single.dataset.view, TODAY, addDays(TODAY, 14)).then((byFac) => {
      const d = dayOf(pool, evsFor(byFac, pool), TODAY, "any");
      single.innerHTML = `<div class="pool"><div>
        <p class="state ${d.state}" style="margin-top:0"><span class="dot"></span>${esc(d.line)}</p>
        ${d.sessions.length ? timeline(d.sessions, TODAY) + `<div class="tlscale"><span>5am</span><span>${T("noon")}</span><span>5pm</span><span>10pm</span></div>` + sessionList(d.sessions, TODAY) : ""}
      </div></div>`;
    }).catch(() => { single.innerHTML = `<p class="muted">The live schedule didn't load. The calendar below has every session.</p>`; });
  });

  // ── This week, pool by pool, with how many lanes ───────────────────────────
  // <div id="week" data-view data-pool="slug" data-pools="Competition Pool|Recreation Pool">: one column per pool.
  // A closure on the whole center spans the row; one on a pool fills only that pool's column.
  const week = document.getElementById("week");
  if (week) {
    const days7 = Array.from({ length: 7 }, (_, i) => addDays(TODAY, i));
    const cols = week.dataset.pools.split("|");
    load(week.dataset.view, TODAY, addDays(TODAY, 7)).then((byFac) => {
      const p = POOLS.find((x) => x.slug === week.dataset.pool) || POOLS[0];
      const evs = byFac[p.facility] || [];
      const only = week.dataset.kind ? week.dataset.kind.split("|") : null;
      const lanesOf = (o) => (o.laneText || "").replace(/ of \d+ lanes$/, " lanes");
      // Cells first, so a closure running several days fills one tall cell instead of repeating.
      const grid = days7.map((d) => {
        const all = evs.find((c) => isClosure(c) && covers(c, d) && c.where === "");
        const mod = modifiedOn(evs, d);
        const head = `<th>${weekday(d, "short")} ${monthDay(d)}${mod ? `<div class="mod">${esc(noticeText(mod))}</div>` : ""}</th>`;
        if (all) return { head, cls: "shut", whole: esc(all.title) };
        return { head, cells: cols.map((c) => {
          const cl = closureOn(evs, d, c);
          if (cl) return { shut: cl, html: esc(cl.title) };
          const on = evs.filter((o) => !o.allDay && o.date === d && o.where === c && (!only || o.kinds.some((k) => only.includes(k))));
          if (!on.length) return { html: `<span class="muted">—</span>` };
          return { html: on.map((o) => `<div><span class="k k-${o.kinds[0] || "other"}"></span><b>${esc(o.title)}</b> ${span(o.start, o.end)}${lanesOf(o) ? ` <span class="n">${esc(lanesOf(o))}</span>` : ""}</div>`).join("") };
        }) };
      });
      grid.forEach((r, i) => (r.cells || []).forEach((c, k) => {
        if (!c.shut) return;
        // Walk back to the first row of this closure in this column and grow its rowspan.
        let j = i - 1;
        while (j >= 0 && grid[j].cells && grid[j].cells[k].shut === c.shut && grid[j].cells[k].skip) j--;
        const top = j >= 0 && grid[j].cells && grid[j].cells[k].shut === c.shut ? grid[j].cells[k] : null;
        if (top) { top.span = (top.span || 1) + 1; c.skip = true; }
      }));
      const rows = grid.map((r) => r.whole ? `<tr class="shut">${r.head}<td colspan="${cols.length}">${r.whole}</td></tr>`
        : `<tr>${r.head}${r.cells.map((c) => c.skip ? "" : `<td${c.shut ? ` class="shut"${c.span ? ` rowspan="${c.span}"` : ""}` : ""}>${c.html}</td>`).join("")}</tr>`).join("");
      week.innerHTML = `<div class="tblwrap"><table class="lanes"><thead><tr><th></th>${cols.map((h) => `<th>${esc(h)}</th>`).join("")}</tr></thead><tbody>${rows}</tbody></table></div>`;
    }).catch(() => { week.innerHTML = `<p class="muted">The live schedule didn't load. The calendar below has every session.</p>`; });
  }

  // ── The swim-now board ──────────────────────────────────────────────────────
  // <div id="finder" data-view>: each pool in window.POOLS, open now or later, for what.
  const root = document.getElementById("finder");
  if (!root) return;
  const state = { day: root.dataset.day === "today" ? TODAY : root.dataset.day || "now", kind: root.dataset.kind || "any", area: "all", me: null };
  // Every pool is also measured from the pool it stands in for, so the list reads "how far
  // from the Laguna Beach pool" before anyone shares a location.
  const origin = root.dataset.origin ? (([lat, lng]) => ({ lat, lng }))(JSON.parse(root.dataset.origin)) : null;
  const days = Array.from({ length: 7 }, (_, i) => addDays(TODAY, i));
  const dayChips = [["now", "Right now"], [TODAY, "Today"], ...days.slice(1).map((d, i) => [d, i === 0 ? "Tomorrow" : weekday(d, "short")])];
  const areas = ["all", ...Array.from(new Set(POOLS.filter((p) => p.kind === "yearRound").map((p) => p.area))).sort()];

  const chipRow = (name, items, cur) => `<div class="chips" role="group">${items.map(([v, l]) =>
    `<button type="button" class="chip" data-${name}="${v}" aria-pressed="${v === cur}">${esc(l)}</button>`).join("")}</div>`;
  root.innerHTML = `
    <div class="bar">
      <fieldset><legend>When</legend>${chipRow("day", dayChips, state.day)}</fieldset>
      <fieldset><legend>To do</legend>${chipRow("kind", [["any", "Anything"], ...Object.entries(KINDS).filter(([k]) => k !== "learn").map(([k, v]) => [k, v.label])], state.kind)}</fieldset>
      ${areas.length > 2 ? `<fieldset><legend>Where</legend>${chipRow("area", areas.map((a) => [a, a === "all" ? (root.dataset.allLabel || "Everywhere") : a]), state.area)}
        <div class="chips" style="margin-top:6px"><button type="button" class="chip near" data-near aria-pressed="false">📍 Nearest to me</button></div></fieldset>` : ""}
    </div>
    <div class="summary" aria-live="polite"><span class="muted">Loading both pools…</span></div>
    <div class="split"><ol class="results"></ol><div id="map" role="region" aria-label="Map of pools"></div></div>
    <div class="legend"><span class="k-lap">Lap swim</span><span class="k-rec">Family rec swim</span><span class="k-fit">Water fitness</span><span class="k-learn">Teams &amp; lessons</span><span class="k-other">Other bookings</span><span class="k-shut">Pool closed</span></div>`;
  const list = root.querySelector(".results");
  const summary = root.querySelector(".summary");

  let map = null, markers = {};
  function drawMap(rows) {
    if (!window.L) return;
    if (!map) {
      map = L.map("map", { scrollWheelZoom: false }).setView(JSON.parse(root.dataset.center || "[34.03,-118.35]"), +(root.dataset.zoom || 10));
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 18, attribution: "© OpenStreetMap contributors" }).addTo(map);
    }
    Object.values(markers).forEach((m) => m.remove()); markers = {};
    const color = { open: "#1f8a4c", soon: "#c27c0e", shut: "#8a8278" };
    for (const r of rows) {
      const m = L.circleMarker([r.p.lat, r.p.lng], {
        radius: r.p.kind === "yearRound" ? (r.d.state === "shut" ? 6 : 9) : 4,
        color: "#fff", weight: 1.5, fillColor: color[r.d.state], fillOpacity: r.p.kind === "yearRound" ? 0.95 : 0.5,
      }).addTo(map);
      m.bindPopup(`<b>${esc(r.p.name)}</b><br>${esc(r.d.line)}<br><a href="${esc(r.p.href)}">Hours and details</a>`);
      m.on("click", () => { const el = document.getElementById("p-" + r.p.slug); if (el) { el.classList.add("hl"); el.scrollIntoView({ block: "nearest", behavior: "smooth" }); setTimeout(() => el.classList.remove("hl"), 1600); } });
      markers[r.p.slug] = m;
    }
    if (origin) {
      markers.__origin = L.circleMarker([origin.lat, origin.lng], { radius: 8, color: "#fff", weight: 2, fillColor: "#b3261e", fillOpacity: 1 })
        .addTo(map).bindPopup(esc(root.dataset.originName || "Origin"));
    }
    if (state.me) {
      markers.__me = L.circleMarker([state.me.lat, state.me.lng], { radius: 7, color: "#fff", weight: 2, fillColor: "#2f6fb3", fillOpacity: 1 }).addTo(map).bindPopup("You are here");
    }
  }

  let byFac = null;
  function render() {
    const day = state.day === "now" ? TODAY : state.day;
    const yr = POOLS.filter((p) => p.kind === "yearRound" && (state.area === "all" || p.area === state.area));
    const rows = yr.map((p) => {
      const d = p.facility ? dayOf(p, evsFor(byFac, p), day, state.kind)
        : { state: "shut", line: p.closedNote || "Closed", sessions: [], live: [] };
      return { p, d, dist: state.me ? miles(state.me, p) : origin ? miles(origin, p) : null };
    });
    const rank = { open: 0, soon: 1, shut: 2 };
    rows.sort((a, b) => {
      if (state.day === "now" || day === TODAY) { const r = rank[a.d.state] - rank[b.d.state]; if (r) return r; }
      else { const r = (a.d.state === "shut") - (b.d.state === "shut"); if (r) return r; }
      if (state.me || origin) return a.dist - b.dist;
      const sa = a.d.live[0]?.end || a.d.sessions.find((o) => day !== TODAY || mins(o.end) > NOW)?.start || "99";
      const sb = b.d.live[0]?.end || b.d.sessions.find((o) => day !== TODAY || mins(o.end) > NOW)?.start || "99";
      return sa.localeCompare(sb) || a.p.name.localeCompare(b.p.name);
    });
    const shown = state.day === "now" ? rows.filter((r) => r.d.state === "open") : rows.filter((r) => r.d.state !== "shut");
    const rest = rows.filter((r) => !shown.includes(r));
    const what = state.kind === "any" ? "" : ` for ${KINDS[state.kind].label.toLowerCase()}`;
    const where = state.area === "all" ? "" : ` in ${state.area}`;
    const when = state.day === "now" ? `right now (${clock(`${P.hour}:${P.minute}`)})` : day === TODAY ? "today" : `on ${weekday(day)}, ${monthDay(day)}`;
    summary.innerHTML = `<b>${shown.length} of ${rows.length} pools</b><span>open${what}${where} ${when}.</span>` +
      (state.day === "now" && !shown.length ? `<span class="muted">Try “Today” to see what opens later.</span>` : "");

    const card = (r) => {
      const { p, d } = r;
      const ses = d.sessions;
      return `<li class="pool" id="p-${p.slug}">
        <div class="ph" ${p.photo ? `style="background-image:url('${esc(p.photo)}')"` : ""} role="img" aria-label=""></div>
        <div>
          <h3><a href="${esc(p.href)}">${esc(p.name)}</a></h3>
          <div class="where">${esc(p.sub || p.area)}${r.dist != null ? ` · <b>${r.dist.toFixed(1)} mi</b>${state.me ? "" : ` <span class="muted">${esc(root.dataset.originLabel || "away")}</span>`}` : ""}</div>
          <p class="state ${d.state}"><span class="dot"></span>${esc(d.line)}</p>
          ${ses.length ? timeline(ses, day) + sessionList(ses, day, state.kind) : ""}
        </div></li>`;
    };
    list.innerHTML = (shown.length ? shown.map(card).join("") : `<li class="empty">No pool${where} matches. ${rest.length ? "The closest options are below." : ""}</li>`) +
      (rest.length ? `<li class="later-h">${state.day === "now" ? "Not open right now" : "No matching sessions that day"} · ${rest.length}</li>` + rest.map(card).join("") : "");
    drawMap(rows.concat(state.area === "all" ? POOLS.filter((p) => p.kind !== "yearRound").map((p) => ({ p, d: { state: "shut", line: p.closedNote || "Closed until summer" } })) : []));
  }

  root.addEventListener("click", (e) => {
    const b = e.target.closest("button.chip"); if (!b) return;
    if (b.hasAttribute("data-near")) {
      if (state.me) { state.me = null; b.setAttribute("aria-pressed", "false"); b.textContent = "📍 Nearest to me"; render(); return; }
      b.textContent = "📍 Finding you…";
      navigator.geolocation?.getCurrentPosition((pos) => {
        state.me = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        b.setAttribute("aria-pressed", "true"); b.textContent = "📍 Nearest first";
        render();
        if (map) map.setView([state.me.lat, state.me.lng], 12);
      }, () => { b.textContent = "📍 Location unavailable"; });
      return;
    }
    for (const k of ["day", "kind", "area"]) {
      if (b.dataset[k] !== undefined) {
        state[k] = b.dataset[k];
        root.querySelectorAll(`[data-${k}]`).forEach((x) => x.setAttribute("aria-pressed", String(x.dataset[k] === state[k])));
      }
    }
    if (byFac) render();
  });

  load(root.dataset.view, TODAY, addDays(TODAY, 7))
    .then((d) => { byFac = d; render(); })
    .catch(() => { summary.innerHTML = `<span>The live schedule didn't load. Each pool's page has its calendar.</span>`; });
})();
