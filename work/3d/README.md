# Poilus d'Orient – maquette 3D interactive (prototype)

- `maquette-3d-autonome.html` : un seul fichier (≈3,4 Mo, Three.js embarqué). S'ouvre en double-cliquant, sans internet.
- `maquette-3d/` : même page en dossier (à servir par un serveur web).

Rotation / zoom / déplacement libres (souris ou doigts). Deux styles : « dessin » coloré (par défaut) et maquette blanche (bouton en bas). Étages : Tout, R+3, R+2, R+1, RDC (↑/↓).
En vue d'étage, les niveaux au-dessus disparaissent et l'étage est coupé à 1,25 m. Lots 1 et 2 cliquables au R+1 (mêmes fiches que la 360°).

## D'où vient la géométrie (work/)
1. **Murs** : dessus des murs détectés sur les 30 vues 360° de chaque niveau, reprojetés en vue de dessus avec la caméra
   en orbite déjà calée (`topview.py`, `fit_h.py`, `export_geo.py`). Le plan correspond donc exactement au rendu et aux polygones de la 360°.
2. **Échelle** : largeur du R+1 calée sur 13,00 m (plan) → longueur mesurée 18,15 m (plan : 17,90 « environ »),
   écart entre étages mesuré 2,74–2,82 m (coupe : 2,80). Surfaces des polygones de lots : 88 et 91 m² (habitables 83,69 / 84,95 + cloisons).
3. **Hauteurs** : coupe AA (RDC 0 / R+1 2,80 / R+2 5,60 / R+3 8,40 ; égout 7,95 ; faîtage 12,00 ; brisis 45°).
4. **Fenêtres** : interruptions des murs extérieurs des plans AVP recalés (`avp_fit.py`, `windows.py`) ; portes-fenêtres jardin,
   porte de garage et entrée d'après les façades. Lucarnes, balcons, terrasse et toitures végétalisées : placés d'après façades/coupe (simplifiés).

## Style et environnement (28/10/2026)
- Projet en style « dessin animé » aux matériaux des façades AVP : enduit gratté pierre grisée, panneaux Equitone Tectiva,
  couverture zinc quartz à joint debout, menuiseries gris moyen, corniche et balcons BA blancs, garde-corps en tôle décorative,
  porte de garage sectionnelle, terrasse bois, toitures végétalisées. Le bouton en bas bascule vers la maquette blanche.
- Environnement en blanc : emprises des bâtiments et rues © contributeurs OpenStreetMap (ODbL), hauteurs BD TOPO © IGN (Licence Ouverte),
  rayon ≈ 170 m (`work/osm/env.py`). Calage : axe OSM de la rue des Poilus d'Orient, projet centré sur la parcelle cadastrale IM 150
  (maison existante retirée), clôture sur la limite côté rue. Terrain supposé plat (le sol varie de 26 à 32 m NGF dans le secteur).
- Fond de carte activable (bouton « 🗺 ») : Plan IGN v2 ou photographie aérienne BD ORTHO © IGN (Géoplateforme, Licence Ouverte),
  zone de 400 × 400 m recalée dans le repère de la scène (`work/osm/basemap.py`), embarquée dans le fichier autonome.
  Google Maps n'est pas utilisé : ses conditions interdisent d'en extraire les tuiles hors de son API payante (clé requise).

## Rendu professionnel (28/10/2026)
- Style par défaut « Illustré » : éclairage d'environnement, ombres douces, occlusion ambiante (GTAO, désactivée sur mobile),
  ciel dégradé, traits discrets. Bouton « ◐ Style » : Illustré → Dessin → Maquette blanche.
- Modèle : murs, emprise et lots redressés à l'équerre (`work/regularize.py` : 84–96 % des arêtes d'équerre selon le niveau) ;
  contours des lots recalculés sur la face intérieure des murs 3D ; menuiseries fines avec meneaux et appuis BA blancs ;
  gouttière, faîtage et édicule en zinc ; lucarnes avec chapeau zinc ; clôture sur rue (muret enduit, chaperon, tôle décorative,
  piliers blancs, portillon), allées pavées, mur de fond avec chaperon ; mains courantes des balcons.

## Points de vue et rendus (29/10/2026)
- Bouton « 🎥 Points de vue » : 6 points de vue avec vol de caméra (façade sur rue à hauteur de piéton, vue aérienne,
  angle sud-ouest, côté jardin, plan masse, étage 1 / lots) + les 2 perspectives officielles ATJ (aérienne, piétonne) en grand.
  Les cadrages « rue » et « aérienne » reprennent ceux des perspectives officielles ; ensoleillement réglé par vue.
- Matériaux recalés sur les perspectives officielles : enduit blanc cassé, volume beige en saillie jusque dans la toiture,
  zinc clair, menuiseries gris foncé à deux vantaux, garde-corps et clôture en tôle blanche à motif géométrique, garage blanc.
- `rendus/` : captures 2560×1440 de chaque point de vue (base pour Magnific).
- Photoréalisme Magnific : `work/views/magnific.py` (API Freepik image-upscaler, prompts décrivant matériaux et voisinage réels).
  Nécessite la variable d'environnement FREEPIK_API_KEY ; les résultats (views/magnific/) remplacent automatiquement les rendus
  de base dans la galerie après `python p3d/build_3d.py out`. NON EXÉCUTÉ : aucune clé disponible.
- Rendus Magnific (29/10/2026, Image Editor de Magnific dans le navigateur, espace « TEST PROJECT SPACE ») : 6 points de vue,
  balcons et terrasses meublés (plantes en pot, oliviers, tables, chaises), voisinage réaliste. `rendus/magnific/` = versions retenues
  (intégrées à la galerie), `rendus/magnific/variantes/` = 2e variante de chaque vue, `rue_test_sans_mobilier*` = premier essai.
  Définition Magnific : 1376 × 768 px (pas d'upscale). La coupe « Étage 1 » meublée réinterprète une partie du cloisonnement : image d'ambiance.

## Interface (29/10/2026)
- En-tête (programme, adresse, consigne selon l'étage) · navigation « Maquette 3D / Galerie » · carte Étages avec la liste
  des appartements de l'étage (survol = mise en avant dans la 3D, clic = fiche) · bande de points de vue illustrée par les rendus
  (clic = vol de caméra, 📷 = rendu en grand) · outils : rotation, Réglages (style du rendu et fond de carte en choix explicites),
  plein écran, aide · galerie plein écran (6 rendus Magnific + 2 perspectives, flèches / clavier / balayage, « Voir en 3D »)
  · écran de chargement illustré · aide au premier lancement. Mise en page dédiée mobile.
- Visite guidée (bouton « ▶ Visite guidée », dans la fenêtre 3D, sans fenêtre surgissante) : pour chaque point de vue, vol de caméra
  vers la pose exacte de la capture envoyée à Magnific (recul CAPK = 1,194), révélation du rendu photoréaliste par balayage calé
  sur la 3D, légende, 5,5 s, effacement, vue suivante, en boucle. Barre : pastilles (aller à une vue), pause (ou Espace),
  suivant (ou →), quitter (ou Échap / toucher la maquette). Image en pleine largeur, champ de caméra ajusté au format d'écran.
