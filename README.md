# Outils de suivi PEA (ETF)

Deux petits scripts Python (bibliothèque standard uniquement, aucun paquet à installer)
pour suivre un PEA investi en ETF chez BoursoBank.

> Information générale et outil de suivi uniquement : ce n'est pas un conseil
> en investissement.

## Fichiers

| Fichier | Rôle |
|---|---|
| `pea_dashboard.py` | Tableau de bord : répartition actuelle vs objectifs, alerte de dérive |
| `pea_dca.py` | Journal DCA : historique des achats, PRU moyen, performance latente |
| `positions.csv` | Quantités détenues par ETF (à mettre à jour après chaque ordre) |
| `achats.csv` | Historique des ordres : `date,etf,quantite,prix_unitaire` |
| `prix.csv` | Cours unitaire actuel par ETF (partagé par les deux scripts) |

## Utilisation

```bash
python3 pea_dashboard.py   # répartition vs cible + alertes
python3 pea_dca.py         # PRU, performance, ancienneté du portefeuille
```

À adapter dans `pea_dashboard.py` : le dictionnaire `OBJECTIFS` (pondérations
cibles, ex. 90 % CW8 / 10 % PAEEM) et `SEUIL_ALERTE` (ex. 0.03 = 3 points).

## Workflow conseillé

1. Chaque mois : versement programmé sur le PEA, puis ordre manuel (achat ETF).
2. Ajouter la ligne dans `achats.csv` et mettre à jour `positions.csv`.
3. Mettre à jour les cours dans `prix.csv`, puis lancer les deux scripts.
