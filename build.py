#!/usr/bin/env python3
"""Build the Rose Bowl Aquatics Center preview: Home, Lap Swim, Family Recreational Swim, Water Fitness & Wellness, Swim
Lessons, the team pages (Swim Team, Water Polo, Dive Team, Rays, Masters) and Calendars, in the look of rosebowlaquatics.org, with every hour, session, class, practice,
closure and early closing read live from Pool Relay by finder.js (#finder, .today-board, #week, data-live).

Nothing about WHEN a pool is open is typed here: only prices, ages, ratios, policies, descriptions and facts about the
water. RBAC's own schedule text appears only as labeled quotes beside the live version.
Run: python3 build.py   (then python3 check.py)"""
import hashlib, html, json

E = html.escape
COMP = "FgHEbQHJyQ9xrnxBa1FmYt"  # Pool Relay tab: Rose Bowl Competition Pool, lane by lane
DIVE = "430wOk0AHmfQrpXaag7Hrs"  # Pool Relay tab: Rose Bowl Dive & Rec Pool, lane by lane
WEEK = "ldh1B3ldemNOlqrz69lAVa"  # Pool Relay tab: Rose Bowl Aquatics Center, week (both pools; feeds every live element)
# A program's page embeds a tab locked to that program's group, so its calendar shows only that program.
LAP_COMP = "lGMh1lF6ZPQkYH4AEKEwC9"   # Lap Swim, Competition Pool lane by lane
LAP_DIVE = "NYCzecS1JPKyAfMrxcTKQs"   # Lap Swim, Dive & Rec Pool lane by lane
MASTERS = "tUrgh3T3PBSjosKGCD3y8v"    # Masters, Competition Pool lane by lane
REC_TAB = "tLcJFojRzuyDeqaNfAeuKT"        # Family Recreational Swim, week
FIT = "YmdcazrCwslIbrYSMAHe3P"        # Water Fitness & Wellness, week
LESSONS_TAB = "3kW9Hqs7rgsmDukChClTRt"    # Swim Lessons, week
SWIM_TAB = "GJAqqJ9is2xRW6F8YVOHQL"   # Swim Team, Competition Pool lane by lane
POLO_TAB = "iy9F70sZq6N9ZFdrSlPs1Q"   # Water Polo Team, week (both pools)
DIVE_TAB = "OlV4FkpT5I0GxYhbdMzMsJ"   # Dive Team, Dive & Rec Pool lane by lane
RAYS_TAB = "i2vGOoejn4ZbCBMz9hblnn"   # Rays Swim Team, week (both pools)
RB = "https://rosebowlaquatics.org"
FAC = "Rose Bowl Aquatics Center"
ADDRESS = "360 N. Arroyo Blvd., Pasadena, CA 91103"
POOLS = [
    dict(slug="comp", name="Competition Pool", facility=FAC, pool="Competition Pool", area="Pasadena", kind="yearRound",
         href="lap-swim.html#comp", sub="50 m · 8 long-course or 20 short-course lanes · typically 79°"),
    dict(slug="rec", name="Dive & Rec Pool", facility=FAC, pool="Dive & Rec Pool", area="Pasadena", kind="yearRound",
         href="lap-swim.html#dive", sub="20 lanes · shallow end for rec swim, deep end for diving · typically 86°"),
    dict(slug="ctr", name=FAC, facility=FAC, area="Pasadena", kind="center", href="index.html"),
]
VER = hashlib.sha1((open("finder.js").read() + open("style.css").read()).encode()).hexdigest()[:8]


def out(href, label, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<a{c} href="{E(href)}" target="_blank" rel="noopener noreferrer">{label}</a>'


def live(mode, pool="ctr", **kw):
    attrs = "".join(f' data-{k.replace("_", "-")}="{E(str(v))}"' for k, v in kw.items())
    return f'data-live="{mode}" data-view="{WEEK}" data-pool="{pool}"{attrs}'


def frame(token, title, height=820):
    return (f'<div class="frame"><iframe src="https://www.poolrelay.com/embed/{token}" height="{height}" title="{E(title)}" '
            f'loading="lazy"></iframe></div><p class="credit">Schedule by {out("https://www.poolrelay.com/", "Pool Relay")}</p>')


def quote(text, src, label, who="RBAC’s own text"):
    return f'<blockquote class="quote"><span class="qh">{E(who)}, quoted from {out(src, label)}</span>“{E(text)}”</blockquote>'


LIVE = '<span class="live-tag">Live</span>'

# ── Navigation: the pages built here, and RBAC's real pages for everything else ──
MENU = [
    ("Programs", "Our Programs", [
        ("Swim Lessons", "swim-lessons.html"), ("Water Fitness & Wellness", "water-fitness.html"),
        ("Adaptive Swim Lessons", RB + "/adaptive-swim-lessons"), ("Anderson Adventure Camp H20", RB + "/camp"),
        ("Family Recreational Swim", "rec-swim.html"), ("Lap Swim", "lap-swim.html"), ("Therapy Pool", RB + "/therapy-pool"),
        ("Red Cross Training/Lifeguard", RB + "/red-cross"), ("Yoga", RB + "/yoga")]),
    ("Teams", "Our Teams", [
        ("Dive Team", "dive-team.html"), ("Swim Team", "swim-team.html"), ("Water Polo Team", "water-polo.html"),
        ("Rays Swim Team", "rays.html"), ("Masters Swim Team", "masters.html")]),
    ("Giving", "Giving", [
        ("Events", RB + "/events"), ("Why Donate?", RB + "/support"), ("Ways to Give", RB + "/ways-to-give"),
        ("Directing Your Gift", RB + "/directing-gift"), ("Donation Request", RB + "/donation-request")]),
    ("About", "About Us", [
        ("Contact Us", RB + "/Contact-Us"), ("About", RB + "/about"), ("Calendars", "calendars.html"), ("Visit RBAC", RB + "/visit"),
        ("Leadership", RB + "/staff"), ("Board of Directors", RB + "/board"), ("RBAC Guidelines", RB + "/guidelines"),
        ("Air Quality Monitoring", RB + "/air-quality"), ("Employment", RB + "/employment"),
        ("Apply for Financial Assistance", RB + "/financial-assistance")]),
]


def link(label, href, here):
    if href.startswith("http"):
        return out(href, E(label), "ext")
    cls = ' class="here"' if href == here else ""
    return f'<a href="{href}"{cls}>{E(label)}</a>'


def page(file, title, hero, body, anchors=()):
    nav = "".join(f'<div class="dd"><button type="button" aria-haspopup="true">{E(top)}</button><div class="panel"><h3>{E(head)}</h3>'
                  + "".join(link(l, h, file) for l, h in items) + "</div></div>" for top, head, items in MENU)
    mnav = "".join(f"<h4>{E(top)}</h4>" + "".join(link(l, h, file) for l, h in items) for top, _, items in MENU)
    if hero is None:
        hero_html = ""
    else:
        hero_html = (f'<div class="hero water"><div class="wrap"><h1>{E(hero)}</h1><ul>'
                     + "".join(f'<li><a href="#{a}">{E(l)}</a></li>' for a, l in anchors) + "</ul></div></div>")
    doc = f"""<!doctype html>
<!-- UNOFFICIAL PREVIEW. Not a Rose Bowl Aquatics Center website. A mock-up of {RB}
     with the schedule on live Pool Relay calendars. Built to demonstrate Pool Relay; not affiliated with RBAC. -->
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{E(title)} | Rose Bowl Aquatics Center (unofficial preview)</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css?v={VER}">
</head>
<body>
<div class="preview-note"><b>Unofficial preview — not a Rose Bowl Aquatics Center website.</b> A mock-up of {out(RB, "rosebowlaquatics.org")} with its schedules on live {out("https://www.poolrelay.com/", "Pool Relay")} calendars.</div>
<header class="site"><div class="hdr">
  <a class="brand" href="index.html" aria-label="RBAC preview home"><span class="rb">RBAC</span><span class="rb-sub">Rose Bowl Aquatics Center</span><span class="wave" aria-hidden="true"></span><span class="np">A 501(c)(3) Nonprofit Organization</span></a>
  <nav class="main" aria-label="Main">{nav}</nav>
  <div class="right">{out(RB + "/login-page", "Program Login/Passes", "btn-login")}
    <details class="mnav"><summary><i aria-hidden="true"></i>MENU</summary><div class="mpanel">{mnav}</div></details></div>
  {out(RB + "/donate", "Donate", "donate")}
</div></header>
<main>
{hero_html}
{body}
</main>
<div class="work"><h3>Work at the RBAC</h3>{out(RB + "/employment", "View Openings")}</div>
<footer class="site"><div class="wrap">
  <div class="cols">
    <div><h4>Public Swim Hours {LIVE}</h4><div {live("hours", "ctr", group="Lap Swim|Family Recreational Swim|Water Fitness & Wellness", format="dl")}>…</div>
      <p class="small" style="margin:6px 0 0">First lap swim, rec swim or water fitness session to the last, from the live schedule.</p></div>
    <div><h4>Rose Bowl Aquatics Center</h4><p style="margin:0">{E(ADDRESS)}<br>Phone: <a href="tel:6265640330">626.564.0330</a><br>
      {out(RB + "/Contact-Us", "Contact Us")}</p></div>
    <div><h4>Closures &amp; early closings {LIVE}</h4><div {live("alerts", ahead=60)} class="foot-alerts"><p>None coming up.</p></div></div>
  </div>
  <p class="disc"><b>Unofficial preview.</b> Built to demonstrate embedded {out("https://www.poolrelay.com/", "Pool Relay")} schedules. Not operated by,
    endorsed by or affiliated with the Rose Bowl Aquatics Center. The schedule was entered from RBAC's public Competition Pool and
    Dive/Rec Pool Google Calendars; on the Competition Pool those give a lane count, so which lanes is Pool Relay's estimate.
    Prices and policies are copied from {out(RB, "rosebowlaquatics.org")}, which remains the official source. No RBAC logo or photos are used.</p>
</div></footer>
<script>window.POOLS = {json.dumps(POOLS)};</script>
<script src="finder.js?v={VER}"></script>
</body>
</html>
"""
    open(file, "w").write(doc)


ALERTS = f"""<div class="alert" aria-live="polite"><h3>Closures &amp; early closings {LIVE}</h3>
  <div {live("alerts", ahead=100)}><p class="muted">None coming up.</p></div></div>"""

# ── Home ─────────────────────────────────────────────────────────────────────
TILE_PROGS = [("Swim Lessons", "swim-lessons.html", "#0d77b0"), ("Lap Swim", "lap-swim.html", "#0a5f8f"),
              ("Family Recreational Swim", "rec-swim.html", "#1fa6c4"), ("Water Fitness & Wellness", "water-fitness.html", "#2a7fb8"),
              ("Masters Swim Team", "masters.html", "#06476e"), ("Dive Team", "dive-team.html", "#0b6aa0")]
prog_tiles = "".join(
    (out(h, f"<span>{E(l)}</span>", "water ext") if h.startswith("http") else f'<a class="water" href="{h}"><span>{E(l)}</span></a>')
    for l, h, _ in TILE_PROGS)
page("index.html", "Home", None, f"""
<div class="home-hero"><div class="pic water"><span>Two pools, one live schedule: the Competition Pool and the Dive &amp; Rec Pool, lane by lane.</span></div>
  <span class="squiggle" aria-hidden="true"></span>
  <h2 class="tagline">Dedicated to water safety &amp; building community connections</h2>
  <p class="lede">Promoting wellness and a love for aquatic activities, at 360 N. Arroyo Blvd. in Pasadena.</p></div>
<div class="tiles"><a class="t-red" href="#programs"><b>Programs</b><span>View Programs</span></a>
  <a class="t-navy" href="#now"><b>Can I swim now?</b><span>See what's open</span></a></div>

<section class="band" id="now"><div class="wrap">
  <h2 class="sec-title">Where can I swim right now? {LIVE}</h2>
  <p class="lede">Both pools from the same schedule the front desk keeps: what's in the water, how many lanes it has, and what's next.
    Pick a day or an activity.</p>
  {ALERTS}
  <div id="finder" class="finder" data-view="{WEEK}" data-all-label="Both pools"></div>
</div></section>

<section class="band tint"><div class="wrap">
  <h2 class="sec-title">Lap swim and rec swim this week {LIVE}</h2>
  <p class="small muted">Each session says how many of its pool's lanes it has. Closures and early closings show in their own row.</p>
  <div id="week" data-view="{WEEK}" data-pool="ctr" data-pools="Competition Pool|Dive &amp; Rec Pool" data-kind="lap|rec"><p class="muted">Loading the week…</p></div>
</div></section>

<section class="band" id="programs"><div class="wrap">
  <h2 class="sec-title">An innovative aquatics facility</h2>
  <div class="prog-grid">{prog_tiles}</div>
  <h2 class="sec-title" style="margin-top:34px">The whole week on one calendar {LIVE}</h2>
  <p class="small muted">Every program in both pools, each block naming its pool. Use the filter row to pick a program; its
    <b>Subscribe</b> button emails you when that program's schedule changes.</p>
  {frame(WEEK, "Rose Bowl Aquatics Center, week", 900)}
</div></section>

<section class="band tint"><div class="wrap">
  <h2 class="sec-title">What's different in this preview</h2>
  <div class="before-after">
    <div class="b"><h3>Today on rosebowlaquatics.org</h3><ul>
      <li>Two Google Calendars in agenda mode, one per pool, with entries titled like “Lap Swim - Lanes 6-20” and “Master's Team - 10 lanes SC”.</li>
      <li>To know what's open, a swimmer reads both lists and works out the lanes.</li>
      <li>Program pages type their times by hand (Family Rec Swim, Masters, each water fitness class), separate from the calendars.</li></ul></div>
    <div class="a"><h3>In this preview</h3><ul>
      <li>One schedule. Each pool drawn lane by lane, plus a week view of both.</li>
      <li>A “swim now” board that counts the lap lanes open right now in each pool.</li>
      <li>Every hour on every page is computed from that schedule, so a change at the desk shows up everywhere at once.</li>
      <li>Closures and early closings (holidays, UCLA football) appear on their own, and clear those hours from every list.</li>
      <li>Each program page shows only its program, and families can subscribe to a program for change emails.</li></ul></div>
  </div>
  <p class="small"><a href="calendars.html">More on the calendars →</a></p>
</div></section>
""")

# ── Lap Swim ─────────────────────────────────────────────────────────────────
LAP = "Lap Swim"
page("lap-swim.html", "Lap Swim", "Lap Swim", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">Lap Swim</h2>
    <p>Lanes are dedicated to lap swimming in the Competition Pool and the Dive &amp; Rec Pool year-round, under lifeguard
      supervision at all times. One or two swimmers may split a lane; three or more circle swim, counter-clockwise. If you are the
      third swimmer entering a lane, make sure the other two know before you start.</p>
    <p>Lanes are first-come, first-served. No reservations.</p>
    <details class="acc" open><summary>RBAC Lap Swim Overview</summary><div>
      <ul><li>Locker rooms are available for personal belongings; bring your own lock.</li>
        <li>Aqua walking is allowed in the shallow end of the Dive &amp; Rec Pool.</li>
        <li>The minimum age for lap swim is 8. Lap swimmers must be able to swim the whole length of the lane and may be asked to take a
          swim test. Swimmers under 14 need adult supervision.</li>
        <li>RBAC does not currently offer annual passes.</li></ul></div></details>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Pricing and Pass Information</h3>{out("https://anc.apm.activecommunities.com/rosebowlaquatics/activity/search?onlineSiteId=0&from_original_cui=true&ActivityCategoryID=23", "Register Now")}</div>
    <div class="c-cyan"><h3>Passes</h3>
      {out("https://anc.apm.activecommunities.com/rosebowlaquatics/membership/search?onlineSiteId=0&keyword=adult", "Adult")}<br>
      {out("https://anc.apm.activecommunities.com/rosebowlaquatics/membership/search?onlineSiteId=0&keyword=senior", "Senior")}<br>
      {out("https://anc.apm.activecommunities.com/rosebowlaquatics/membership/search?onlineSiteId=0&keyword=youth", "Youth")}</div>
  </div>
</div></section>

<section class="band tint" id="now"><div class="wrap">
  <h2 class="sec-title">Lap lanes right now {LIVE}</h2>
  <p class="lede">Both pools, counted from the lanes each booking holds. Pick another day to plan ahead.</p>
  <div id="finder" class="finder" data-view="{WEEK}" data-kind="lap"></div>
  {ALERTS}
</div></section>

<section class="band" id="hours"><div class="wrap">
  <h2 class="sec-title">Lap swim hours by day {LIVE}</h2>
  <p class="small muted">Each weekday's usual lap swim hours over the published season, computed from the schedule. Holidays and
    early closings are left out of the usual hours and listed under each pool.</p>
  <div class="hours-grid">
    <div class="hbox"><h3>Competition Pool</h3><div {live("hours", "comp", group=LAP, whole=0, format="dl")}>…</div>
      <h4>Fewer than all the lanes</h4><div class="limited" {live("limited", "comp", group=LAP, empty="Every lane, all lap swim hours.")}>…</div>
      <h4>Changed days ahead</h4><div class="adjusted" {live("exceptions", "comp", group=LAP)}><p class="small muted">None in the published schedule.</p></div></div>
    <div class="hbox rec"><h3>Dive &amp; Rec Pool</h3><div {live("hours", "rec", group=LAP, whole=0, format="dl")}>…</div>
      <h4>How many lanes</h4><div class="limited" {live("limited", "rec", group=LAP, compact=1, empty="Every lane, all lap swim hours.")}>…</div>
      <p class="small muted" style="margin:4px 0 0">Lap lanes here change through the day around lessons, classes and diving. The
        <a href="#now">board above</a> and the <a href="#dive">lane calendar</a> show each stretch.</p>
      <h4>Changed days ahead</h4><div class="adjusted" {live("exceptions", "rec", group=LAP)}><p class="small muted">None in the published schedule.</p></div></div>
  </div>
  {quote("Please note lap swimming lane availability varies daily, based upon scheduled programming and events. During peak times, generally 3 – 9 pm Monday – Friday, lap swim lane availability is limited.", RB + "/lap-swim", "the Lap Swim page")}
  <p class="small">Above, “fewer than all the lanes” lists those stretches exactly, weekday by weekday, from the same bookings.</p>
</div></section>

<section class="band tint" id="comp"><div class="wrap">
  <h4 class="red">Competition Pool</h4>
  <p>Typically heated to 79 degrees. 50 meters, set as 8 long-course lanes or 20 short-course (25-yard) lanes. Which layout a
    session uses is on each booking, so the calendar draws the lanes that are actually up. Safe dive entry is allowed in all lanes.</p>
  {quote("The pool is set for short course except on Mondays, Wednesdays and Fridays.", RB + "/lap-swim", "the Lap Swim page")}
  <div class="today-board" data-view="{WEEK}" data-pool="comp"><p class="muted">Loading today…</p></div>
  <h3>Lane by lane {LIVE}</h3>
  <p class="small muted">Lap swim only, lane by lane: pick a day to see which lanes are open for laps. Lane numbers in this pool are
    Pool Relay's placement of the lane counts RBAC's calendar gives.</p>
  {frame(LAP_COMP, "Rose Bowl lap swim, Competition Pool", 900)}
</div></section>

<section class="band" id="dive"><div class="wrap">
  <h4 class="red">Dive &amp; Rec Pool</h4>
  <p>RBAC's site calls it the Recreational Pool or Dive/Rec Pool. Typically heated to 86 degrees, 20 lanes; shallow end 3'6", deep end
    17'. Safe dive entry is allowed in lanes 11–20.</p>
  <div class="today-board" data-view="{WEEK}" data-pool="rec"><p class="muted">Loading today…</p></div>
  <h3>Lane by lane {LIVE}</h3>
  <p class="small muted">Lap swim only, lane by lane.</p>
  {frame(LAP_DIVE, "Rose Bowl lap swim, Dive & Rec Pool", 900)}
</div></section>

<section class="band tint" id="faqs"><div class="wrap">
  <h2 class="sec-title">Swimming Etiquette</h2>
  <ul><li><b>Entering the water:</b> always feet first into shallow water.</li>
    <li><b>Resting:</b> while resting on the wall, stay aware of the swimmers around you.</li>
    <li><b>Sharing lanes:</b> please be courteous and responsive if a lifeguard asks you to move lanes.</li>
    <li><b>Coughing:</b> into your elbow, never into the gutters.</li></ul>
  <h2 class="sec-title">Pass Information</h2>
  <p>Buy a monthly or quarterly lap swim pass online or in person, or a day-use pass in person. The therapy pool and water fitness
    classes need separate passes. Youth passes are for 17 and under; senior passes for 55 and over.
    Financial assistance: {out(RB + "/scholarships", "rosebowlaquatics.org/scholarships")}.</p>
  <div class="tblwrap"><table class="fees"><thead><tr><th></th><th>Adult</th><th>Youth/Senior</th></tr></thead><tbody>
    <tr><th>Daily</th><td>$22</td><td>$19</td></tr><tr><th>Weekly</th><td>$52</td><td>$42</td></tr>
    <tr><th>Monthly</th><td>$100</td><td>$79</td></tr><tr><th>Quarterly</th><td>$280</td><td>$213</td></tr>
    <tr><th>Semi-annual</th><td colspan="2" style="text-align:center">not currently offered</td></tr></tbody></table></div>
  <div class="faqhead"><h3>FAQs</h3></div>
  <div class="faq">
    <details class="acc"><summary>Can I shower at the Center?</summary><div>Please shower before you swim. Deck showers are for a pre-swim rinse; the locker rooms and family changing room have showers for after.</div></details>
    <details class="acc"><summary>Where do I put my stuff?</summary><div>Lockers are available for daily use. RBAC recommends bringing only swim equipment onto the deck.</div></details>
    <details class="acc"><summary>Can I use the spas?</summary><div>Yes, up to 8 people at a time. Children under 8 need adult supervision. Please limit your time to 15 minutes.</div></details>
    <details class="acc"><summary>What is the minimum age for lap swimming?</summary><div>8 years old. Lap swimmers must be able to swim the whole length of the lane and may be asked to take a swim test. Under 14 needs adult supervision.</div></details>
    <details class="acc"><summary>Can I swim laps in the Therapy Pool?</summary><div>No. The Therapy Pool needs a separate pass.</div></details>
  </div>
</div></section>
""", [("overview", "Overview"), ("now", "Lap lanes right now"), ("hours", "Lap swim hours"), ("comp", "Comp Pool Calendar"),
      ("dive", "Dive & Rec Pool Calendar"), ("faqs", "FAQs")])

# ── Family Recreational Swim ─────────────────────────────────────────────────
REC = "Family Recreational Swim"
page("rec-swim.html", "Family Recreational Swim", "Family Recreational Swim", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">How Family Recreational Swim Works</h2>
    <p>The Family Recreational Swim line forms outside the front doors. Capacity is strict, so waiting in line doesn't guarantee a spot.</p>
    <ul><li>Wristbands go on sale 15 minutes before each session. Your whole party must be there when sales begin.</li>
      <li>Everyone in Family Rec Swim buys a wristband. Once capacity is reached, no more are sold.</li>
      <li>Each child under 8 must be with an adult in the water (two children under 8 means two adults in the water).</li>
      <li>Rec swim is in the shallow end of the Dive &amp; Rec Pool. Lifeguards go over the pool rules at the start of each session and
        let you know when it's over.</li></ul>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Pricing</h3><p class="price">$2</p><p>Adults (18 and over), per session</p>
      <p class="price">$1</p><p>Children (17 and under), per session</p></div>
    <div class="c-cyan"><h3>Questions?</h3>{out("mailto:customerservice@rosebowlaquatics.org", "Contact us")}</div>
  </div>
</div></section>

<section class="band tint" id="schedule"><div class="wrap">
  <h2 class="sec-title">Schedule {LIVE}</h2>
  <p class="lede">Every session, from the pool's live schedule. First-come, first-served; arriving early is a good idea.</p>
  <div class="hours-grid">
    <div class="hbox rec"><h3>Family Rec Swim sessions</h3><p style="margin:0;font-size:17px" {live("when", "rec", group=REC, gap=-1)}>…</p>
      <h4>Changed days ahead</h4><div class="adjusted" {live("exceptions", "rec", group=REC)}><p class="small muted">None in the published schedule.</p></div></div>
    <div>{quote("Monday through Friday: Session 1: 12:00 pm – 12:55 pm except Fridays. Session 2: 1:00 pm – 1:55 pm. Session 3: 7:35 pm – 8:35 pm. Saturday & Sunday: Session 1: 2:20 pm - 3:30 pm. Session 2: 3:35 pm - 4:45 pm.", RB + "/rec-swim", "the Family Recreational Swim page")}
      <p class="small">On RBAC's site these times are typed into the page, apart from the pool calendar. The list at left is the rec swim
        bookings on the pool calendar itself, so when the calendar changes, so does this page.</p></div>
  </div>
  <h3>This week {LIVE}</h3>
  <div id="week" data-view="{WEEK}" data-pool="ctr" data-pools="Dive &amp; Rec Pool" data-kind="rec"><p class="muted">Loading the week…</p></div>
  {ALERTS}
</div></section>

<section class="band" id="calendar"><div class="wrap">
  <h2 class="sec-title">On the calendar {LIVE}</h2>
  <p class="small muted">Family Recreational Swim only. <b>Subscribe</b> in the filter row to get an email when its sessions change.</p>
  {frame(REC_TAB, "Rose Bowl Family Recreational Swim", 860)}
</div></section>

<section class="band tint" id="rules"><div class="wrap">
  <h2 class="sec-title">Pool Rules</h2>
  <ul><li>Each child under 8 must be with an adult in the water.</li><li>Lifeguards have the final authority on the pool deck; swim only while they're on duty.</li>
    <li>Standard swimsuits only, no street clothes. Footwear to and from the pool is recommended.</li>
    <li>No gum, alcohol, smoking or glass in the water or on deck.</li><li>No diving or jumping, no running on deck, no rough play.</li>
    <li>No flotation devices or play equipment except in supervised lessons. No hanging on lane lines.</li>
    <li>Adults or guardians must be present to buy for and supervise minors (17 and under) at all times.</li></ul>
</div></section>
""", [("overview", "Overview"), ("schedule", "Schedule"), ("calendar", "Calendar"), ("rules", "Pool Rules")])

# ── Water Fitness & Wellness ─────────────────────────────────────────────────
WF = "Water Fitness & Wellness"
CLASSES = [  # title in the schedule, short description (paraphrased from RBAC's class pages)
    ("Sr. Splash", "Fun, lower-impact exercise for joint range of motion, balance and cardio. Senior Splash passes are valid for Senior Splash classes only."),
    ("Sr. Water Fitness", ""),
    ("Arthritis and MS Splash", "Gentle exercise in deep water following Arthritis Foundation guidelines; the cooler water helps with MS."),
    ("Deep Water", "Deep-water conditioning with flotation, no impact on the joints."),
    ("Deep Strong Burn", ""),
    ("Movin' Water", "High-energy cardio and core work, including aqua jogging and running."),
    ("Aqua HIIT", "High-intensity intervals for cardio and strength."),
    ("Aqua Zumba", "Water-adapted Zumba dance moves, cardio with less impact."),
    ("Aqua Fusion", ""),
    ("Aqua Super Setting", ""),
    ("Classic Shallow Water Fitness", "Multi-level classic aqua aerobics: cardio, strength and flexibility."),
    ("Shallow Move and Groove", "Fitness and dance with aqua fitness and Pilates techniques, for all levels."),
    ("Strong Water Burn", "Plyometric and isometric moves to burn calories and tone."),
    ("Finning Fitness", ""),
    ("Water Walking", ""),
]
rows = "".join(f'<tr><th>{E(t)}{f"<small>{E(d)}</small>" if d else ""}</th><td class="when" {live("when", "rec", title=t, gap=-1)}>…</td></tr>'
               for t, d in CLASSES)
page("water-fitness.html", "Water Fitness & Wellness", "Water Fitness Programs", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">Jump Right In – The Water is Great!</h2>
    <p>Water fitness classes take place in the Dive &amp; Rec Pool (86 degrees) and the Therapy Pool (91 degrees). Water is low impact on
      weight-bearing joints, increases circulation and strengthens muscles in every direction of movement, so classes suit beginners,
      weekend warriors and athletes alike.</p>
    <p>All water fitness passes except drop-in include unlimited lap swimming; a drop-in includes lap swimming that day. You don't need
      to know how to swim, but you must be comfortable in the water (tell your instructor if you can't swim). Participants must be able
      to perform skills independently and be ambulatory, with or without an assistive device.</p>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Register</h3><p>Water fitness registration is through Mindbody.</p>{out("https://clients.mindbodyonline.com/ASP/su1.asp?studioid=7398", "Mindbody Registration")}</div>
    <div class="c-cyan"><h3>Fees</h3>{out(RB + "/files/galleries/WF_Wellness_Options_Prices-Sept_2026_UPDATED.pdf", "Pricing Options (PDF)")}<br>
      {out(RB + "/Financial-Assistance", "Financial Assistance Program")}</div>
  </div>
</div></section>

<section class="band tint" id="classes"><div class="wrap">
  <h2 class="sec-title">Dive &amp; Rec Pool classes {LIVE}</h2>
  <p class="lede">Each class's usual times, read from the pool schedule. Class times, prices and instructors are subject to change; when
    they change, this table changes with them.</p>
  <div class="tblwrap"><table class="prog">{rows}</table></div>
  <div class="adjusted" {live("exceptions", "rec", group=WF)} hidden></div>
  <p class="small muted">Therapy Pool classes are on RBAC's {out(RB + "/therapy-pool-classes", "Therapy Pool Classes")} page; the Therapy Pool
    isn't part of this preview.</p>
  <div class="whatsnew"><b class="k">Why this table can't go stale</b>RBAC's class pages type each class's days and times by hand, separate
    from the pool calendar. Here there is one source: the class booked in the pool <i>is</i> the time printed.</div>
</div></section>

<section class="band" id="week-sec"><div class="wrap">
  <h2 class="sec-title">This week {LIVE}</h2>
  <div id="week" data-view="{WEEK}" data-pool="ctr" data-pools="Dive &amp; Rec Pool" data-kind="fit"><p class="muted">Loading the week…</p></div>
  {ALERTS}
  <h3>On the calendar</h3>
  <p class="small muted">Water fitness classes only. <b>Subscribe</b> in the filter row for an email when a class time changes.</p>
  {frame(FIT, "Rose Bowl Water Fitness & Wellness", 860)}
</div></section>

<section class="band tint" id="faqs"><div class="wrap">
  <div class="faqhead"><h3>FAQs</h3></div>
  <div class="faq">
    <details class="acc"><summary>How do I register for a class session?</summary><div>You need an account, made online or by phone. Register online or call (626) 564-0330 ext. 601. Your spot is reserved once payment is made in full (all major credit cards, cash and checks).</div></details>
    <details class="acc"><summary>Does the Center offer credits or refunds?</summary><div>With a doctor's note on letterhead, credits are offered if you can't finish the session. There is a no-refund policy.</div></details>
    <details class="acc"><summary>The class I wanted is full. Can I be waitlisted?</summary><div>Yes, but someone has to un-enroll from that class for a spot to open, which is occasional. Check with the office.</div></details>
    <details class="acc"><summary>How warm and deep is the Dive &amp; Rec Pool?</summary><div>86 degrees. Shallow area 3'6", deepest 17'. 50 meters by 25 yards.</div></details>
    <details class="acc"><summary>What should I bring?</summary><div>Swim attire, towel, sandals (the deck gets hot), hat, cover-up, and sunscreen applied 30 minutes before class.</div></details>
  </div>
</div></section>
""", [("overview", "Overview"), ("classes", "Rec Pool Classes"), ("week-sec", "This week"), ("faqs", "FAQs")])

# ── Swim Lessons ─────────────────────────────────────────────────────────────
LESSONS = [("Group swim lessons", "Swim Lessons", "Swim Lessons", "Parent/infant through school age"),
           ("Junior adult lessons", "Swim Lessons", "Jr. Adult Swim Lessons", "Ages 13–17"),
           ("Adult lessons", "Swim Lessons", "Adult Swim Lessons", "18 and up"),
           ("Private lessons", "Swim Lessons", "Private Lessons", "One-on-one"),
           ("Adaptive swim lessons", "Adaptive Swim Lessons", None, f'See {out(RB + "/adaptive-swim-lessons", "Adaptive Swim Lessons")}')]
lrows = "".join(f'<tr><th>{E(l)}<small>{d}</small></th><td class="when" {live("when", "rec", group=g, **({"title": t} if t else {}))}>…</td></tr>'
                for l, g, t, d in LESSONS)
LEVELS = [("Parent Infant", "6–18 months", "12:1", "Rubber Ducky, Baby Beluga"),
          ("Parent Preschool", "18 months – 3 years", "12:1", "Sea Otters"),
          ("Preschool", "3–6 years", "5:1", "Starfish, Seahorse, Clownfish, Penguin, Spotted Seal, Dolphin, Hammerhead Shark"),
          ("School Age", "6–12 years", "6:1", "Turtle, Octopus, Manta Ray, Polar Bear, Crocodile, Killer Whale, Great White Shark"),
          ("Junior Adult", "13–17 years", "10:1", ""), ("Adult", "18 and up", "10:1", "")]
levrows = "".join(f"<tr><th>{E(a)}</th><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td></tr>" for a, b, c, d in LEVELS)
page("swim-lessons.html", "Swim Lessons", "Swim Lessons", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">Group Swim Lessons</h2>
    <p>Swimming lessons are a chance to learn to swim in a safe, controlled setting with trained professionals. Learning to swim reduces
      the risk of drowning and is a life skill everyone should have. RBAC's mission is to make sure every person is water safe:
      quality swim lessons save lives.</p>
    <p>Classes are grouped first by age, then by skill, matched to each age's development while staying challenging enough to move
      swimmers up a level.</p>
    <p>To register or ask questions, call Swim Lessons Customer Service at <a href="tel:6265640330">(626) 564-0330</a> ext. 601.</p>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Group Swim Lessons</h3>{out("https://anc.apm.activecommunities.com/rosebowlaquatics/activity/search?onlineSiteId=0&from_original_cui=true&ActivityCategoryID=23", "Register Now")}</div>
    <div class="c-cyan"><h3>Sessions</h3><p>Session dates and registration windows are in RBAC's own documents:</p>
      {out(RB + "/files/galleries/2026_Session_Calendar_BrochureWebsite-0001.pdf", "Session calendar (PDF)")}<br>
      {out(RB + "/files/galleries/Swim_Lessons_2026-rev2.pdf", "Swim lessons brochure (PDF)")}</div>
  </div>
</div></section>

<section class="band tint" id="times"><div class="wrap">
  <h2 class="sec-title">When lessons are in the water {LIVE}</h2>
  <p class="lede">The usual lesson blocks in the Dive &amp; Rec Pool, from the pool schedule. Your class time within a block comes with registration.</p>
  <div class="tblwrap"><table class="prog">{lrows}</table></div>
  <div class="adjusted" {live("exceptions", "rec", group="Swim Lessons")} hidden></div>
  {ALERTS}
</div></section>

<section class="band" id="calendar"><div class="wrap">
  <h2 class="sec-title">On the calendar {LIVE}</h2>
  <p class="small muted">Swim lessons only. <b>Subscribe</b> in the filter row for an email when a lesson block changes.</p>
  {frame(LESSONS_TAB, "Rose Bowl Swim Lessons", 860)}
</div></section>

<section class="band" id="levels"><div class="wrap">
  <h2 class="sec-title">Levels</h2>
  <div class="tblwrap"><table class="prog"><thead><tr><th>Program</th><th>Ages</th><th>Ratio</th><th>Levels</th></tr></thead><tbody>{levrows}</tbody></table></div>
  <p class="small muted">Entry requirements for each level are on {out(RB + "/swim-lessons-programs", "RBAC's Swim Lessons page")}.</p>
</div></section>
""", [("overview", "Overview"), ("times", "Lesson times"), ("calendar", "Calendar"), ("levels", "Levels")])

# ── Masters Swim Team ────────────────────────────────────────────────────────
M = "Masters Swim Team"
page("masters.html", "Masters Swim Team", "Masters Swim", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">Adult Team-based Training</h2>
    <p>The Rose Bowl Aquatics Center Masters Swim Team is a team-based adult training program, supervised by Coach Chad Durieux. Swimmers
      range from novice competitors to former Olympians, grouped by ability in their lanes. Some train for specific events; most train
      for health and fitness. The atmosphere is a mix of dedication and fun.</p>
    <p>Workouts are typically an hour long. The team trains for three seasons a year and helps swimmers prepare for open water,
      triathlons and other water sports. Please contact the coach before dropping in.</p>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Fees</h3><p>Drop in <b>$22</b></p><p>Monthly pass <b>$135</b></p><p>Quarterly <b>$375</b></p></div>
    <div class="c-cyan"><h3>Membership Inquiry</h3>{out(RB + "/masters", "Contact the coach")}<br>{out("https://rosebowlmasters.theswimguy.com/", "Club gear")}</div>
  </div>
</div></section>

<section class="band tint" id="workouts"><div class="wrap">
  <h2 class="sec-title">Workout Schedule {LIVE}</h2>
  <div class="hours-grid">
    <div class="hbox"><h3>Competition Pool workouts</h3><p style="margin:0;font-size:17px" {live("when", "comp", group=M, gap=-1)}>…</p>
      <h4>Lanes the team holds</h4><div class="limited" {live("limited", "comp", group=M, empty="The whole pool.")}>…</div>
      <h4>Changed days ahead</h4><div class="adjusted" {live("exceptions", "comp", group=M)}><p class="small muted">None in the published schedule.</p></div></div>
    <div>{quote("Rose Bowl Aquatics Center Masters Swimming offers fifteen workouts in an average week. Workouts are typically 1 hour long.", RB + "/masters", "the Masters Swim Team page")}
      <p class="small">RBAC's Masters page types out its workout table by hand. Here the workouts are read from the same bookings that hold
        the team's lanes, so lap swimmers see the same lanes come off their board at the same moment.</p>
      <p class="small">Some workouts are at Occidental College; those aren't on RBAC's pool calendar, so they aren't here.
        See {out(RB + "/masters", "RBAC's Masters page")}.</p></div>
  </div>
  <h3>Lane by lane {LIVE}</h3>
  <p class="small muted">Masters workouts only, lane by lane. Lane numbers are Pool Relay's placement of the lane counts on RBAC's calendar.
    <b>Subscribe</b> in the filter row for an email when a workout changes.</p>
  {frame(MASTERS, "Rose Bowl Masters", 900)}
</div></section>

<section class="band" id="collegiate"><div class="wrap">
  <h2 class="sec-title">Collegiate Swimmers Incentive</h2>
  <p>College swimmers who train with the team on their breaks get 25% off monthly and quarterly passes, access to team discounts and
    sponsors, and prorated entry and exit around their school schedule. Short breaks (up to 6 days) are free for USMS-registered swimmers
    who swim with the team in the current year. To qualify: USMS registration, proof of full-time student status (or a current
    post-graduate program), and the Head Coach's approval.</p>
</div></section>
""", [("overview", "Overview"), ("workouts", "Workout Schedule"), ("collegiate", "Collegiate Incentive")])

# ── Team pages ───────────────────────────────────────────────────────────────
# Each team's practice times are read live from its training groups in Pool Relay, which were entered from the team's
# own schedule site (named on each page). Nothing about when a group practices is typed here.
ORG = "Rose Bowl Aquatics"


def grp_rows(team, pool, rows):
    """rows: (label, group under the team, note). One live 'when' cell per training group."""
    return "".join(f'<tr><th>{E(l)}{f"<small>{E(n)}</small>" if n else ""}</th><td class="when" '
                   f'{live("when", pool, group=f"{ORG} / {team} / {g}")}>…</td></tr>' for l, g, n in rows)


def team_site(href, label, what):
    return f'<div class="c-cyan"><h3>Team website</h3><p>{what}</p>{out(href, label)}</div>'


# ── Swim Team ────────────────────────────────────────────────────────────────
GO = "https://www.gomotionapp.com/team/rose/page"
SWIM_GROUPS = [
    ("National", "National", "Senior Division · high school · Futures qualifying time"),
    ("Senior 3", "Senior 3", "Senior Division · high school · two Sectional times"),
    ("Senior 2", "Senior 2", "Senior Division · high school · Summer Age Group qualifier"),
    ("Senior 1", "Senior 1", "Senior Division · high school"),
    ("13-14 Gold", "13-14 Gold", "Spring Age Group Championships qualifier"),
    ("13-14 Silver", "13-14 Silver", ""), ("13-14 Bronze", "13-14 Bronze", ""), ("13 & Over Red", "13 & Over Red", ""),
    ("11-12 Gold", "11-12 Gold", ""), ("11-12 Silver", "11-12 Silver", ""), ("11-12 Bronze", "11-12 Bronze", ""),
    ("11-12 Red", "11-12 Red", ""),
    ("10 & Under Gold", "10 & Under Gold", ""), ("10 & Under Silver", "10 & Under Silver", ""),
    ("10 & Under Bronze", "10 & Under Bronze", ""), ("10 & Under Red", "10 & Under Red", ""),
]
ST = "Swim Team"
page("swim-team.html", "Swim Team", "Swim Team", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">Swim Teams</h2>
    <p>Rose Bowl Aquatics is a nationally renowned swim team. Success at the highest level of competition comes from respect, hard
      work, discipline and dedication, and the team focuses on developing the whole student-athlete in a safe, supportive team
      environment, in and out of the pool.</p>
    <p><b>Rose Buds</b> is the pre-competitive team: an introduction to practices, team culture and competition for swimmers 6 to 17 who
      can swim freestyle and backstroke and have been introduced to butterfly and breaststroke. The <b>competitive team</b> is for
      swimmers 6 and older who swim all four strokes legally with proper turns and dives. Swimmers new to competition start with a
      tryout of about ten minutes; coaches then suggest a group and review progress at the end of each month.</p>
    <details class="acc"><summary>Core values</summary><div><ul><li>Fun</li><li>Team</li><li>Accountability</li><li>Train for Life</li><li>Humble Success</li></ul></div></details>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Register for Tryouts</h3>{out("https://anc.apm.activecommunities.com/rosebowlaquatics/activity/search?onlineSiteId=0&activity_select_param=2&activity_category_ids=15&viewMode=list", "Register")}</div>
    {team_site(GO + "/home", "gomotionapp.com/team/rose", "Training schedule, meet schedule, group descriptions and team registration, on the team's own SportsEngine Motion site.")}
  </div>
</div></section>

<section class="band tint" id="practice"><div class="wrap">
  <h2 class="sec-title">Practice times by training group {LIVE}</h2>
  <p class="lede">Each group's usual swims in the Competition Pool, read from the pool schedule. Dryland is out of the water and isn't listed.</p>
  <div class="tblwrap"><table class="prog">{grp_rows(ST, "comp", SWIM_GROUPS)}</table></div>
  <h4>Changed days ahead</h4><div class="adjusted" {live("exceptions", "comp", group=f"{ORG} / {ST}")}><p class="small muted">None in the published schedule.</p></div>
  <h4>Home meets at RBAC {LIVE}</h4><p {live("dates", "comp", group=f"{ORG} / {ST}", title="Block Party Intrasquad|Rose IMX Meet", empty="None on the pool schedule in the coming months.")}>…</p>
  <div class="whatsnew"><b class="k">Where these times come from</b>The team publishes its practice schedule as a PDF on
    {out(GO + "/newsletter/2023-training-schedule-", "its training schedule page")}. Pool Relay holds each group's swims inside the
    water RBAC's pool calendar gives the Swim Team, so the pool, the team and lap swimmers read the same lanes. Where the team's
    sheet starts a swim before the pool calendar gives the team the water, this page shows the pool calendar's time. How many lanes
    each group gets is Pool Relay's estimate; the team's schedule doesn't say.</div>
  {ALERTS}
</div></section>

<section class="band" id="calendar"><div class="wrap">
  <h2 class="sec-title">Lane by lane {LIVE}</h2>
  <p class="small muted">Swim Team groups only, lane by lane. Pick a day; use the filter row to show one group, and <b>Subscribe</b> for an
    email when that group's practices change.</p>
  {frame(SWIM_TAB, "Rose Bowl Swim Team", 900)}
</div></section>

<section class="band tint" id="groups"><div class="wrap">
  <h2 class="sec-title">Group Requirements and Descriptions</h2>
  <p>Groups run by age and ability across four divisions (Senior, 13-14, 11-12 and 10 &amp; Under), each with Gold, Silver, Bronze
    and Red levels below the senior groups. Placement is at the coaches' discretion. The full requirements for each group are in the
    team's {out(GO + "/newsletter/2023-group-descriptions", "group descriptions")}.</p>
  <details class="acc"><summary>Rose Buds levels</summary><div><ul>
    <li><b>Rose 1:</b> swims 25 yards without stopping; water safety, kicking all four strokes, side breathing, body position.</li>
    <li><b>Rose 2:</b> 25 yards of freestyle and of backstroke; all four strokes taught through drills.</li>
    <li><b>Rose 3:</b> legal stroke and IM turns, and dives using the USA Swimming dive progression.</li></ul></div></details>
  <h2 class="sec-title" style="margin-top:28px">Swim Team Fees</h2>
  <p>All registration fees and season rates are paid in full before a swimmer enters the water. Competitive team: a monthly membership
    fee to RBAC, a semi-annual family commitment to the Booster Club, and annual USA Swimming registration. Rose Buds pricing is by
    group, with an eight-week fee.</p>
  <div class="tblwrap"><table class="fees"><tbody>
    <tr><th>Sports Engine Motion</th><td>$60</td></tr>
    <tr><th>USA Swimming Flex membership (12 &amp; under)</th><td>$30 a year</td></tr>
    <tr><th>USA Swimming Premium membership (6 and up)</th><td>$80 a year</td></tr></tbody></table></div>
  <p class="small">Financial assistance: {out(RB + "/scholarships", "rosebowlaquatics.org/scholarships")}.</p>
</div></section>

<section class="band" id="coaches"><div class="wrap">
  <h2 class="sec-title">Coaches</h2>
  <p>Head Coach Andrew Nguyen, with Scott Player, Matt Cervantes, Katherine Fisher, Katherine Tse, Jordan Morillo, Jeanette MacDougall
    (Rose Buds), Hector Jimenez, David Jimenez, Cameron Ware, Michael Wong and Alex Moothart.</p>
  <p class="small">Questions: {out("mailto:anguyen@rosebowlaquatics.org", "contact the head coach")} · Rose Buds:
    {out("mailto:jmacdougall@rosebowlaquatics.org", "email the Rose Buds team")} · Booster Club and policies:
    {out(GO + "/documents", "team documents")}</p>
</div></section>
""", [("overview", "Overview"), ("practice", "Practice times"), ("calendar", "Calendar"), ("groups", "Groups & fees"),
      ("coaches", "Coaches")])

# ── Water Polo Team ──────────────────────────────────────────────────────────
WPT = "Water Polo Team"
WP_SHEET = "https://docs.google.com/spreadsheets/d/17UqEF5NKlFPGQZvh8AkeMXMXa3-FcM4oiXRn0fkIOaw/edit?usp=sharing"
WP_SITE = "https://rosebowlwaterpolo.com/"
WP_PRE = [("Splashball", "Splash Ball", "Ages 4–8 · shallow end of the Dive & Rec Pool"),
          ("Intro to Water Polo 1 & 2", "Intro 1", "Ages 8–13 · dive well of the Dive & Rec Pool"),
          ("Gold Academy 1 & 2", "Gold Academy 1", "Ages 8–13 · after Intro, or by coach's recommendation")]
WP_TEAMS = [("10U Coed", "10U Coed", ""), ("12U Boys", "12U Boys", ""), ("12U Girls", "12U Girls", ""),
            ("14U Boys", "14U Boys", ""), ("14U Girls", "14U Girls", ""),
            ("HS Boys Group 1", "HS Boys Group 1", "Some practices are at La Cañada High School"),
            ("HS Boys Group 2", "HS Boys Group 2", "Some practices are at Occidental College")]
page("water-polo.html", "Water Polo Team", "Water Polo Team", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">Water Polo - All Ages &amp; Levels</h2>
    <p>Student-athletes at the RBAC are led by a coaching staff that includes current local high school, collegiate, zone team and
      National Team coaches. Athletes begin with Splashball and Intro to Water Polo, which build water safety, confidence and the key
      skills of the game. Gold Academy is the next step: endurance, strength, speed and water polo skills. After Gold Academy,
      athletes are invited to try out for the travel teams, fielded at 10 &amp; under, 12 &amp; under, 14 &amp; under, 16 &amp; under
      and 18 &amp; under.</p>
    <p>The program has placed over 100 players on U.S. National Team rosters, has medaled 14 times at national events and won six
      national championships. No prior experience is required.</p>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Ready to Sign Up</h3><p>New players attend a practice before registering.</p>{out("mailto:pbeemer@rosebowlaquatics.org", "Contact Coach Pat Beemer")}</div>
    {team_site(WP_SITE, "rosebowlwaterpolo.com", "Rose Bowl Water Polo Club's own site: teams, rosters, registration and news. Its practice schedule is the sheet linked from RBAC's page.")}
  </div>
</div></section>

<section class="band tint" id="practice"><div class="wrap">
  <h2 class="sec-title">Practice times {LIVE}</h2>
  <p class="lede">Each group's usual practices, read from the pool schedule: pre-teams in the Dive &amp; Rec Pool, competition teams in
    the Competition Pool.</p>
  <h3>Pre-teams</h3><div class="tblwrap"><table class="prog">{grp_rows(WPT, "ctr", WP_PRE)}</table></div>
  <h3>Competition teams</h3><div class="tblwrap"><table class="prog">{grp_rows(WPT, "ctr", WP_TEAMS)}</table></div>
  <h4>All water polo water on the pool calendar</h4><p {live("when", "ctr", group=f"{ORG} / {WPT}")}>…</p>
  <div class="whatsnew"><b class="k">Where these times come from</b>The club's practice schedule is a Google Sheet,
    {out(WP_SHEET, "linked from RBAC's Water Polo page")}; the team's own site, {out(WP_SITE, "rosebowlwaterpolo.com")}, doesn't list
    practices. Pool Relay holds each group inside the water RBAC's pool calendar gives water polo. The sheet covers the fall season, so
    group times end with it; after that the pool calendar's water polo blocks stand until the next season's sheet is entered. How many
    lanes each group gets is Pool Relay's estimate.</div>
  {quote("Coaches may make adjustments to their individual age group and practice group plans, make sure to ask your coach about any changes.", RB + "/water-polo", "the Water Polo page")}
  {ALERTS}
</div></section>

<section class="band" id="calendar"><div class="wrap">
  <h2 class="sec-title">This week {LIVE}</h2>
  <p class="small muted">Water polo only, both pools. Each block names its pool. Use the filter row to show one group, and <b>Subscribe</b>
    for an email when its practices change.</p>
  {frame(POLO_TAB, "Rose Bowl Water Polo", 860)}
</div></section>

<section class="band tint" id="programs"><div class="wrap">
  <h2 class="sec-title">Programs and Fees</h2>
  <div class="tblwrap"><table class="prog"><thead><tr><th>Program</th><th>Ages</th><th>Fee</th></tr></thead><tbody>
    <tr><th>Splashball<small>Coed, non-contact, in the shallow end</small></th><td>4–8</td><td>$250 a session (8 classes)</td></tr>
    <tr><th>Intro to Water Polo 1 &amp; 2<small>Deep water; four laps of head-down freestyle to start</small></th><td>8–13</td><td>$167 for 8 sessions</td></tr>
    <tr><th>Gold Academy 1 &amp; 2<small>Highest pre-competitive tier; coach assessment required</small></th><td>8–13</td><td>$410 a session (8 weeks)</td></tr>
    <tr><th>Competition teams<small>10U through 18U, boys and girls</small></th><td>8–18</td><td>Monthly, all-inclusive</td></tr></tbody></table></div>
  <p class="small">Competition team fees are paid monthly to RBAC and include tournament and league entry, except major events like the
    National Junior Olympics. Ages follow the USA Water Polo age cutoff. Pre-teams sign-up: Hannah Landswick,
    {out("mailto:hlandswick@rosebowlaquatics.org", "hlandswick@rosebowlaquatics.org")}. Financial assistance:
    {out(RB + "/scholarships", "rosebowlaquatics.org/scholarships")}.</p>
  <div class="faqhead"><h3>FAQs</h3></div>
  <div class="faq">
    <details class="acc"><summary>Do I have to know how to play before joining?</summary><div>No. Most athletes come with little or no experience and learn through Intro to Water Polo and Gold Academy.</div></details>
    <details class="acc"><summary>When can I sign up?</summary><div>Any time. Practices run year-round, and you're welcome to attend one before joining.</div></details>
    <details class="acc"><summary>Where are games played?</summary><div>Mostly between San Clemente, Riverside and Santa Barbara, occasionally San Diego. Junior Olympics alternate between Northern and Southern California.</div></details>
    <details class="acc"><summary>How do I register?</summary><div>Register with USA Water Polo, then with RBAC at the front desk (fees are paid monthly). Only fully registered players practice and play.</div></details>
  </div>
</div></section>
""", [("overview", "Overview"), ("practice", "Practice times"), ("calendar", "Calendar"), ("programs", "Programs & fees")])

# ── Dive Team ────────────────────────────────────────────────────────────────
DT = "Dive Team"
DV_SITE = "https://www.rosebowldiving.org/"
DV_GROUPS = [("National Team (Black)", "National Team", "Invitation only · 14 & over"),
             ("Jr National Team (Black)", "Jr National Team", "Invitation only · 13 & under"),
             ("Red Team", "Red Team", "High school · 14 & over"), ("Blue Team", "Blue Team", "Middle school · 11–14"),
             ("White Team", "White Team", "12 & under"), ("Green Team", "Green Team", "8 & under · invitation only"),
             ("Orange Team (Rising Stars)", "Orange Team", "13 & under · first step after lessons")]
page("dive-team.html", "Dive Team", "Dive Team", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">Ready to Dive In</h2>
    <p>The Rose Bowl Aquatics Center Dive Program offers year-round introductory, intermediate and advanced lessons, plus competitive
      Novice and Junior Olympic teams. The Rose Bowl Dive Team has ranked among the nation's top teams since the center opened, and most
      of its high school graduates continue to dive in college. For beginners, all you need is a swimsuit, basic swimming skills and a
      desire to have fun.</p>
    <p>Divers practice at the deep end (18 feet) of the Dive &amp; Rec Pool, on 1-meter and 3-meter springboards and the tower. The team's
      current age range is 8 to 17. Head Coach: Jean-Luc Miralda.</p>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Interested in Lessons</h3>{out("https://anc.apm.activecommunities.com/rosebowlaquatics/activity/search?onlineSiteId=0&activity_select_param=2&activity_category_ids=43&viewMode=list", "Lesson Sign-Up")}</div>
    {team_site(DV_SITE, "rosebowldiving.org", "Rose Bowl Diving's own site: team registration, dive groups, and the day-by-day practice schedule.")}
  </div>
</div></section>

<section class="band tint" id="practice"><div class="wrap">
  <h2 class="sec-title">Team practice times by group {LIVE}</h2>
  <p class="lede">Each group's usual practices in the dive well, read from the pool schedule.</p>
  <div class="tblwrap"><table class="prog">{grp_rows(DT, "rec", DV_GROUPS)}</table></div>
  <h4>All diving on the pool calendar</h4><p {live("when", "rec", group=f"{ORG} / {DT}")}>…</p>
  <h4>Changed days ahead</h4><div class="adjusted" {live("exceptions", "rec", group=f"{ORG} / {DT}")}><p class="small muted">None in the published schedule.</p></div>
  <div class="whatsnew"><b class="k">Where these times come from</b>Rose Bowl Diving publishes practices day by day on
    {out(DV_SITE + "schedule", "its schedule page")}. Pool Relay holds each group inside the dive-well water RBAC's pool calendar gives
    the Dive Team, so where the team's schedule runs later than the pool calendar, this page shows the pool calendar's time. Which
    lane of the dive well each group is drawn in is Pool Relay's estimate. Once the team's published schedule ends, the pool
    calendar's diving blocks stand until the next one is entered.</div>
  {quote("Training days are flexible and vary based on the team! Check our calendar for dates.", RB + "/dive-team", "the Dive Team page")}
  {ALERTS}
</div></section>

<section class="band" id="calendar"><div class="wrap">
  <h2 class="sec-title">The dive well, lane by lane {LIVE}</h2>
  <p class="small muted">Dive Team only. Pick a day; use the filter row to show one group, and <b>Subscribe</b> for an email when its
    practices change.</p>
  {frame(DIVE_TAB, "Rose Bowl Dive Team", 900)}
</div></section>

<section class="band tint" id="programs"><div class="wrap">
  <h2 class="sec-title">Programs and Training Groups</h2>
  <ul><li><b>Learn to Dive Day</b> (ages 6–12): a 1½-hour intro for anyone who can swim one lap comfortably in deep water. $35.</li>
    <li><b>Lessons Group</b> (13 &amp; under): no experience needed; mechanics, body control and confidence. $250 a month.</li>
    <li><b>Team groups</b>: $275–$475 a month depending on the team, plus $50 a year team registration and booster fees (Orange team and
      above). USA Diving membership is required.</li></ul>
  <p class="small">Off-site tower training is available on select weekends. The Breaking Barriers Dive Grant funds Learn to Dive Days,
    USA Diving memberships and meet fees for local athletes: {out(DV_SITE + "about/breaking-barriers-dive-grant/78697", "about the grant")}.</p>
  <div class="faqhead"><h3>FAQs</h3></div>
  <div class="faq">
    <details class="acc"><summary>Is there a minimum age?</summary><div>No, but divers need basic swim skills: they practice in 18 feet of water and must surface and return to the deck on their own.</div></details>
    <details class="acc"><summary>What's the difference between beginner, novice and J.O.?</summary><div>A beginner is learning basic skills. A novice has enough skills to join the team and compete locally. A Junior Olympic diver has moved beyond novice and competes regionally and nationally.</div></details>
    <details class="acc"><summary>Are you closed in winter?</summary><div>No. Programs run year-round in heated pools, with two hot tubs by the boards.</div></details>
    <details class="acc"><summary>How do I get in touch?</summary><div>Call the front desk at 626-564-0330 x404 or email {out("mailto:jmiralda@rosebowlaquatics.org", "the dive coach")}.</div></details>
  </div>
</div></section>
""", [("overview", "Overview"), ("practice", "Practice times"), ("calendar", "Calendar"), ("programs", "Programs & FAQs")])

# ── Rays Swim Team ───────────────────────────────────────────────────────────
RT = "Rays Swim Team"
page("rays.html", "Rays Swim Team", "Rays Swim Team", f"""
<section class="band" id="overview"><div class="wrap two">
  <div><h2 class="sec-title">The Rays Swim Team</h2>
    <p>The Rays Swim Team gives swimmers with special needs the opportunity to learn a sport and be part of a team. The skills,
      self-confidence and empowerment gained in sports carry into daily life, helping athletes become healthier, happier and more
      productive students and individuals.</p>
    <p>Practices are structured so each swimmer trains with peers by age and ability, and each practice day swimmers choose a 30- or
      60-minute session within the team's practice time. The Rays compete in intra-squad meets through the year, and a parent volunteer
      group plans social activities. All ages are welcome to try out.</p>
  </div>
  <div class="cardstack">
    <div class="c-red"><h3>Fees</h3><p class="price">$87</p><p>per month</p>{out("https://anc.apm.activecommunities.com/rosebowlaquatics/membership/search?onlineSiteId=0&from_original_cui=true&keyword=", "Register")}</div>
    <div class="c-cyan"><h3>Tryouts</h3><p>Email {out("mailto:rays@rosebowlaquatics.org", "rays@rosebowlaquatics.org")} or call (626) 564-0330 ext. 419.</p></div>
  </div>
</div></section>

<section class="band tint" id="practice"><div class="wrap">
  <h2 class="sec-title">Practice Information and Schedule {LIVE}</h2>
  <div class="hours-grid">
    <div class="hbox"><h3>Team practice time</h3><p style="margin:0;font-size:17px" {live("when", "ctr", group=f"{ORG} / {RT}", gap=-1)}>…</p>
      <h4>Changed days ahead</h4><div class="adjusted" {live("exceptions", "ctr", group=f"{ORG} / {RT}")}><p class="small muted">None in the published schedule.</p></div></div>
    <div>{quote("The Rays Swim Team has 3 practices per week and swimmers have an option for a 30 minute or 60 minute session each practice day during allocated practice times.", RB + "/rays", "the Rays Swim Team page")}
      <p class="small">The Rays don't have a separate team website. RBAC's page types the practice times by hand; here they're read from
        the Rays' bookings on the pool calendar, which say which pool and how many lanes.</p></div>
  </div>
  {ALERTS}
</div></section>

<section class="band" id="calendar"><div class="wrap">
  <h2 class="sec-title">This week {LIVE}</h2>
  <p class="small muted">Rays only, both pools; each block names its pool. <b>Subscribe</b> in the filter row for an email when a practice changes.</p>
  {frame(RAYS_TAB, "Rose Bowl Rays Swim Team", 760)}
</div></section>

<section class="band tint" id="coaches"><div class="wrap">
  <h2 class="sec-title">Coaches</h2>
  <p>Cameron Lee, Cassie Morla and Amanda Tuttle. {out("mailto:clee@rosebowlaquatics.org", "Contact us")}.</p>
  <p class="small">Financial assistance: {out(RB + "/scholarships", "rosebowlaquatics.org/scholarships")}.</p>
</div></section>
""", [("overview", "Overview"), ("practice", "Practice times"), ("calendar", "Calendar"), ("coaches", "Coaches")])

# ── Calendars ────────────────────────────────────────────────────────────────
page("calendars.html", "Calendars", "Calendars", f"""
<section class="band" id="before"><div class="wrap">
  <h2 class="sec-title">One schedule instead of two lists</h2>
  <p class="lede">RBAC publishes each pool's schedule as a Google Calendar in agenda mode. Below are the same two pools on Pool Relay,
    drawn lane by lane, plus a week view of both.</p>
  <div class="before-after">
    <div class="b"><h3>Before: two agenda lists</h3>
      <p class="small">Entries as they appear on RBAC's calendars (titles only):</p>
      <div class="agenda" aria-label="Example agenda entries">
        <div><i></i><span>General Lap Swim - 10 lanes SC</span></div><div><i></i><span>Master's Team - 10 lanes SC</span></div>
        <div><i></i><span>Swim team- 10 lanes SC</span></div><div><i style="background:#6b3304"></i><span>Lap Swim - Lanes 11-13</span></div>
        <div><i style="background:#6b3304"></i><span>Private Lessons - Lane 10</span></div><div><i style="background:#6b3304"></i><span>Rec Swim - Lanes 1-3</span></div></div>
      <ul style="margin-top:10px"><li>To find an open lane, read both lists and add up the lanes.</li>
        <li>Lap swim in one pool is often several entries at once on different lanes.</li>
        <li>The same practice sometimes appears twice, under different spellings, and both copies have to be updated.</li></ul></div>
    <div class="a"><h3>After: one live schedule</h3><ul>
      <li>Each pool drawn lane by lane, so open water is visible at a glance.</li>
      <li>A <a href="index.html#now">swim-now board</a> counting the lap lanes open right now in each pool.</li>
      <li><a href="lap-swim.html#hours">Lap swim hours by day</a>, computed from the bookings rather than typed.</li>
      <li>Closures and early closings show up on their own, and clear those hours everywhere.</li>
      <li>Each program page lists only its own times; the filter row's <b>Subscribe</b> sends change emails for one program.</li>
      <li>Every entry is kept once. Putting both calendars into one schedule merged repeated entries, so a change is made in one place.</li></ul></div>
  </div>
  {ALERTS}
</div></section>

<section class="band tint" id="comp"><div class="wrap">
  <h2 class="sec-title">Competition Pool, lane by lane {LIVE}</h2>
  <p class="small muted">Short course (20 lanes) by default; sessions on the long-course layout (8 lanes) show on that layout. Lane numbers
    are Pool Relay's placement of the lane counts RBAC's calendar gives.</p>
  {frame(COMP, "Rose Bowl Competition Pool, lane by lane", 900)}
</div></section>

<section class="band" id="dive"><div class="wrap">
  <h2 class="sec-title">Dive &amp; Rec Pool, lane by lane {LIVE}</h2>
  {frame(DIVE, "Rose Bowl Dive & Rec Pool, lane by lane", 900)}
</div></section>

<section class="band tint" id="week-cal"><div class="wrap">
  <h2 class="sec-title">Both pools, by week {LIVE}</h2>
  <p class="small muted">Each block names its pool. Filter by program and subscribe from the filter row.</p>
  {frame(WEEK, "Rose Bowl Aquatics Center, week", 900)}
  <p class="small">Independent Therapy Pool calendars stay on {out(RB + "/Therapy-Pool#faqs", "RBAC's Therapy Pool page")}.</p>
</div></section>
""", [("before", "Why one schedule"), ("comp", "Competition Pool"), ("dive", "Dive & Rec Pool"), ("week-cal", "Both pools, by week")])

print("built 11 pages, assets", VER)
