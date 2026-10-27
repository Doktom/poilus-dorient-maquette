# Poilus d'Orient – maquette 360° (INOVA / ATJ Graphics)

## Livrables
- `maquette-360-autonome.html` : un seul fichier, tout embarqué (≈18 Mo). S'ouvre en double-cliquant.
- `maquette-360/` : même page, images et PDF à part (à mettre en ligne sur un serveur web, ex. atj-app.com).

Compatible smartphone : en portrait, la vue est agrandie et recadrée sur le bâtiment à chaque image (centre calculé d'après
les polygones, `FOCUS` dans `build_poilus.py`), étages et commandes sous l'image, 1er appui = info-bulle, 2e = fiche ;
en paysage, commandes compactes et fiche sur deux colonnes.

5 niveaux (RDC, R+1, R+2, R+3, Toit), 30 vues par niveau, angle conservé quand on change d'étage (touches ↑/↓ ou boutons).
Polygones cliquables :
- **R+1** : lot 1 (T4, côté jardin, terrasse) et lot 2 (T4, côté rue, balcon) ;
- **R+2** : lot 3 (côté jardin) et lot 4 (côté rue), même disposition qu'au R+1 ;
- **R+3** (comble) : lot 5, tout l'étage sauf la cage d'escalier.
Survol : info-bulle ; clic : fiche (plan de vente, PDF, plan 3D, vues intérieures).

## Méthode des polygones (work/)
R+2 : `python f0level.py src/rp2 R+2 polygones-R2.json 3:T4:15 4:T4:285,295` (pièces = zones non blanches fermées, `segment_rooms`)
puis `python fitmask.py src/rp2 polygones-R2.json polys_rp2.json` (médiane 0,2 px).
R+3 : contour du lot 5 tracé en lignes droites dans `polygones-R3.json` (mur du fond, pignon, ligne du toit, cage d'escalier), d'après
`rooms3.py` (le toit en zinc sert aussi de limite) ; `ROOF=120 python fitmask.py src/rp3 polygones-R3.json polys_rp3.json` (médiane 1 px).
La baie de la terrasse du lot 5 est sous le plan de coupe : elle n'est pas dans le polygone (comme les balcons des autres lots).

R+1 :
1. `f0b.py` : contours des lots sur l'image 0 = bords intérieurs du dessus des murs (blanc pur, segmenté automatiquement).
   Lot 1 = pièces côté jardin, lot 2 = pièces côté rue ; cage d'escalier/palier exclus.
2. `fitmask.py src/r1 polygones-R1.json polys_r1.json` : modèle de caméra en orbite (`orbit.py`) ajusté directement sur le
   dessus des murs des 30 images (pas de tracé manuel). Résidu médian 0,2 px sur les vues où le dessus des murs est détectable ;
   vues 15–22 (côté jardin, dessus des murs peu contrastés) : pas mesurées automatiquement, contrôlées à l'œil au zoom (≈1–2 px).
3. `build_assets_poilus.py` (fiches, d'après `config_poilus.json`) puis `build_poilus.py <sortie>`.

Sources : `360etages_POILUS/<niveau>` (images 2560×1440), `plans_de_vente_PDF`, `Apppartements 3D/LOT n`.
Programme : R+1 lots 1–2, R+2 lots 3–4, R+3 lot 5, RDC box lots 6–10.
