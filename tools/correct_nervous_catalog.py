"""Targeted, reproducible classification correction; never synthesizes anatomy.
Source IDs/names: BodyParts3D IS-A tables. CNS reference: NCI SEER CNS module.
No assertion of expert anatomical validation or full coverage.
"""
from pathlib import Path
import json,struct,copy,hashlib
R=Path(__file__).resolve().parents[1];P=R/'public'
IDS='61961 73462 73461 86464 62032 75351 62008 73464 83740 74877 67943 73414 72940 62327 258716 62072 73463 73413 61974 258714 61842'.split()
IDS += '62007 62080 62445 67242 67942 67950 71114 72417 74866 83143 83153 83465 83738 83854 83857 83904 83906 83912 83915 83929 83930 84054 84881'.split()
IDS={'FMA'+i for i in IDS}
REFERENCE='https://training.seer.cancer.gov/anatomy/nervous/organization/cns.html'
def subset(raw,ids,system=None):
 n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=raw[28+n:]
 assert not any(g.get(k) for k in ['images','skins','animations','materials']), 'Unsupported source GLB'
 out={'asset':g['asset'],'scene':0,'scenes':[{'nodes':[]}],'nodes':[],'meshes':[],'accessors':[],'bufferViews':[]};buf=bytearray();am={};vm={}
 def accessor(i):
  if i in am:return am[i]
  a=copy.deepcopy(g['accessors'][i]);v=a['bufferView'];assert 'sparse' not in a
  if v not in vm:
   view=copy.deepcopy(g['bufferViews'][v]);assert view.get('buffer',0)==0
   start=view.get('byteOffset',0);buf.extend(b'\x00'*((-len(buf))%4));view['byteOffset']=len(buf);buf.extend(binary[start:start+view['byteLength']]);vm[v]=len(out['bufferViews']);out['bufferViews'].append(view)
  a['bufferView']=vm[v];am[i]=len(out['accessors']);out['accessors'].append(a);return am[i]
 for ni in g['scenes'][g.get('scene',0)]['nodes']:
  node=copy.deepcopy(g['nodes'][ni]);assert not node.get('children')
  if node['name'] not in ids:continue
  mesh=copy.deepcopy(g['meshes'][node['mesh']])
  if system:mesh.setdefault('extras',{})['system']=system
  for pr in mesh['primitives']:
   pr['attributes']={k:accessor(v) for k,v in pr['attributes'].items()}
   if 'indices' in pr:pr['indices']=accessor(pr['indices'])
  node['mesh']=len(out['meshes']);out['meshes'].append(mesh);out['scenes'][0]['nodes'].append(len(out['nodes']));out['nodes'].append(node)
 assert len(out['nodes'])==len(ids)
 buf.extend(b'\x00'*((-len(buf))%4));out['buffers']=[{'byteLength':len(buf)}];j=json.dumps(out,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
 return struct.pack('<III',0x46546c67,2,28+len(j)+len(buf))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(buf),0x004e4942)+buf

def main():
 c=json.loads((P/'catalog.json').read_text());by={s['id']:s for s in c['structures']}
 targets={m['id'] for m in c['meshes'].values() if m['structureId'] in IDS and m['system']!='nervous'}
 if not targets:
  for s in c['structures']:
   if s['id'] in IDS:s.update(system='nervous',classificationStatus='source-ID correction; expert review pending',classificationReferences=[REFERENCE])
  c['version']='bp3d4-'+hashlib.sha256(json.dumps({'packs':c['packs'],'structures':c['structures']},sort_keys=True).encode()).hexdigest()[:12]
  (P/'catalog.json').write_text(json.dumps(c,separators=(',',':'),ensure_ascii=False));print('Concepts corrected; geometry already classified');return
 report=[];new=[]
 def save_pack(p,raw,soft,ids):
  (P/p['url'].lstrip('/')).write_bytes(raw);payload=json.dumps(soft,separators=(',',':')).encode();(P/p['softwareUrl'].lstrip('/')).write_bytes(payload)
  p.update(meshIds=sorted(ids),bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),softwareBytes=len(payload),softwareSha256=hashlib.sha256(payload).hexdigest(),triangles=sum(c['meshes'][i]['triangles'] for i in ids))
 for p in list(c['packs']):
  moved=set(p['meshIds'])&targets
  if not moved:continue
  remain=set(p['meshIds'])-moved;assert remain
  raw=(P/p['url'].lstrip('/')).read_bytes();soft=json.loads((P/p['softwareUrl'].lstrip('/')).read_text());pid='nervous-corrected-'+p['id'];np={**p,'id':pid,'system':'nervous','url':'/packs/'+pid+'.glb','softwareUrl':'/software/'+pid+'.json'}
  save_pack(np,subset(raw,moved,'nervous'),[x for x in soft if x['id'] in moved],moved);new.append(np)
  save_pack(p,subset(raw,remain),[x for x in soft if x['id'] in remain],remain)
  for i in moved:
   m=c['meshes'][i];report.append({'mesh':i,'structure':m['structureId'],'name':by[m['structureId']]['canonicalName'],'previousSystem':m['system']});m.update(system='nervous',packId=pid)
 for s in c['structures']:
  if s['id'] in IDS:s.update(system='nervous',classificationStatus='source-ID correction; expert review pending',classificationReferences=[REFERENCE])
 c['packs']+=new;c['version']='bp3d4-'+hashlib.sha256(json.dumps({'packs':c['packs'],'structures':c['structures']},sort_keys=True).encode()).hexdigest()[:12]
 (P/'catalog.json').write_text(json.dumps(c,separators=(',',':'),ensure_ascii=False));(R/'docs/nervous-corrections.json').write_text(json.dumps(report,indent=2));print(len(report),'meshes reclassified,',len(new),'dedicated pack(s)')
if __name__=='__main__':main()
