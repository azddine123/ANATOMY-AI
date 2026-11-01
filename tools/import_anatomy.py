"""Reproducible BodyParts3D OBJ -> glTF pack + FMA catalogue pipeline."""
from pathlib import Path
import csv,collections,json,zipfile,io,hashlib,time
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'data/source'; OUT=ROOT/'public'
def rows(n):return list(csv.DictReader(open(SRC/n),delimiter='\t'))
def main():
 start=time.time(); parts=rows('isa_parts_list_e.txt'); names={x['concept id']:x['en'] for x in parts}; parents=collections.defaultdict(list);children=collections.defaultdict(list)
 for x in rows('isa_inclusion_relation_list.txt'):
  parents[x['child id']].append(x['parent id']);children[x['parent id']].append(x['child id'])
 elements=collections.defaultdict(list); reverse=collections.defaultdict(list)
 for x in rows('isa_element_parts.txt'):
  elements[x['concept id']].append(x['element file id']); reverse[x['element file id']].append(x['concept id'])
 def ancestors(i,seen=None):
  seen=set() if seen is None else seen
  for p in parents[i]:
   if p not in seen:seen.add(p);ancestors(p,seen)
  return seen
 def system(i):
  n=names[i].lower();anc=' '.join(names.get(x,'') for x in ancestors(i)).lower();s=n+' '+anc
  if 'muscle organ' in s or 'tendon' in n or 'fascia' in n:return 'muscular'
  if any(w in s for w in ['vein','artery','cardiac','heart','vascular tree']):return 'cardiovascular'
  if any(w in s for w in ['nerve','brain','spinal cord','cerebell','cerebr','ganglion']):return 'nervous'
  if any(w in s for w in ['lymph','spleen','thymus']):return 'lymphatic'
  if any(w in s for w in ['bone organ','bone of','cartilage','joint','ligament','skeleton','tooth']):return 'skeletal'
  if any(w in s for w in ['lung','bronch','trache','larynx','nasal','respiratory','pleura']):return 'respiratory'
  if any(w in s for w in ['kidney','ureter','urinary','urethra']):return 'urinary'
  if any(w in s for w in ['testis','prostat','penis','seminal','epididym','ductus deferens','scrotum','ovary','uterus']):return 'reproductive'
  if any(w in s for w in ['thyroid','adrenal','pituitary','pineal']):return 'endocrine'
  if any(w in s for w in ['skin','nail','mammary']):return 'integumentary'
  if any(w in s for w in ['eye','retina','lens','cochlea','ear','ossicle','tympan']):return 'sensory'
  return 'digestive' if any(w in s for w in ['liver','stomach','intestin','colon','esophag','pancrea','duoden','gallbladder','rectum','tongue','pharynx','salivary','digestive','ileum','cecum','jejunum','anal']) else 'other'
 colors={'skeletal':'ddd2b3','muscular':'ac514e','cardiovascular':'c84458','nervous':'e4b952','respiratory':'bf8896','digestive':'b8785e','urinary':'ae666a','lymphatic':'64ab8c','endocrine':'ad8abd','reproductive':'c98b94','integumentary':'cdb292','sensory':'70b7b9','other':'aea5b0'}
 z=zipfile.ZipFile(SRC/'isa_BP3D_4.0_obj_99.zip'); files={Path(n).stem:n for n in z.namelist() if n.endswith('.obj')};print('meshes',len(files),flush=True)
 packs=collections.defaultdict(list);meta={};allbounds=[]
 for j,(fid,path) in enumerate(sorted(files.items())):
  candidates=reverse[fid]
  if not candidates:continue
  cid=min(candidates,key=lambda i:(len(elements[i]),-len(ancestors(i)),i));sys=system(cid)
  mesh=trimesh.load(io.BytesIO(z.read(path)),file_type='obj',force='mesh',process=True)
  mesh.update_faces(mesh.nondegenerate_faces());mesh.remove_unreferenced_vertices()
  if not len(mesh.faces) or not np.isfinite(mesh.vertices).all():raise ValueError(fid)
  # BP3D uses millimetres, Z superior. Preserve shared origin; Y-up glTF.
  v=mesh.vertices.copy();mesh.vertices=np.column_stack([v[:,0],v[:,2],-v[:,1]])*.001
  if len(mesh.faces)>7000:mesh=mesh.simplify_quadric_decimation(face_count=7000)
  mesh.visual=trimesh.visual.ColorVisuals(mesh=mesh,vertex_colors=[*bytes.fromhex(colors[sys]),255])
  mesh.metadata={'sourceId':fid,'structureId':cid,'system':sys}
  b=mesh.bounds.tolist();allbounds.append(b)
  meta[fid]={'id':fid,'structureId':cid,'system':sys,'triangles':len(mesh.faces),'vertices':len(mesh.vertices),'bounds':b,'watertight':bool(mesh.is_watertight),'sourceSha256':hashlib.sha256(z.read(path)).hexdigest()}
  packs[sys].append((fid,mesh))
  if j%250==0:print('processed',j,flush=True)
 packout=[]
 for sys,items in packs.items():
  for k in range(0,len(items),75):
   scene=trimesh.Scene()
   group=items[k:k+75];pid=f'{sys}-{k//75:02}'
   for fid,m in group:scene.add_geometry(m,node_name=fid,geom_name=fid)
   payload=scene.export(file_type='glb');dest=OUT/'packs'/f'{pid}.glb';dest.write_bytes(payload)
   packout.append({'id':pid,'system':sys,'url':f'/packs/{pid}.glb','bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'meshIds':[i[0] for i in group],'triangles':sum(len(i[1].faces) for i in group)})
   for fid,_ in group:meta[fid]['packId']=pid
 structures=[]
 for p in parts:
  i=p['concept id'];assets=[f for f in elements[i] if f in meta]
  if not assets:continue
  structures.append({'id':i,'canonicalName':p['en'],'englishName':p['en'],'frenchName':None,'arabicName':None,'latinName':None,'synonyms':[],'system':system(i),'region':None,'parentStructure':parents[i],'children':children[i],'relatedStructures':[],'description':None,'function':None,'origin':None,'insertion':None,'innervation':None,'vascularization':None,'lymphaticDrainage':None,'clinicalNotes':None,'gender':None,'modelAssetIds':assets,'source':'BodyParts3D 4.0','sourceReferences':['https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html'],'classificationStatus':'rule-derived; review required'})
 catalog={'version':'2026.09.13.1','sourceVersion':'BodyParts3D 4.0 reduced 99%','license':'CC-BY-4.0','structures':structures,'meshes':meta,'packs':packout,'bounds':[np.min(np.array(allbounds)[:,0,:],axis=0).tolist(),np.max(np.array(allbounds)[:,1,:],axis=0).tolist()]}
 (OUT/'catalog.json').write_text(json.dumps(catalog,separators=(',',':')))
 report={'structures':len(structures),'meshes':len(meta),'packs':len(packout),'bytes':sum(x['bytes'] for x in packout),'triangles':sum(x['triangles'] for x in packout),'seconds':round(time.time()-start,1),'systems':{s:len(v) for s,v in packs.items()},'bounds':catalog['bounds']}
 (ROOT/'docs/import-report.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
if __name__=='__main__':main()
