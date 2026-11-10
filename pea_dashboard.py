#!/usr/bin/env python3
"""Tableau de bord PEA : suivi de la répartition ETF vs objectifs."""

import csv
import sys
from pathlib import Path

# --- Configuration (à adapter) ---
OBJECTIFS = {  # pondération cible par ETF
    "CW8": 0.90,    # Amundi MSCI World (capitalisant)
    "PAEEM": 0.10,  # Amundi MSCI Emerging Markets
}
SEUIL_ALERTE = 0.03  # alerte si écart > 3 points de pourcentage
FICHIER_POSITIONS = "positions.csv"   # etf,quantite
FICHIER_PRIX = "prix.csv"             # etf,prix_unitaire


def lire_csv(chemin, colonnes):
    donnees = {}
    with open(chemin, newline="", encoding="utf-8") as f:
        for ligne in csv.DictReader(f):
            cle = ligne[colonnes[0]].strip()
            donnees[cle] = ligne[colonnes[1]].strip()
    return donnees


def main():
    positions = lire_csv(FICHIER_POSITIONS, ("etf", "quantite"))
    prix = lire_csv(FICHIER_PRIX, ("etf", "prix"))

    lignes = []
    total = 0.0
    for etf, qte in positions.items():
        if etf not in prix:
            sys.exit(f"Erreur : pas de prix pour {etf} dans {FICHIER_PRIX}")
        qte = float(qte.replace(",", "."))
        pu = float(prix[etf].replace(",", "."))
        valeur = qte * pu
        total += valeur
        lignes.append({"etf": etf, "qte": qte, "pu": pu, "valeur": valeur})

    if total <= 0:
        sys.exit("Erreur : portefeuille vide.")

    print(f"Valeur totale du PEA : {total:,.2f} €\n")
    print(f"{'ETF':<10}{'Qté':>8}{'Prix':>10}{'Valeur':>14}{'Poids':>8}{'Cible':>8}{'Écart':>8}")
    print("-" * 66)

    alertes = []
    for l in lignes:
        poids = l["valeur"] / total
        cible = OBJECTIFS.get(l["etf"], 0.0)
        ecart = poids - cible
        print(f"{l['etf']:<10}{l['qte']:>8.4f}{l['pu']:>10.2f}{l['valeur']:>14,.2f}"
              f"{poids:>7.1%}{cible:>7.0%}{ecart:>+8.1%}")
        if abs(ecart) > SEUIL_ALERTE:
            alertes.append((l["etf"], poids, cible, ecart))

    etfs_connus = set(positions) | set(OBJECTIFS)
    for etf in etfs_connus - set(positions):
        cible = OBJECTIFS.get(etf, 0.0)
        if cible > 0 and cible > SEUIL_ALERTE:
            alertes.append((etf, 0.0, cible, -cible))

    print()
    if alertes:
        print(f"⚠ ALERTE : dérive > {SEUIL_ALERTE:.0%} détectée :")
        for etf, poids, cible, ecart in alertes:
            if ecart < 0:
                manque = (cible - poids) * total
                print(f"  - {etf} sous-pondéré de {abs(ecart):.1%} "
                      f"→ acheter environ {manque:,.2f} € (privilégier l'achat "
                      f"plutôt que la vente)")
            else:
                print(f"  - {etf} surpondéré de {ecart:.1%} "
                      f"→ envisager de réduire de {(ecart * total):,.2f} €")
    else:
        print("✓ Répartition conforme aux objectifs (dans la marge d'alerte).")


if __name__ == "__main__":
    base = Path(__file__).parent
    FICHIER_POSITIONS = str(base / FICHIER_POSITIONS)
    FICHIER_PRIX = str(base / FICHIER_PRIX)
    main()
