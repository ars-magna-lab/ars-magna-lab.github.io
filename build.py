"""Generate arsmagnalab.com from content.json and _src/.

Usage: python3 build.py            # generate
       python3 build.py --check    # also check every external link answers (needs network)

Output, per language (es at the root, the others under /<lang>/):
  index.html                 home, with the index of projects
  llull/index.html           why the name
  futbolin/index.html        the foosball table, from _src/futbolin.<lang>.html

The foosball pages are written by hand, one file per language. Their media and
diagrams live once in futbolin/ (the diagrams stay in Spanish); the sources only
leave the @@...@@ placeholders for the parts that change with the language.
Texts in content.json are {"es": ..., "ca": ..., "en": ...} or a plain string.
"""
import json
import math
import sys
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = "https://arsmagnalab.com/"
LANG_NAMES = {"es": "Español", "en": "English", "ca": "Català"}


def t(v, lang):
    return v[lang] if isinstance(v, dict) else v


def base(lang):
    return "" if lang == "es" else f"{lang}/"


def link(url, prefix):
    """External links open as they are; internal ones are relative to the page."""
    if url.startswith("http"):
        return f'<a href="{escape(url)}" rel="noopener">'
    return f'<a href="{prefix}{escape(url)}">'


def lang_nav(c, lang, path, prefix):
    return f'<nav class="lang" aria-label="{LANG_NAMES[lang]}">' + " ".join(
        f'<a href="{prefix}{base(l)}{path}" hreflang="{l}" lang="{l}"{" aria-current=page" if l == lang else ""}>{l.upper()}</a>'
        for l in c["langs"]) + "</nav>"


def alternates(c, lang, path):
    return "\n".join([f'<link rel="canonical" href="{SITE}{base(lang)}{path}">']
                     + [f'<link rel="alternate" hreflang="{l}" href="{SITE}{base(l)}{path}">' for l in c["langs"]]
                     + [f'<link rel="alternate" hreflang="x-default" href="{SITE}{path}">'])


def figure_a(size):
    # Llull's Figura A with the letters B..K, same geometry as the channel banner
    c, r = 100, 74
    pts = [(c + r * math.cos(i * 2 * math.pi / 9 - math.pi / 2), c + r * math.sin(i * 2 * math.pi / 9 - math.pi / 2)) for i in range(9)]
    chords = "".join(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>'
                     for i, a in enumerate(pts) for b in pts[i + 1:])
    nodes = "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="11"/><text x="{x:.1f}" y="{y + 4.5:.1f}">{ch}</text>'
                    for (x, y), ch in zip(pts, "BCDEFGHIK"))
    return (f'<svg class="wheel" width="{size}" height="{size}" viewBox="0 0 200 200" aria-hidden="true">'
            f'<circle class="ring2" cx="100" cy="100" r="92"/><g class="chords">{chords}</g><circle class="ring" cx="100" cy="100" r="{r}"/>'
            f'<g class="dots">{nodes}</g><circle class="hub" cx="100" cy="100" r="5"/></svg>')


def shell(c, lang, path, title, description, body):
    """path: page path inside a language, '' for home or 'llull/'."""
    prefix = "../" * (base(lang) + path).count("/")
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="author" content="Edu Herraiz">
{alternates(c, lang, path)}
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:image" content="{SITE}og.jpg">
<meta property="og:url" content="{SITE}{base(lang)}{path}">
<meta name="twitter:card" content="summary_large_image">
<meta name="color-scheme" content="dark">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}assets/style.css">
</head>
<body>
<main>
  {lang_nav(c, lang, path, prefix)}
{body}
  <footer>© <a href="{c["links"]["author"]}" rel="noopener">Edu Herraiz</a> · {escape(c["ui"][lang]["footer"])}</footer>
</main>
</body>
</html>
"""


def project(p, lang, prefix):
    meta = " · ".join(x for x in [p.get("year", ""), t(p.get("tags", ""), lang)] if x)
    links = " ".join(f'{link(u, "")}{escape(t(k, lang))}</a>' for k, u in p["links"])
    first = p["links"][0][1]
    thumb = link(first, "").replace("<a ", '<a class="thumb" tabindex="-1" ', 1)
    return f"""      <li class="proj">
        {thumb}<img src="{prefix}assets/projects/{p["image"]}" width="176" height="99" alt="" loading="lazy"></a>
        <div>
          <div class="proj-head"><h3>{escape(t(p["name"], lang))}</h3><span class="meta">{escape(meta)}</span></div>
          <p>{escape(p[lang])}</p>
          <p class="links">{links}</p>
        </div>
      </li>"""


def home(c, lang):
    ui = c["ui"][lang]
    L = c["links"]
    prefix = "../" * base(lang).count("/")
    intro = "\n".join(f"    <p>{escape(p)}</p>" for p in ui["intro"])
    projects = "\n".join(project(p, lang, prefix) for p in c["projects"])
    body = f"""
  <header class="hero">
    <img class="figura" src="{prefix}figura-a.png" width="200" height="200" alt="{escape(ui["figura_alt"])}">
    <h1>Ars Magna Lab</h1>
    <p class="lema">{escape(ui["lema"])}</p>
{intro}
    <a class="canal" href="{L["youtube"]}" rel="noopener">{escape(ui["canal"])}</a>
    <p class="more"><a href="llull/">{escape(ui["why_link"])} →</a></p>
  </header>

  <section>
    <h2>{escape(ui["projects"])}</h2>
    <ul class="projects">
{projects}
    </ul>
    <p class="more"><a href="{L["github"]}" rel="noopener">{escape(ui["github_link"])} →</a></p>
  </section>
"""
    return shell(c, lang, "", ui["title"], ui["description"], body)


def name_page(c, lang):
    ui = c["ui"][lang]
    n = c["name_page"][lang]
    paras = lambda ps: "\n".join(f"    <p>{escape(p)}</p>" for p in ps)
    body = f"""
  <article class="essay">
    <p class="back"><a href="../">← {escape(ui["back"])}</a></p>
    <h1>{escape(n["title"])}</h1>
    <p class="lead">{escape(n["lead"])}</p>
    <figure>{figure_a(260)}</figure>
{paras(n["body"])}
    <h2>{escape(n["lab_title"])}</h2>
{paras(n["lab"])}
    <p class="back"><a href="../">← {escape(ui["back"])}</a></p>
  </article>
"""
    return shell(c, lang, "llull/", f'{n["title"]} · Ars Magna Lab', n["lead"], body)


def futbolin(c, lang):
    path = "futbolin/"
    prefix = "../" * (base(lang) + path).count("/")
    html = (ROOT / "_src" / f"futbolin.{lang}.html").read_text()
    for k, v in {"ALTERNATES": alternates(c, lang, path), "URL": f"{SITE}{base(lang)}{path}",
                 "NAV": lang_nav(c, lang, path, prefix), "HOME": f"{prefix}{base(lang)}", "ROOT": prefix}.items():
        html = html.replace(f"@@{k}@@", v)
    assert "@@" not in html, f"placeholder sin rellenar en _src/futbolin.{lang}.html"
    return html


def check(c):
    urls = [u for p in c["projects"] for _, u in p["links"] if u.startswith("http")]
    urls += list(c["links"].values())
    bad = []
    for u in dict.fromkeys(urls):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
            code = urllib.request.urlopen(req, timeout=15).status
        except Exception as e:
            code = getattr(e, "code", None) or type(e).__name__
        if code != 200:
            bad.append(f"  {code}  {u}")
    print("\n".join(["enlaces caídos:"] + bad) if bad else "todos los enlaces responden")
    return not bad


def main():
    c = json.loads((ROOT / "content.json").read_text())
    if "--check" in sys.argv and not check(c):
        sys.exit(1)
    out = []
    for lang in c["langs"]:
        for rel, html in ((base(lang) + "index.html", home(c, lang)),
                          (base(lang) + "llull/index.html", name_page(c, lang)),
                          (base(lang) + "futbolin/index.html", futbolin(c, lang))):
            f = ROOT / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(html)
            out.append(rel)
    print(", ".join(out))


if __name__ == "__main__":
    main()
