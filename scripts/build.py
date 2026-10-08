"""Build assets/hero.svg and assets/terminal.svg for the profile README.

Fonts are subset and embedded, so the SVGs render the same on every machine.
The terminal numbers come from the GitHub and npm APIs at build time.

Usage: pip install fonttools brotli && python scripts/build.py
"""

import base64
import datetime as dt
import io
import json
import os
import urllib.request
from html import escape
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
ASSETS = ROOT / "assets"

USER = "OmarNassar1127"
PACKAGES = ["skillsync-team", "claude-pin", "huurradar", "huischeck"]
EMAIL = "omarnassar1127@gmail.com"

INK, BODY, CANVAS, SIGNAL = "#0f0f0e", "#6b6964", "#f4f4f2", "#f2541a"


# ---------- fonts ----------

def load(name, axes=None):
    font = TTFont(FONTS / name, recalcTimestamp=False)
    if axes:
        font = instancer.instantiateVariableFont(font, axes)
    return font


def embed(font, text, family):
    """Subset `font` to `text` and return an @font-face rule with a woff2 data URI."""
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern"]
    opts.name_IDs = []
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{family}';src:url(data:font/woff2;base64,{data}) format('woff2')}}"


def advances(font, size):
    """Map char -> advance width in px at `size`."""
    cmap, hmtx, upm = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    return lambda ch: hmtx[cmap[ord(ch)]][0] * size / upm


# ---------- hero ----------

def build_hero():
    W, PAD = 900, 40
    name_font = load("MonaSans-latin-var.woff2", {"wght": 800, "wdth": 112})
    lede_font = load("MonaSans-latin-var.woff2", {"wght": 600, "wdth": 100})
    mono = load("GeistMono-Regular.woff2")

    # Size the name so "Omar [pill] Nassar" fills the card width exactly.
    track, gap, pill_w, pill_h = -0.055, 0.1, 1.28, 0.72
    adv1 = advances(name_font, 1)
    word_em = lambda w: sum(adv1(c) + track for c in w)
    total_em = word_em("Omar") + word_em("Nassar") + pill_w + 2 * gap
    size = (W - 2 * PAD) / total_em
    cap = name_font["OS/2"].sCapHeight / name_font["head"].unitsPerEm * size
    base = 292

    letters, x, i = [], PAD, 0
    for word in ("Omar", "Nassar"):
        for ch in word:
            delay = 0.05 + i * 0.045
            letters.append(f'<text class="l" x="{x:.1f}" y="{base}" style="animation-delay:{delay:.3f}s">{ch}</text>')
            x += (adv1(ch) + track) * size
            i += 1
        if word == "Omar":
            x += gap * size
            pill_x = x
            x += (pill_w + gap) * size
    pw, ph = pill_w * size, pill_h * size
    py = base - cap / 2 - ph / 2
    memoji = base64.b64encode((ASSETS / "memoji.webp").read_bytes()).decode()

    lede1 = [("AI engineer at ", BODY), ("Vloto", INK), (", founder of ", BODY), ("Virelio", INK), (".", BODY)]
    lede2 = [("I build AI that ships, not demos.", INK)]
    span = lambda parts: "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in parts)
    lede_text = "".join(t for t, _ in lede1 + lede2)
    status = "Open to new roles · Amsterdam"
    site = "omardev.xyz →"

    css = f"""
{embed(name_font, "OmarNs", "Name")}
{embed(lede_font, lede_text, "Lede")}
{embed(mono, status + site, "Mono")}
.l{{font:{size:.2f}px Name;fill:{INK};transform:translateY({size * 1.05:.1f}px);animation:rise .7s cubic-bezier(.2,.8,.2,1) forwards}}
.lede{{font:27px Lede;letter-spacing:-.02em}}
.mono{{font:13px Mono;fill:#55534f}}
.pill{{transform-box:fill-box;transform-origin:center;transform:scale(0);animation:pop .6s .45s cubic-bezier(.3,1.6,.5,1) forwards}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 1.8s ease-out infinite}}
@keyframes rise{{to{{transform:none}}}}
@keyframes pop{{to{{transform:none}}}}
@keyframes ping{{0%{{transform:scale(1);opacity:.6}}80%,100%{{transform:scale(3);opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.l,.pill{{animation:none;transform:none}}.ping{{animation:none;opacity:0}}}}
"""
    H = 330
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Omar Nassar. AI engineer at Vloto, founder of Virelio. I build AI that ships, not demos.">
<style>{css}</style>
<defs>
<clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<clipPath id="rise"><rect x="0" y="{base - size:.1f}" width="{W}" height="{size * 1.06:.1f}"/></clipPath>
<clipPath id="pillc"><rect x="{pill_x:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="{ph / 2:.1f}"/></clipPath>
</defs>
<g clip-path="url(#card)">
<rect width="{W}" height="{H}" fill="{CANVAS}"/>
<circle class="ping" cx="{PAD + 4}" cy="40" r="4" fill="{SIGNAL}"/>
<circle cx="{PAD + 4}" cy="40" r="4" fill="{SIGNAL}"/>
<text class="mono" x="{PAD + 18}" y="44.5">{escape(status)}</text>
<text class="mono" x="{W - PAD}" y="44.5" text-anchor="end">{escape(site)}</text>
<text class="lede" x="{PAD}" y="102">{span(lede1)}</text>
<text class="lede" x="{PAD}" y="136">{span(lede2)}</text>
<g clip-path="url(#rise)">{"".join(letters)}</g>
<g class="pill">
<g clip-path="url(#pillc)">
<rect x="{pill_x:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" fill="#050505"/>
<image href="data:image/webp;base64,{memoji}" x="{pill_x:.1f}" y="{py - ph * 0.22:.1f}" width="{pw:.1f}" height="{ph * 1.4:.1f}" preserveAspectRatio="xMidYMin slice"/>
</g>
<rect x="{pill_x:.1f}" y="{py:.1f}" width="{pw:.1f}" height="{ph:.1f}" rx="{ph / 2:.1f}" fill="none" stroke="#00000022"/>
</g>
</g>
</svg>
"""
    (ASSETS / "hero.svg").write_text(svg)


# ---------- terminal ----------

def get_json(url, token=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER, "Accept": "application/vnd.github+json"})
    if token and "github.com" in url:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def stats():
    token = os.environ.get("GITHUB_TOKEN")
    repos = get_json(f"https://api.github.com/users/{USER}", token)["public_repos"]
    # The number on the public contribution graph, private contributions included.
    since = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    query = 'query($u:String!,$f:DateTime!){user(login:$u){contributionsCollection(from:$f){contributionCalendar{totalContributions}}}}'
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": query, "variables": {"u": USER, "f": since}}).encode(),
                                 headers={"User-Agent": USER, "Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        commits = json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    npm = get_json("https://api.npmjs.org/downloads/point/last-month/" + ",".join(PACKAGES))
    downloads = sum(p["downloads"] for p in npm.values() if p)
    return repos, commits, downloads


def wide_lines(repos, commits, downloads, q):
    return [
        ([("p", "› "), ("k", q)], 0),
        ([("m", "  ● reading "), ("", "omardev.xyz"), ("m", " … "), ("g", "ok")], 0),
        ([("m", "  ● reading "), ("", f"{repos} public repositories"), ("m", " … "), ("g", "ok")], 0.45),
        ([("m", "  ● running "), ("", "gh contributions --last=30.days"), ("m", " → "), ("k", f"{commits} contributions")], 0.5),
        ([("m", "  ● running "), ("", "npm view " + " ".join(PACKAGES)), ("m", " → "), ("k", f"{downloads} downloads/mo")], 0.5),
        ([], 0.4),
        ([("", "AI engineer in Amsterdam. I ship AI products end to end: agents, RAG and document")], 0.25),
        ([("", "search, LLM apps, voice assistants, computer vision, and the evals that keep them")], 0.08),
        ([("", "honest. In production at Vloto; open-source tools for people who code with agents.")], 0.08),
        ([], 0.08),
        ([("p", "→ "), ("", "hiring for AI? Agents, RAG, LLMs, all of it: "), ("k", EMAIL)], 0.3),
    ]


def narrow_lines(repos, commits, downloads, q):
    return [
        ([("p", "› "), ("k", q)], 0),
        ([("m", "  ● reading "), ("", "omardev.xyz"), ("m", " … "), ("g", "ok")], 0),
        ([("m", "  ● reading "), ("", f"{repos} repositories"), ("m", " … "), ("g", "ok")], 0.45),
        ([("m", "  ● "), ("", "gh contribs --30d"), ("m", " → "), ("k", f"{commits} contributions")], 0.5),
        ([("m", "  ● "), ("", f"npm view ({len(PACKAGES)} packages)"), ("m", " → "), ("k", f"{downloads}/mo")], 0.5),
        ([], 0.4),
        ([("", "AI engineer in Amsterdam. I ship AI")], 0.25),
        ([("", "products end to end: agents, RAG and")], 0.08),
        ([("", "document search, LLM apps, voice")], 0.08),
        ([("", "assistants, computer vision, and the")], 0.08),
        ([("", "evals that keep them honest.")], 0.08),
        ([], 0.08),
        ([("p", "→ "), ("", "hiring for AI? Agents, RAG,")], 0.3),
        ([("", "  LLMs, all of it:")], 0.08),
        ([("", "  "), ("k", EMAIL)], 0.08),
    ]


def build_terminal(name, W, make_lines, data):
    repos, commits, downloads = data
    S, LH, PAD = 14, 24, 26
    cw = S * 0.6  # Geist Mono advance is 600/1000 em
    q = "who is omar nassar?"
    # (segments, delay after previous line). Segment classes: p prompt, k strong, m muted, g green.
    lines = make_lines(repos, commits, downloads, q)

    head = 46
    rows, t = [], 0.6
    y = head + 32
    for n, (segs, d) in enumerate(lines):
        t += d
        if segs:
            tspans = "".join(f'<tspan class="{c}">{escape(s)}</tspan>' if c else escape(s) for c, s in segs)
            rows.append(f'<text class="row" x="{PAD}" y="{y}" style="animation-delay:{t:.2f}s" xml:space="preserve">{tspans}</text>')
        if n == 0:
            # Typewriter: a cover slides off the question one character at a time.
            qx = PAD + 2 * cw
            type_t = len(q) * 0.055
            rows.append(f'<rect class="cover" x="{qx:.1f}" y="{y - S}" width="{(len(q) + 1) * cw:.1f}" height="{S + 6}" fill="#010409" '
                        f'style="animation:type {type_t:.2f}s steps({len(q)}) {t + 0.3:.2f}s forwards"/>')
            t += 0.3 + type_t + 0.6  # first tool line lands 0.6s after typing ends
        y += LH
    caret_y = y
    H = caret_y + 30
    all_text = "".join(s for segs, _ in lines for _, s in segs) + "›█"

    css = f"""
{embed(load("GeistMono-Regular.woff2"), all_text, "TermMono")}
{embed(load("GeistMono-SemiBold.woff2"), all_text, "TermMonoBold")}
text{{font:{S}px TermMono;fill:#e6edf3}}
.bar{{font-size:12px;fill:#7d8590}}
.p{{fill:{SIGNAL}}}.m{{fill:#7d8590}}.g{{fill:#3fb950}}.k{{font-family:TermMonoBold}}
.row{{opacity:0;animation:in .3s ease-out forwards}}
.caret{{opacity:0;animation:in 0s {t + 0.4:.2f}s forwards,blink 1s steps(1) {t + 0.4:.2f}s infinite}}
@keyframes in{{from{{opacity:0;transform:translateY(4px)}}to{{opacity:1;transform:none}}}}
@keyframes type{{to{{transform:translateX({len(q) * cw:.1f}px)}}}}
@keyframes blink{{0%{{opacity:1}}50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.row,.caret{{animation:none;opacity:1}}.cover{{display:none}}}}
"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="An agent session answering who Omar Nassar is: AI engineer in Amsterdam shipping agents, RAG, LLM apps, voice and computer vision. {repos} public repositories, {commits} contributions in the last 30 days. Contact {EMAIL}.">
<style>{css}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="#010409" stroke="#30363d"/>
<line x1="1" y1="{head}" x2="{W - 1}" y2="{head}" stroke="#21262d"/>
<circle cx="{PAD + 2}" cy="23" r="5.5" fill="#30363d"/><circle cx="{PAD + 20}" cy="23" r="5.5" fill="#30363d"/><circle cx="{PAD + 38}" cy="23" r="5.5" fill="#30363d"/>
<text class="bar" x="{PAD + 58}" y="27">~/omar · agent session</text>
{chr(10).join(rows)}
<text class="p" x="{PAD}" y="{caret_y}">›</text>
<rect class="caret" x="{PAD + 2 * cw:.1f}" y="{caret_y - S + 1}" width="{cw:.1f}" height="{S + 3}" fill="{SIGNAL}"/>
</svg>
"""
    (ASSETS / name).write_text(svg)



if __name__ == "__main__":
    build_hero()
    data = stats()
    print("stats: {} repos, {} contributions/30d, {} npm downloads/mo".format(*data))
    build_terminal("terminal.svg", 900, wide_lines, data)
    build_terminal("terminal-narrow.svg", 440, narrow_lines, data)
    for f in ("hero.svg", "terminal.svg", "terminal-narrow.svg"):
        print(f, (ASSETS / f).stat().st_size // 1024, "KB")
