# Glossar – wird nach studien.py von build.py ausgeführt (teilt page, write, esc, BASE, eps, OUT, STUDIEN, _folge, RICHTUNG).
# Quelle: _werkzeug/glossar.json  ·  Ausgabe: glossar/, glossar/<id>/, glossar/daten.json, Ergänzung von llms.txt und sitemap.xml
import json as _gjson, os as _gos

_GSRC = _gos.path.join(_gos.path.dirname(_gos.path.abspath(__file__)), "glossar.json")
GLOSSAR = _gjson.load(open(_GSRC, encoding="utf-8"))
GLOSSAR.sort(key=lambda g: g["begriff"].lower())
_gidx = {g["id"]: g for g in GLOSSAR}
_sidx = {s["id"]: s for s in STUDIEN}

CSS_GLOSSAR = """
.az{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0 18px}.az a{display:inline-block;min-width:30px;text-align:center;padding:4px 8px;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--ink);font-size:14px}
.az a:hover{border-color:var(--teal);color:var(--teal)}
.gl h2{font-size:22px;margin:26px 0 4px;color:var(--teal)}
.gt{padding:12px 0;border-top:1px solid var(--line)}.gt h3{margin:0 0 3px;font-size:18px}.gt h3 a{color:var(--ink);text-decoration:none}.gt h3 a:hover{color:var(--teal)}
.gt p{margin:0;font-size:15px}.gt .en{font-size:13px;color:var(--mute);margin-left:6px;font-weight:400}
.gbox{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px 20px;margin:16px 0}
.gbox h2{font-size:17px;margin:0 0 8px}.gbox ul{margin:0;padding-left:20px}.gbox li{margin:4px 0}
.warn{border-left:3px solid #d8b44a}
"""
open(_gos.path.join(OUT, "style.css"), "a", encoding="utf-8").write(CSS_GLOSSAR.strip() + "\n")


def _buchstabe(b):
    c = b[0].upper()
    return {"Ä": "A", "Ö": "O", "Ü": "U"}.get(c, c if c.isalpha() else "#")


def _studien_links(g, pre):
    out = []
    for sid in g.get("studien") or []:
        s = _sidx.get(sid)
        if s:
            out.append(f'<li><a href="{pre}studien/{s["id"]}/">{esc(s["titel_de"])}</a> <span class="meta">· MFK-Score {str(s["score"]["gesamt"]).replace(".", ",")} · {RICHTUNG[s["richtung"]][0]}</span></li>')
    return out


def _folgen_links_g(g, pre):
    out = []
    for n in g.get("folgen") or []:
        e = _folge.get(n)
        if e:
            out.append(f'<li><a href="{pre}folge/{e["slug"]}/">Folge {n}: {esc(e["kopf"])}</a></li>')
    return out


def _en_span(g):
    if g.get("en") and g["en"].lower() != g["begriff"].lower():
        return '<span class="en">' + esc(g["en"]) + '</span>'
    return ""


# ---------- Übersicht A–Z
gruppen = {}
for g in GLOSSAR:
    gruppen.setdefault(_buchstabe(g["begriff"]), []).append(g)
az = "".join(f'<a href="#b-{b}">{b}</a>' for b in sorted(gruppen))
bloecke = []
for b in sorted(gruppen):
    eintr = "".join(
        f'<div class="gt" data-q="{esc((g["begriff"] + " " + g.get("en", "") + " " + g["kurz"]).lower())}"><h3><a href="{g["id"]}/">{esc(g["begriff"])}</a>'
        + _en_span(g) + f'</h3><p>{esc(g["kurz"])}</p></div>'
        for g in gruppen[b])
    bloecke.append(f'<section class="gl" id="b-{b}"><h2>{b}</h2>{eintr}</section>')
ld_set = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "Marketing-Glossar von Marketing Facts Kompakt",
          "url": BASE + "/glossar/", "inLanguage": "de", "license": "https://creativecommons.org/licenses/by/4.0/",
          "hasDefinedTerm": [{"@type": "DefinedTerm", "name": g["begriff"], "description": g["kurz"], "url": f"{BASE}/glossar/{g['id']}/"} for g in GLOSSAR]}
uebersicht_g = f"""<div style="padding:36px 0 0"><p class="kicker">Glossar</p><h1>Marketing-Begriffe, <span class="g">belegt</span> erklärt</h1>
<p class="lead">{len(GLOSSAR)} Fachbegriffe aus Markenführung, Media, Messung, Preis und KI-Suche – kurz erklärt, mit typischen Verwechslungen und verknüpft mit den passenden Studien der <a href="../studien/">Studiendatenbank</a> und den Podcastfolgen.</p></div>
<div class="sfilter" role="search"><input id="gq" type="search" placeholder="Begriff suchen, z. B. Attribution, Share of Search …" aria-label="Glossar durchsuchen"></div>
<nav class="az" aria-label="Alphabet">{az}</nav>
<div id="gliste">{''.join(bloecke)}</div>
<p class="meta" style="margin-top:28px">Erklärungen in eigenen Worten. Frei nutzbar unter {LIZENZ} mit Quellenangabe „Marketing Facts Kompakt“. Alle Begriffe als <a href="daten.json">JSON</a>.</p>
<script>(function(){{var q=document.getElementById('gq');q.addEventListener('input',function(){{var w=q.value.toLowerCase().trim();document.querySelectorAll('#gliste .gt').forEach(function(e){{e.hidden=w&&e.dataset.q.indexOf(w)<0}});document.querySelectorAll('#gliste .gl').forEach(function(s){{s.hidden=!s.querySelector('.gt:not([hidden])')}})}})}})();</script>
<script type="application/ld+json">{_gjson.dumps(ld_set, ensure_ascii=False)}</script>"""
write("glossar/index.html", page(f"Marketing-Glossar: {len(GLOSSAR)} Begriffe mit Studienbelegen – Marketing Facts Kompakt",
                                 f"{len(GLOSSAR)} Marketing-Begriffe kurz erklärt – von Attribution und Carryover bis Share of Search und GEO, mit Studienbelegen und MFK-Score.",
                                 uebersicht_g, path="glossar/", cur="glossar", depth=1))

# ---------- Einzelseiten
for g in GLOSSAR:
    pre = "../../"
    st = _studien_links(g, pre)
    fo = _folgen_links_g(g, pre)
    ve = [f'<a href="../{v}/">{esc(_gidx[v]["begriff"])}</a>' for v in g.get("verwandt") or [] if v in _gidx]
    en = ('<p class="meta">Englisch: ' + esc(g["en"]) + '</p>') if g.get("en") else ""
    box_v = ('<div class="gbox warn"><h2>Häufige Verwechslung</h2><p>' + esc(g["verwechslung"]) + '</p></div>') if g.get("verwechslung") else ""
    box_s = ('<div class="gbox"><h2>Studien dazu</h2><ul>' + "".join(st) + '</ul></div>') if st else ""
    box_f = ('<div class="gbox"><h2>Im Podcast</h2><ul>' + "".join(fo) + '</ul></div>') if fo else ""
    box_r = ('<p class="meta">Verwandte Begriffe: ' + " · ".join(ve) + '</p>') if ve else ""
    body = f"""<div style="padding:36px 0 0"><p class="kicker"><a href="../">Glossar</a></p><h1>{esc(g["begriff"])}</h1>{en}
<p class="lead">{esc(g["kurz"])}</p></div>
<div class="prose"><p>{esc(g["text"])}</p></div>
{box_v}
{box_s}
{box_f}
{box_r}
<p class="meta" style="margin-top:24px"><a href="../">← Alle Begriffe</a> · <a href="{pre}studien/methodik/">So funktioniert der MFK-Score</a></p>
<script type="application/ld+json">{_gjson.dumps({"@context": "https://schema.org", "@type": "DefinedTerm", "name": g["begriff"], "alternateName": g.get("en") or None, "description": g["kurz"] + " " + g["text"], "url": f"{BASE}/glossar/{g['id']}/", "inDefinedTermSet": BASE + "/glossar/"}, ensure_ascii=False)}</script>"""
    write(f"glossar/{g['id']}/index.html", page(f"{g['begriff']} – Marketing-Glossar | Marketing Facts Kompakt", g["kurz"], body, path=f"glossar/{g['id']}/", cur="glossar", depth=2))

# ---------- Daten, llms.txt, Sitemap
write("glossar/daten.json", _gjson.dumps({"name": "MFK-Marketing-Glossar", "lizenz": LIZENZ, "quelle": BASE + "/glossar/", "anzahl": len(GLOSSAR),
                                         "begriffe": [{k: g.get(k) for k in ("id", "begriff", "en", "kurz", "text", "verwechslung", "studien", "folgen", "verwandt")} | {"url": f"{BASE}/glossar/{g['id']}/"} for g in GLOSSAR]},
                                        ensure_ascii=False, indent=1))
_llms = open(_gos.path.join(OUT, "llms.txt"), encoding="utf-8").read()
_llms += "\n## Glossar\n\n" + "\n".join(f"- [{g['begriff']}]({BASE}/glossar/{g['id']}/): {g['kurz']}" for g in GLOSSAR) + "\n"
write("llms.txt", _llms)
_gsm = open(_gos.path.join(OUT, "sitemap.xml"), encoding="utf-8").read().replace(
    "</urlset>\n", "".join(f"<url><loc>{BASE}/{u}</loc></url>\n" for u in ["glossar/"] + [f"glossar/{g['id']}/" for g in GLOSSAR]) + "</urlset>\n")
write("sitemap.xml", _gsm)
print("ok", len(GLOSSAR), "Glossarbegriffe")
