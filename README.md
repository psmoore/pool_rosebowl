# Rose Bowl Aquatics Center — unofficial preview

A mock-up of [rosebowlaquatics.org](https://rosebowlaquatics.org/) (Home, Lap Swim, Family Recreational Swim, Water Fitness &
Wellness, Swim Lessons, Swim Team, Water Polo Team, Dive Team, Rays Swim Team, Masters Swim Team, Calendars) in the look of RBAC's own site, with its schedules on live
[Pool Relay](https://www.poolrelay.com) calendars. Not operated by, endorsed by or affiliated with the Rose Bowl Aquatics Center.
No RBAC logo or photos are used: the wordmark is text and the "photos" are CSS gradients.

RBAC publishes its schedule as two Google Calendars in agenda mode (Competition Pool, Dive/Rec Pool), with entries like
"Lap Swim - Lanes 6-20" and "Master's Team - 10 lanes SC", and types program times by hand into the program pages. Here one
schedule feeds every page: each pool drawn lane by lane, a swim-now board counting the lap lanes open in each pool, lap swim
hours by day, closures and early closings, and each program's own times.

No schedule is typed into the pages. Hours, sessions, classes, practices, closures and changed days are filled by `finder.js`
from the live Pool Relay view; `build.py` holds only prices, ages, policies, descriptions, facts about the water, and quotes of
RBAC's schedule that are labeled as quotes. `check.py` fails if a time, weekday or date appears outside a script or a labeled quote.

- `build.py`: generates the eleven pages (`python3 build.py && python3 check.py`).
- `finder.js`: `#finder` (swim-now board, one card per pool), `.today-board` (one pool's day), `#week` (pool by pool), and
  `data-live` elements (`when`, `hours`, `limited`, `exceptions`, `alerts`). Overlapping bookings of one program on different lanes
  are cut by time and counted as one session. Timed notices on the whole center ("Closed for UCLA football", "Closes at 2pm") read
  as changed days; "Pool change (closed)" stays in the Competition Pool's day as a closed block.
- Pool Relay views: `FgHEbQHJyQ9xrnxBa1FmYt` (Competition Pool, lane by lane), `430wOk0AHmfQrpXaag7Hrs` (Dive & Rec Pool, lane by
  lane), `ldh1B3ldemNOlqrz69lAVa` (both pools, week; feeds every live element). These three are the all-program calendars,
  on Home and Calendars.
- Each program page embeds a tab locked to that program's group, so its calendar shows that program only:
  Lap Swim `lGMh1lF6ZPQkYH4AEKEwC9` (Competition Pool) and `NYCzecS1JPKyAfMrxcTKQs` (Dive & Rec Pool), Masters
  `tUrgh3T3PBSjosKGCD3y8v`, Family Recreational Swim `tLcJFojRzuyDeqaNfAeuKT`, Water Fitness & Wellness
  `YmdcazrCwslIbrYSMAHe3P`, Swim Lessons `3kW9Hqs7rgsmDukChClTRt`.
- Team pages embed a tab locked to that team's group: Swim Team `GJAqqJ9is2xRW6F8YVOHQL` (Competition Pool, lane by lane),
  Water Polo Team `iy9F70sZq6N9ZFdrSlPs1Q` (both pools, week), Dive Team `OlV4FkpT5I0GxYhbdMzMsJ` (Dive & Rec Pool, lane by lane),
  Rays Swim Team `i2vGOoejn4ZbCBMz9hblnn` (both pools, week). The Teams menu points at these pages.
- Each team's training groups were entered in Pool Relay from the team's own schedule, inside the water RBAC's pool calendar gives
  the team (draft "RBAC team training groups (from team sites)", read 2026-11-04): Swim Team from the 2026-2027 Training Schedule PDF
  on gomotionapp.com/team/rose (16 groups); Water Polo from the Fall 2026 practice sheet linked on RBAC's Water Polo page
  (rosebowlwaterpolo.com lists no practices; groups run to the sheet's end, then the pool calendar's blocks); Dive Team from
  rosebowldiving.org/schedule (7 groups, through the last published week). The Rays have no team site, so their page reads the
  pool calendar's Rays bookings. Lanes per group are Pool Relay's estimate, said in each booking's description.
