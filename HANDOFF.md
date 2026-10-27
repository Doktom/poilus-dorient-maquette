# HANDOFF – Poilus d'Orient

*V1 : 28/10/2026 (tag `v1`) · v2 : 28/10/2026 (tag `v2`, branche `main`).*

## Sources (hors dépôt – OneDrive de Tom)
Racine : `C:\Users\tom\OneDrive\Documents\ATJ\ATJ GRAPHICS\PROJETS CLIENTS\2026\INOVA - Poilus d'Orient\` (chemin dans `work/config_poilus.json` > `base`)
- `360etages_POILUS\{RDC,R+1,R+2,R+3,TOITURE}\` : 30 JPG 2560×1440 par niveau, mêmes angles d'un niveau à l'autre
- `plans_de_vente_PDF\Plans de vente CEPIA - RUE DES POILUS-N.pdf` (N = 1…10)
- `Apppartements 3D\LOT n\` : plan 3D + vues intérieures (versions `_up` = finales)
- `plans_poilus d'orient\` : plans architecte AVP (PDF/DWG), non utilisés pour la V1

## Programme
| Niveau | Lots | Polygones V1 |
|---|---|---|
| RDC | box 6–10 | non |
| R+1 | 1 (T4, jardin), 2 (T4, rue) | oui |
| R+2 | 3 (T4, jardin), 4 (T4, rue) | oui |
| R+3 (comble) | 5 (T4) | oui |
Les rendus 3D ne suivent pas toujours les plans de vente (R+1/R+2 : pas de bloc salles de bains côté droit ; R+3 : plateau ouvert) → polygones calés sur les rendus.

## Méthode (dans `work/`)
1. Images web : `python export_frames.py "<base>/360etages_POILUS/R+1" final/frames r1` (préfixes : rdc, r1, rp2, rp3, toiture)
2. Contours image 0 : le dessus des murs coupés est blanc pur (`wall.py`). Pièces = zones non blanches fermées (`lotpoly.segment_rooms`) :
   `python f0level.py <images> R+2 polygones-R2.json 3:T4:15 4:T4:285,295` (numéros de pièces : `rooms2.py`).
   R+3 (comble) : le toit zinc limite aussi les pièces (`rooms3.py … 120`), contour redressé à la main en lignes droites.
3. Report sur les 30 images : `python fitmask.py <images> polygones-RX.json polys_X.json` (`ROOF=120` pour le R+3).
   Modèle de caméra en orbite (`orbit.py`) ajusté sur les bords du dessus des murs de toutes les images. Médianes : R+1/R+2 0,2 px, R+3 1 px.
   Vues 15–22 (côté jardin) : dessus des murs peu contrastés, non mesurés automatiquement ; contrôlés à l'œil (≈1–2 px).
   Contrôle : `zoomchk.py`, `drawf.py`.
4. Fiches : `python build_assets_poilus.py` (→ `site/`), maquette : `python build_poilus.py <sortie>` (→ `<sortie>/maquette-360/` + `maquette-360-autonome.html`), puis copier `maquette-360/` dans `docs/`.

## Page (`template_poilus.html`)
Canvas (images) + SVG (polygones, viewBox 2560×1440). Sélecteur d'étages (angle conservé). Info-bulle au survol, fiche au clic
(plan de vente image + PDF, plan 3D, vues). Smartphone portrait : vue ×2,2 recadrée sur le bâtiment (`FOCUS`, centre des polygones par image).

## v2 (28/10/2026, fusionnée dans `main`, tag `v2`)
- **Liste des lots** (bouton « ☰ Lots ») : filtres par étage et « Disponibles », clic = bon étage + meilleur angle (image où le lot
  est le plus visible) + lot mis en évidence ; bouton « Fiche ».
- **Statuts** : `statut` par lot dans `config_poilus.json` (`disponible` | `reserve` | `vendu`, défaut disponible — aucun statut réel
  fourni par INOVA). Légende : bascule couleurs « Typo / Statut ». Statut affiché dans l'info-bulle, la fiche et la liste.
- **Rotation** : images WebP (−28 % : dossier 36→26 Mo, autonome 22→17 Mo), chargement par proximité de l'angle courant,
  inertie au lâcher (≈6 images max), fondu entre étages.
- **Liens directs** : `#lot-3` ouvre la fiche (bon étage + angle), `#etage-rp2` ouvre un étage ; l'adresse suit la navigation.
  Bouton « Partager » (partage natif sur mobile, sinon copie du lien). Bouton plein écran (masqué si non supporté, ex. iPhone).
- **Zoom dans la fiche** : molette, double-clic / double-appui, pincement, glisser, boutons + / −.
- **Visite guidée** : enchaîne les lots (étage, angle, info-bulle 3,8 s) — mode vitrine pour écran en espace de vente.

## Publication (GitHub Pages, dépôt public Doktom/poilus-dorient-maquette)
Pages sert la branche `gh-pages` = contenu de `docs/` de `main` (actuellement v2). La V1 reste récupérable par le tag `v1`.
- Site : https://doktom.github.io/poilus-dorient-maquette/ (ex. `…/#lot-3`)
- Pour tester une branche avant fusion : publier son `docs/` dans `gh-pages/test/` (`git archive <branche> docs`), lien `…/test/`.
Mise à jour : dans un clone de `gh-pages`, remplacer le contenu par `git archive main docs`, commit, push.
