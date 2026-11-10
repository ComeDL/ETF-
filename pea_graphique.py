#!/usr/bin/env python3
"""Génère graphique.html : évolution du portefeuille + répartition actuelle.

Lit achats.csv, positions.csv, prix.csv et (optionnel) historique_valeur.csv
(date,valeur_totale relevée chaque mois sur BoursoBank).
Ouvrir graphique.html dans un navigateur.
"""

import csv
import html
from datetime import date
from pathlib import Path

FICHIER_ACHATS = "achats.csv"            # date,etf,quantite,prix_unitaire
FICHIER_POSITIONS = "positions.csv"      # etf,quantite
FICHIER_PRIX = "prix.csv"                # etf,prix
FICHIER_HISTORIQUE = "historique_valeur.csv"  # optionnel : date,valeur_totale
SORTIE = "graphique.html"

L = 70          # marge gauche
R = 30          # marge droite
T = 50          # marge haute
B = 50          # marge basse
W, H = 920, 380  # taille du graphique en pixels

COULEURS = ["#2563eb", "#dc2626", "#16a34a", "#d97706", "#7c3aed",
            "#0891b2", "#db2777", "#65a30d"]


def lire_csv(chemin):
    with open(chemin, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def echelle(valeurs, taille, marge_debut, marge_fin):
    vmin, vmax = min(valeurs), max(valeurs)
    if vmax == vmin:
        vmax = vmin + 1
    amplitude = vmax - vmin
    vmin -= amplitude * 0.05
    vmax += amplitude * 0.05

    def proj(v):
        return marge_debut + (v - vmin) / (vmax - vmin) * (taille - marge_debut - marge_fin)

    return proj, vmin, vmax


def graphique_courbes(series, titre):
    """series : liste de (nom, couleur, [(date, valeur)]) -> SVG."""
    toutes_dates = sorted({d for _, _, pts in series for d, _ in pts})
    x_min, x_max = toutes_dates[0].toordinal(), toutes_dates[-1].toordinal()
    if x_max == x_min:
        x_max = x_min + 1
    toutes_valeurs = [v for _, _, pts in series for _, v in pts] or [0, 1]
    proj_y, y_min, y_max = echelle(toutes_valeurs, H, T, B)

    def px(d):
        return L + (d.toordinal() - x_min) / (x_max - x_min) * (W - L - R)

    pas_y = (y_max - y_min) / 5
    parties = [f'<text x="8" y="{T - 10}" font-size="15" font-weight="bold">{html.escape(titre)}</text>']
    for i in range(6):
        v = y_min + i * pas_y
        y = proj_y(v)
        parties.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W - R}" y2="{y:.1f}" stroke="#e5e7eb"/>')
        parties.append(f'<text x="{L - 6}" y="{y + 4:.1f}" font-size="11" text-anchor="end" fill="#6b7280">{v:,.0f} €</text>')
    nb_x = min(6, len(toutes_dates))
    for i in range(nb_x):
        d = toutes_dates[round(i * (len(toutes_dates) - 1) / max(nb_x - 1, 1))]
        x = px(d)
        parties.append(f'<line x1="{x:.1f}" y1="{T}" x2="{x:.1f}" y2="{H - B}" stroke="#f3f4f6"/>')
        parties.append(f'<text x="{x:.1f}" y="{H - B + 18}" font-size="11" text-anchor="middle" fill="#6b7280">{d.strftime("%d/%m/%y")}</text>')
    parties.append(f'<rect x="{L}" y="{T}" width="{W - L - R}" height="{H - T - B}" fill="none" stroke="#9ca3af"/>')
    legende_x = L + 10
    for nom, couleur, pts in series:
        if pts:
            points = " ".join(f"{px(d):.1f},{proj_y(v):.1f}" for d, v in pts)
            parties.append(f'<polyline points="{points}" fill="none" stroke="{couleur}" stroke-width="2.5"/>')
            for d, v in pts[-1:]:
                parties.append(f'<circle cx="{px(d):.1f}" cy="{proj_y(v):.1f}" r="4" fill="{couleur}"/>')
        parties.append(f'<rect x="{legende_x}" y="{T + 8}" width="12" height="12" fill="{couleur}" rx="2"/>')
        parties.append(f'<text x="{legende_x + 18}" y="{T + 18}" font-size="12">{html.escape(nom)}</text>')
        legende_x += 18 + 9 * len(nom) + 30
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">{"".join(parties)}</svg>'


def camembert(donnees, titre):
    """donnees : [(nom, valeur, couleur)] -> SVG."""
    total = sum(v for _, v, _ in donnees) or 1
    cx, cy, r = 110, 130, 90
    parties = [f'<text x="8" y="24" font-size="15" font-weight="bold">{html.escape(titre)}</text>']
    angle = -90
    for nom, v, couleur in donnees:
        part = v / total * 360
        if part >= 359.9:
            parties.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{couleur}"/>')
        else:
            import math
            a1 = math.radians(angle)
            a2 = math.radians(angle + part)
            x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
            x2, y2 = cx + r * math.cos(a2), cy + r * math.sin(a2)
            grand = 1 if part > 180 else 0
            parties.append(f'<path d="M {cx} {cy} L {x1:.1f} {y1:.1f} A {r} {r} 0 {grand} 1 {x2:.1f} {y2:.1f} Z" fill="{couleur}" stroke="#fff" stroke-width="2"/>')
        angle += part
    lx, ly = 230, 60
    for nom, v, couleur in donnees:
        pct = v / total * 100
        parties.append(f'<rect x="{lx}" y="{ly - 11}" width="12" height="12" fill="{couleur}" rx="2"/>')
        parties.append(f'<text x="{lx + 18}" y="{ly}" font-size="12">{html.escape(nom)} — {v:,.0f} € ({pct:.1f} %)</text>')
        ly += 24
    return f'<svg width="560" height="260" viewBox="0 0 560 260" xmlns="http://www.w3.org/2000/svg">{"".join(parties)}</svg>'


def main():
    base = Path(__file__).parent
    achats = lire_csv(base / FICHIER_ACHATS)
    positions = {r["etf"].strip(): float(r["quantite"].replace(",", ".")) for r in lire_csv(base / FICHIER_POSITIONS)}
    prix = {r["etf"].strip(): float(r["prix"].replace(",", ".")) for r in lire_csv(base / FICHIER_PRIX)}

    par_date = {}
    for r in achats:
        d = date.fromisoformat(r["date"].strip())
        montant = float(r["quantite"].replace(",", ".")) * float(r["prix_unitaire"].replace(",", "."))
        par_date[d] = par_date.get(d, 0.0) + montant
    investi, cumul = [], 0.0
    for d in sorted(par_date):
        cumul += par_date[d]
        investi.append((d, cumul))

    series = [("Investi cumulé", "#6b7280", investi)]
    hist_path = base / FICHIER_HISTORIQUE
    if hist_path.exists():
        hist = [(date.fromisoformat(r["date"].strip()), float(r["valeur_totale"].replace(",", ".")))
                for r in lire_csv(hist_path)]
        series.append(("Valeur du portefeuille", "#2563eb", hist))

    valeur_actuelle = sum(q * prix.get(e, 0.0) for e, q in positions.items())
    if valeur_actuelle > 0 and investi:
        series.append(("Valeur actuelle", "#16a34a", [(investi[-1][0], valeur_actuelle)]))

    cam = [(e, q * prix.get(e, 0.0), COULEURS[i % len(COULEURS)])
           for i, (e, q) in enumerate(sorted(positions.items())) if q * prix.get(e, 0.0) > 0]

    pnl = valeur_actuelle - cumul
    pct = (pnl / cumul * 100) if cumul else 0.0
    resume = (f"Investi : {cumul:,.2f} € — Valeur actuelle : {valeur_actuelle:,.2f} € "
              f"— +/- latente : {pnl:+,.2f} € ({pct:+.1f} %)")

    page = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<title>PEA — graphique</title>
<style>
body{font-family:system-ui,sans-serif;margin:24px;color:#111827}
h1{font-size:20px} .resume{font-size:15px;color:#374151;margin-bottom:18px}
.carte{border:1px solid #e5e7eb;border-radius:12px;padding:16px;margin-bottom:18px;display:inline-block}
</style></head><body>
<h1>Suivi PEA — graphiques</h1>
<p class="resume">__RESUME__</p>
<div class="carte">__COURBES__</div>
<div class="carte">__CAMEMBERT__</div>
<p style="color:#6b7280;font-size:12px">Généré le __DATE__ par pea_graphique.py — données : achats.csv, positions.csv, prix.csv__HIST__.</p>
</body></html>"""
    page = (page.replace("__RESUME__", html.escape(resume))
                .replace("__COURBES__", graphique_courbes(series, "Évolution du portefeuille"))
                .replace("__CAMEMBERT__", camembert(cam, "Répartition actuelle"))
                .replace("__DATE__", date.today().strftime("%d/%m/%Y"))
                .replace("__HIST__", f", {FICHIER_HISTORIQUE}" if hist_path.exists() else ""))
    sortie = base / SORTIE
    sortie.write_text(page, encoding="utf-8")
    print(f"Graphique généré : {sortie} (ouvrir dans un navigateur)")
    print(resume)


if __name__ == "__main__":
    main()
