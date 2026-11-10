#!/usr/bin/env python3
"""Journal DCA PEA : historique des achats, PRU moyen et performance."""

import csv
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

FICHIER_ACHATS = "achats.csv"  # date,etf,quantite,prix_unitaire
FICHIER_PRIX = "prix.csv"      # etf,prix_actuel


def lire_achats(chemin):
    achats = defaultdict(list)
    with open(chemin, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            etf = ligne["etf"].strip()
            achats[etf].append({
                "date": ligne["date"].strip(),
                "qte": float(ligne["quantite"].replace(",", ".")),
                "prix": float(ligne["prix_unitaire"].replace(",", ".")),
            })
    return achats


def lire_prix(chemin):
    prix = {}
    with open(chemin, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            prix[ligne["etf"].strip()] = float(ligne["prix"].replace(",", "."))
    return prix


def main():
    achats = lire_achats(FICHIER_ACHATS)
    prix = lire_prix(FICHIER_PRIX)

    if not achats:
        sys.exit("Erreur : aucun achat dans " + FICHIER_ACHATS)

    total_investi = 0.0
    total_valeur = 0.0

    print(f"{'ETF':<10}{'Achats':>7}{'Qté totale':>12}{'Investi':>12}{'PRU':>9}"
          f"{'Prix':>9}{'Valeur':>12}{'+/-':>10}{'%':>8}")
    print("-" * 88)

    for etf in sorted(achats):
        lignes = sorted(achats[etf], key=lambda a: a["date"])
        qte = sum(a["qte"] for a in lignes)
        investi = sum(a["qte"] * a["prix"] for a in lignes)
        pru = investi / qte if qte else 0.0
        if etf not in prix:
            sys.exit(f"Erreur : pas de prix actuel pour {etf} dans {FICHIER_PRIX}")
        pu = prix[etf]
        valeur = qte * pu
        pnl = valeur - investi
        pct = (pnl / investi * 100) if investi else 0.0
        total_investi += investi
        total_valeur += valeur
        print(f"{etf:<10}{len(lignes):>7}{qte:>12.4f}{investi:>12,.2f}{pru:>9.2f}"
              f"{pu:>9.2f}{valeur:>12,.2f}{pnl:>+10,.2f}{pct:>+7.1f}%")
        print(f"{'':>10}dernier achat : {lignes[-1]['date']} "
              f"({lignes[-1]['qte']:g} parts à {lignes[-1]['prix']:.2f} €)")

    print("-" * 88)
    pnl = total_valeur - total_investi
    pct = (pnl / total_investi * 100) if total_investi else 0.0
    print(f"{'TOTAL':<10}{'':>7}{'':>12}{total_investi:>12,.2f}{'':>9}"
          f"{'':>9}{total_valeur:>12,.2f}{pnl:>+10,.2f}{pct:>+7.1f}%")

    premiere = min(a["date"] for lignes in achats.values() for a in lignes)
    print(f"\nPremier achat : {premiere} — ancienneté : "
          f"{(date.today() - date.fromisoformat(premiere)).days} jours")


if __name__ == "__main__":
    base = Path(__file__).parent
    FICHIER_ACHATS = str(base / FICHIER_ACHATS)
    FICHIER_PRIX = str(base / FICHIER_PRIX)
    main()
