"""Environnement OSM (rues, batiments) + hauteurs BD TOPO, dans le repere de la scene three.js (X, Z) -> env.json
Calage : axe de la rue des Poilus d'Orient (OSM) ; facade rue a 15,25 m de l'axe (comme la scene) ; centre du projet au droit du point d'adresse n°4."""
import json, numpy as np
from shapely.geometry import Polygon, LineString, Point, box as sbox
from shapely.ops import unary_union
from shapely import affinity
from load import osm, bdtopo
ways, rel = osm(); bd = bdtopo()
street = [w for w in ways if w['tags'].get('name') == "Rue des Poilus d'Orient" and 'highway' in w['tags']]
line = unary_union([LineString(w['pts']) for w in street if len(w['pts']) > 1])
A = Point(0, 0)                                     # point d'adresse n°4
foot = line.interpolate(line.project(A))
a = line.interpolate(max(0, line.project(A) - 8)); b = line.interpolate(line.project(A) + 8)
d = np.array([b.x - a.x, b.y - a.y]); d /= np.linalg.norm(d)
nrm = np.array([-d[1], d[0]])
if np.dot(nrm, [A.x - foot.x, A.y - foot.y]) < 0: nrm = -nrm          # normale vers le projet (NO)
Zd = -nrm                                                             # +Z scene = vers la rue
Xd = np.array([-Zd[1], Zd[0]])                                        # +X = haut x Z
C = np.array([foot.x, foot.y]) + nrm * 15.25
# recalage sur la parcelle cadastrale IM 150 (maison existante) : centree dans la largeur, cloture sur la limite rue
C = C + Xd * (-7.3) + Zd * (1.8)
print('rue (est,nord)', d.round(3), 'normale', nrm.round(3), '+X scene ->', Xd.round(3), 'centre', C.round(1))
def S(p): p = np.asarray(p) - C; return np.c_[p @ Xd, p @ Zd]
PLOT = Polygon([(-11.6, -21.6), (11.6, -21.6), (11.6, 9.3), (-11.6, 9.3)])   # parcelle du projet (repere scene)
R = 170
bdp = [(Polygon(S(b['pts'])).buffer(0), b['h']) for b in bd if len(b['pts']) > 3]
out = dict(buildings=[], roads=[], removed=[])
for w in ways:
    t = w['tags']
    if 'building' not in t or len(w['pts']) < 4: continue
    P = Polygon(S(w['pts'])).buffer(0)
    if P.is_empty or P.centroid.distance(Point(0, 0)) > R: continue
    if P.intersection(PLOT).area > 0.3 * P.area:
        out['removed'].append(dict(id=w['id'], area=round(P.area, 1), tags={k: t[k] for k in t if k in ('building', 'addr:housenumber')})); continue
    best, h = 0, None
    for Q, hq in bdp:
        if hq is None or not Q.intersects(P): continue
        o = Q.intersection(P).area
        if o > best: best, h = o, hq
    src = 'bdtopo'
    if h is None or best < 0.3 * P.area:
        lv = t.get('building:levels'); src = 'osm' if lv else 'defaut'
        h = (float(lv) * 3 + 1.5) if lv and lv.replace('.', '').isdigit() else (3.0 if t['building'] in ('garage', 'garages', 'shed', 'roof') else 7.0)
    geo = P if P.geom_type == 'Polygon' else max(P.geoms, key=lambda g: g.area)
    out['buildings'].append(dict(pts=np.round(np.array(geo.exterior.coords)[:-1], 2).tolist(),
                                 holes=[np.round(np.array(i.coords)[:-1], 2).tolist() for i in geo.interiors], h=round(float(h), 1), src=src))
W = {'secondary': 11, 'secondary_link': 7, 'tertiary': 9, 'tertiary_link': 6, 'residential': 7, 'unclassified': 6, 'living_street': 5,
     'service': 3.5, 'pedestrian': 4, 'cycleway': 2, 'footway': 1.8, 'path': 1.5, 'steps': 1.8}
for w in ways:
    t = w['tags']; k = t.get('highway')
    if k not in W or len(w['pts']) < 2 or t.get('area') == 'yes': continue
    L = LineString(S(w['pts']))
    if L.distance(Point(0, 0)) > R: continue
    out['roads'].append(dict(kind='voie' if W[k] >= 5 else ('desserte' if k == 'service' else 'pieton'), poly=None, line=L, w=W[k], name=t.get('name')))
# rubans fusionnes par categorie, decoupes en dehors de la parcelle du projet
clip = Point(0, 0).buffer(R + 20)
res = []
for kind in ('voie', 'desserte', 'pieton'):
    U = unary_union([r['line'].buffer(r['w'] / 2, cap_style='flat' if kind != 'voie' else 'round') for r in out['roads'] if r['kind'] == kind]).intersection(clip).difference(PLOT)
    geoms = [U] if U.geom_type == 'Polygon' else list(getattr(U, 'geoms', []))
    for g in geoms:
        g = g.simplify(0.15)
        if g.area < 1 or g.geom_type != 'Polygon': continue
        res.append(dict(kind=kind, pts=np.round(np.array(g.exterior.coords)[:-1], 2).tolist(), holes=[np.round(np.array(i.coords)[:-1], 2).tolist() for i in g.interiors]))
# axe de la rue (pour le nom au sol)
sl = LineString(S(np.array(line.coords) if line.geom_type == 'LineString' else np.vstack([np.array(g.coords) for g in line.geoms])))
pt = sl.interpolate(sl.project(Point(0, 15.25))); pt2 = sl.interpolate(sl.project(Point(0, 15.25)) + 1)
print('axe de rue a Z =', round(pt.y, 2))
out = dict(buildings=out['buildings'], roads=res, removed=out['removed'],
           label=dict(x=round(pt.x, 2), z=round(pt.y, 2), ang=round(float(np.arctan2(pt2.y - pt.y, pt2.x - pt.x)), 4)),
           calage=dict(centre_local_m=C.round(2).tolist(), axe_X_est_nord=Xd.round(4).tolist(), ref_latlon=[49.1849490, -0.3837301]))
json.dump(out, open('env.json', 'w'))
import collections
print('batiments', len(out['buildings']), collections.Counter(b['src'] for b in out['buildings']), 'retires', out['removed'])
print('routes', len(res), collections.Counter(r['kind'] for r in res), 'etiquette', out['label'])
hs = [b['h'] for b in out['buildings']]; print('hauteurs min/med/max', min(hs), np.median(hs), max(hs))
