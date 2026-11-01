"""Deterministic data-health and duplicate candidates; not a medical completeness score."""
from pathlib import Path
import json,hashlib,collections,re,struct,sys
R=Path(__file__).resolve().parents[1];P=R/'public'
def main():
 c=json.loads((P/'catalog.json').read_text());ss=c['structures'];by={s['id']:s for s in ss};meshes=c['meshes'];errors=[];warnings=[];membership=collections.Counter();names=collections.defaultdict(list);assetsets=collections.defaultdict(list);geometries=collections.defaultdict(list)
 for s in ss:
  names[re.sub(r'[^a-z0-9]','',s['canonicalName'].lower())].append(s['id'])
  if s['modelAssetIds']:assetsets[tuple(sorted(s['modelAssetIds']))].append(s['id'])
  for m in s['modelAssetIds']:
   if m not in meshes:errors.append('Missing mesh '+s['id']+' '+m)
  for i in s['parentStructure']+s['children']:
   if i not in by:warnings.append({'type':'unresolved_relation_target','structure':s['id'],'target':i})
 if len(by)!=len(ss):errors.append('Duplicate stable structure IDs')
 for p in c['packs']:
  for key,hkey in [('url','sha256'),('softwareUrl','softwareSha256')]:
   path=P/p[key].lstrip('/')
   if not path.is_file():errors.append('Missing pack '+str(path));continue
   if hashlib.sha256(path.read_bytes()).hexdigest()!=p[hkey]:errors.append('Checksum mismatch '+str(path))
  raw=(P/p['url'].lstrip('/')).read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:];glbids=[]
  for node in g['nodes']:
   if 'mesh' not in node:continue
   glbids.append(node['name']);h=hashlib.sha256()
   for prim in g['meshes'][node['mesh']]['primitives']:
    for ai in [prim['attributes']['POSITION'],prim['indices']]:
     a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];size={5126:4,5125:4,5123:2,5121:1}[a['componentType']]*(3 if a['type']=='VEC3' else 1);off=v.get('byteOffset',0)+a.get('byteOffset',0)
     for i in range(a['count']):h.update(binary[off+i*v.get('byteStride',size):off+i*v.get('byteStride',size)+size])
   geometries[h.hexdigest()].append(node['name'])
  if sorted(glbids)!=sorted(p['meshIds']):errors.append('GLB membership '+p['id'])
  software=json.loads((P/p['softwareUrl'].lstrip('/')).read_text())
  if sorted(m['id'] for m in software)!=sorted(p['meshIds']):errors.append('CPU membership '+p['id'])
  for mid in p['meshIds']:
   membership[mid]+=1;m=meshes[mid]
   if m['packId']!=p['id'] or m['system']!=p['system']:errors.append('Pack classification '+mid)
   if by[m['structureId']]['system']!=m['system']:warnings.append({'type':'primary_concept_system_mismatch','mesh':mid,'structure':m['structureId'],'meshSystem':m['system'],'conceptSystem':by[m['structureId']]['system']})
 for mid in meshes:
  if membership[mid]!=1:errors.append('Mesh pack membership '+mid)
 duplicates={'normalizedNames':[{'name':n,'ids':ids} for n,ids in names.items() if len(ids)>1],'sharedAssetSets':[{'meshIds':list(ids),'structureIds':sids} for ids,sids in assetsets.items() if len(sids)>1],'identicalGeometry':[{'sha256':h,'meshIds':ids} for h,ids in geometries.items() if len(ids)>1]}
 fields=['englishName','frenchName','arabicName','latinName','description','function','innervation','vascularization','clinicalNotes','source','system','region','type','parentStructure','modelAssetIds']
 counts={f:sum(not s.get(f) for s in ss) for f in fields};systems={sys:{'meshes':sum(m['system']==sys for m in meshes.values()),'concepts':sum(s['system']==sys for s in ss),'missingDescription':sum(s['system']==sys and not s['description'] for s in ss)} for sys in sorted(set(s['system'] for s in ss))}
 report=dict(catalogVersion=c['version'],totalConcepts=len(ss),totalMeshes=len(meshes),packs=len(c['packs']),otherMeshes=sum(m['system']=='other' for m in meshes.values()),otherConcepts=sum(s['system']=='other' for s in ss),missing=counts,systems=systems,duplicateCandidates=duplicates,errors=errors,warnings=warnings,validationStatus='MEDICAL_REVIEW_PENDING',anatomicalCoveragePercent=None)
 from m2_reports import generate
 generate(c,report)
 (R/'docs/data-health.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
 out=['# Anatomy data health','',f"Generated from `{c['version']}` by `npm run audit:data`. Counts describe catalogue fields, never medical coverage.",'',f"Concepts: **{len(ss)}** · meshes: **{len(meshes)}** · packs: **{len(c['packs'])}** · Other meshes: **{report['otherMeshes']}** · Other concepts: **{report['otherConcepts']}**.",'','| Missing field | Concepts |','|---|---:|']+[f'| {f} | {n} |' for f,n in counts.items()]
 out+=['','## Integrity',f"Blocking file/ID/hash/membership errors: **{len(errors)}**. Semantic/relation warnings: **{len(warnings)}**. See `data-health.json` for every item.",'','## Duplicate candidates']+[f'- {k}: {len(v)} groups' for k,v in duplicates.items()]+['','Shared geometry sets often reflect IS-A ancestors or aggregate concepts; identical names may denote source fragments. Do not merge these automatically. Left/right counterparts are not duplicates. This audit detects exact indexed-geometry equality, not arbitrary remeshing or English/Latin semantic equivalence.','', 'Missing parents can be valid roots or absent imported ancestors; they are reported for review, not silently invented. All French/Arabic/Latin entries remain draft unless evidence exists. No numerical medical-readiness score is published.','', '## Meshes by system','| System | Meshes | Concepts |','|---|---:|---:|']+[f"| {s} | {v['meshes']} | {v['concepts']} |" for s,v in systems.items()]
 (R/'docs/DATA_HEALTH.md').write_text('\n'.join(out)+'\n');print(json.dumps({'errors':len(errors),'warnings':len(warnings),'duplicates':{k:len(v) for k,v in duplicates.items()},'missing':counts}));return bool(errors)
if __name__=='__main__':sys.exit(main())
