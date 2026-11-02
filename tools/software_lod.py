"""Build low-detail CPU fallback from licensed, imported meshes. Not clinical detail."""
from pathlib import Path
import json,hashlib,trimesh,numpy as np
R=Path(__file__).resolve().parents[1];cat=json.load(open(R/'public/catalog.json'));out=R/'public/software';out.mkdir(exist_ok=True)
for p in cat['packs']:
 scene=trimesh.load(R/'public'/p['url'].lstrip('/'));data=[]
 for node in scene.graph.nodes_geometry:
  transform,key=scene.graph[node];m=scene.geometry[key].copy();m.apply_transform(transform)
  target=220 if cat['meshes'][node]['system']=='skeletal' else 100
  if len(m.faces)>target:m=m.simplify_quadric_decimation(face_count=target)
  data.append({'id':node,'v':np.round(m.vertices,5).ravel().tolist(),'f':m.faces.ravel().tolist()})
 dest=out/(p['id']+'.json');dest.write_text(json.dumps(data,separators=(',',':')))
 p['softwareUrl']='/software/'+p['id']+'.json'
 p['softwareBytes']=dest.stat().st_size
 p['softwareSha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
print('fallback bytes',sum(x.stat().st_size for x in out.iterdir()))
(R/'public/catalog.json').write_text(json.dumps(cat,separators=(',',':')))
