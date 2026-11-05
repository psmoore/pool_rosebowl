#!/usr/bin/env python3
"""Rule check: no schedule typed into the pages. Strips <script>, comments and labeled quotes (blockquote.quote), then flags
anything that looks like a time, weekday, month or date. Run after build.py; prints nothing but a summary when clean."""
import glob, re, sys
PAT = re.compile(r"\b(\d{1,2}(:\d\d)?\s*(am|pm|a\.m\.|p\.m\.)|\d{1,2}:\d\d|noon|midnight|"
                 r"mon(day)?s?|tue(s|sday)?s?|wed(nesday)?s?|thu(rs|rsday)?s?|fri(day)?s?|sat(urday)?s?|sun(day)?s?|nightly|"
                 r"(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|june?|july?|aug(ust)?|sept?(ember)?|oct(ober)?|nov(ember)?|dec(ember)?)\.?\s+\d{1,2}|"
                 r"\d{1,2}/\d{1,2}|"
                 r"20\d\d|thanksgiving|christmas|new year)\b", re.I)
bad = 0
for f in sorted(glob.glob("*.html")):
    s = open(f).read()
    s = re.sub(r"(?s)<script.*?</script>|<!--.*?-->|<blockquote class=\"quote\">.*?</blockquote>", " ", s)
    s = re.sub(r'(?s)<a [^>]*href="[^"]*"', "<a", s)  # URLs (file names like ..._2026.pdf) aren't text
    text = re.sub(r"<[^>]+>", " ", s)
    for m in PAT.finditer(text):
        ctx = text[max(0, m.start() - 50): m.end() + 40].replace("\n", " ")
        print(f"{f}: {m.group(0)!r}  …{ctx.strip()}…"); bad += 1
print(f"{bad} schedule-like matches outside scripts and labeled quotes")
sys.exit(1 if bad else 0)
