"""Audit every previous Other mesh; explicit decision records, no broad re-import."""
from pathlib import Path
import json,re,hashlib,collections
from correct_nervous_catalog import subset
R=Path(__file__).resolve().parents[1];P=R/'public';C=R/'data/curation/taxonomy-decisions.json'
SOURCE='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_parts_list_e.txt'
REL='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/isa_inclusion_relation_list.txt'
def decision(n):
 if 'papillary muscle' in n:return 'cardiovascular','myocardium','thorax','Cardiac muscle is part of the heart, not skeletal musculature.'
 if 'venous arch' in n:return 'cardiovascular','vein','upper_limb','Named venous palmar arch.'
 if 'arteries' in n or 'palmar arch' in n or 'arterial arch' in n:return 'cardiovascular','artery',('thorax' if 'intercostal' in n else 'upper_limb' if 'palmar' in n or 'metacarpal' in n else 'lower_limb' if 'plantar' in n else None),'Arterial branch/set; ambiguous digital/perforating region remains null.'
 if any(w in n for w in ['hepatic','hepatovenous','biliary','cystic duct']):return 'digestive',('organ_segment' if 'segment' in n else 'bile_duct'),'abdomen','Liver segment or named biliary duct; hepatovenous segment is parenchymal territory.'
 if 'deferent duct' in n:return 'reproductive','duct',None,'Ductus deferens spans pelvic/inguinal/scrotal regions; no single region asserted.'
 if 'lacrimal' in n:return 'sensory',('gland' if 'gland' in n else 'fluid_space' if 'lake' in n else 'lacrimal_drainage'),'head_neck','Accessory lacrimal apparatus of eye.'
 if 'vitreous' in n:return 'sensory','vitreous_body','head_neck','Named vitreous body of eyeball.'
 if 'common tendinous ring' in n:return 'muscular','tendon','head_neck','Common tendinous origin for extraocular muscles; region eye, tissue tendon.'
 if 'retinaculum' in n:return 'muscular','deep_fascia',('upper_limb' if 'wrist' in n else None),'Retinaculum is a fascial restraint at wrist; substring matching is not an anatomical classification.'
 if 'interosseous membrane' in n:return 'skeletal','syndesmosis',('upper_limb' if 'forearm' in n else 'lower_limb'),'Fibrous connection of paired long bones.'
 if any(w in n for w in ['iliotibial','linea alba','tendinous arch','raphe']):return 'muscular','fibrous_attachment',('lower_limb' if 'iliotibial' in n else 'abdomen' if 'linea alba' in n else 'pelvis' if 'levator ani' in n else 'head_neck'),'Aponeurotic/fascial attachment; functional system and histological type are recorded separately.'
 if any(w in n for w in ['levatores','interossei','lumbricals','trapezius','intertransversarii','interspinales']):return 'muscular','skeletal_muscle_group',('upper_limb' if 'hand' in n else 'head_neck' if 'cervic' in n else 'thorax' if 'costarum' in n else 'abdomen' if 'lumborum' in n else None),'Named skeletal muscle/group; source grouping and bilateral ambiguity preserved.'
 if any(w in n for w in ['gingiva','appendix','taenia','ileocecal','lip']):return 'digestive',('mucosa' if 'gingiva' in n else 'muscle_band' if 'taenia' in n else 'organ_part'),('head_neck' if 'gingiva' in n or n=='lip' else 'abdomen'),'Oral or intestinal structure; no artificial decomposition of source aggregate.'
 if 'conus elasticus' in n or 'thyrohyoid membrane' in n:return 'respiratory','fibrous_membrane','head_neck','Fibroelastic support of larynx.'
 if 'xiphoid' in n or 'sternum' in n:return 'skeletal','bone_part','thorax','Named part of sternum.'
 return None

def main():
 c=json.loads((P/'catalog.json').read_text());by={s['id']:s for s in c['structures']}
 if not C.exists():
  rows=[]
  for m in c['meshes'].values():
   s=by[m['structureId']];n=s['canonicalName'];target=m['system']=='other' or (m['system']=='sensory' and ('retinaculum' in n or 'interosseous membrane' in n))
   if not target:continue
   d=decision(n)
   rows.append({'meshId':m['id'],'structureId':s['id'],'sourceName':n,'previousSystem':m['system'],'system':d[0] if d else 'other','type':d[1] if d else None,'region':d[2] if d else None,'sourceParents':s['parentStructure'],'reason':d[3] if d else 'Unresolved; manual review required.','references':[SOURCE,REL],'status':'DATA_VERIFIED' if d else 'NOT_YET_VALIDATED','medicalStatus':'MEDICAL_REVIEW_PENDING','regionStatus':'EDITORIAL_REVIEW_PENDING' if d and d[2] else 'NOT_YET_VALIDATED'})
  C.write_text(json.dumps(rows,indent=2)+'\n')
 rows=json.loads(C.read_text());changes={x['meshId']:x for x in rows};newpacks=[]
 for pack in list(c['packs']):
  groups=collections.defaultdict(set)
  for i in pack['meshIds']:groups[changes.get(i,{}).get('system',c['meshes'][i]['system'])].add(i)
  if len(groups)==1 and next(iter(groups))==pack['system']:continue
  raw=(P/pack['url'].lstrip('/')).read_bytes();soft=json.loads((P/pack['softwareUrl'].lstrip('/')).read_text());c['packs'].remove(pack)
  for system,ids in sorted(groups.items()):
   pid=pack['id'] if system==pack['system'] else 'curated-'+system+'-'+pack['id'];p={**pack,'id':pid,'system':system,'url':'/packs/'+pid+'.glb','softwareUrl':'/software/'+pid+'.json'}
   blob=subset(raw,ids,system);sb=json.dumps([v for v in soft if v['id'] in ids],separators=(',',':')).encode();(P/p['url'].lstrip('/')).write_bytes(blob);(P/p['softwareUrl'].lstrip('/')).write_bytes(sb)
   p.update(meshIds=sorted(ids),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),softwareBytes=len(sb),softwareSha256=hashlib.sha256(sb).hexdigest(),triangles=sum(c['meshes'][i]['triangles'] for i in ids));newpacks.append(p)
   for i in ids:c['meshes'][i].update(system=system,packId=pid)
  if pack['system'] not in groups:
   (P/pack['url'].lstrip('/')).unlink();(P/pack['softwareUrl'].lstrip('/')).unlink()
 c['packs']+=newpacks
 # Corrections also cover named grouping concepts using the SAME explicit tissue rules.
 for s in c['structures']:
  d=decision(s['canonicalName']) if s['system']=='other' or any(w in s['canonicalName'] for w in ['retinaculum','interosseous membrane']) else None
  if d:s.update(system=d[0],type=d[1],region=d[2],classificationStatus='source-ID correction; expert review pending',classificationReferences=[SOURCE,REL])
  s.setdefault('canonicalId',s['id']);s.setdefault('sourceId',s['id']);s.setdefault('subsystem',None);s.setdefault('type',None);s.setdefault('validationStatus','MEDICAL_REVIEW_PENDING')
  s['translationStatusByLanguage']={'en':'SOURCE_MATCHED' if s.get('englishName') else 'MISSING',**{lang:'AI_DRAFT' if s.get(field) else 'MISSING' for lang,field in [('fr','frenchName'),('ar','arabicName'),('la','latinName')]}}
  s['metadataCompleteness']={f:bool(s.get(f)) for f in ['description','function','innervation','vascularization','clinicalNotes']}
 c['version']='bp3d4-'+hashlib.sha256(json.dumps({'packs':c['packs'],'structures':c['structures']},sort_keys=True).encode()).hexdigest()[:12];(P/'catalog.json').write_text(json.dumps(c,separators=(',',':'),ensure_ascii=False))
 print('Decisions:',len(rows),'Other remaining:',sum(m['system']=='other' for m in c['meshes'].values()),'packs:',len(c['packs']))
if __name__=='__main__':main()
