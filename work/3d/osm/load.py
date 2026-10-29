import xml.etree.ElementTree as ET, json, numpy as np
LAT0, LON0 = 49.1849490, -0.3837301
KX = 111320 * np.cos(np.radians(LAT0)); KY = 110574
def xy(lat, lon): return ((lon - LON0) * KX, (lat - LAT0) * KY)   # x est, y nord (m)
def osm():
    r = ET.parse('map.osm').getroot()
    nodes = {n.get('id'): xy(float(n.get('lat')), float(n.get('lon'))) for n in r.findall('node')}
    out = []
    for w in r.findall('way'):
        t = {k.get('k'): k.get('v') for k in w.findall('tag')}
        pts = [nodes[n.get('ref')] for n in w.findall('nd') if n.get('ref') in nodes]
        out.append(dict(id=w.get('id'), tags=t, pts=np.array(pts)))
    rel = []
    for rl in r.findall('relation'):
        t = {k.get('k'): k.get('v') for k in rl.findall('tag')}
        if 'building' in t:
            rel.append(dict(id=rl.get('id'), tags=t, outer=[m.get('ref') for m in rl.findall('member') if m.get('role') == 'outer' and m.get('type') == 'way']))
    return out, rel
def bdtopo():
    d = json.load(open('bdtopo.json', encoding='utf8')); out = []
    for f in d['features']:
        g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
        for p in polys:
            out.append(dict(h=f['properties'].get('hauteur'), sol=f['properties'].get('altitude_minimale_sol'),
                            pts=np.array([xy(c[1], c[0]) for c in p[0]])))
    return out
