"""Import a pinned licensed reference organ. Never align it to the male body by guesswork."""
import json,struct,hashlib,math
from pathlib import Path
from urllib.request import urlopen
R=Path(__file__).resolve().parents[1];P=R/'public';S=R/'data/source/hra'
URL='https://cdn.humanatlas.io/hra-releases/v1.2/models/VH_F_Ovary_L.glb'
DOI='https://doi.org/10.48539/HBM499.JLMB.357'
def main():
 S.mkdir(parents=True,exist_ok=True);path=S/'VH_F_Ovary_L.glb'
 if not path.exists():path.write_bytes(urlopen(URL,timeout=45).read())
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);binary=bytearray(raw[28+n:]);a=g['accessors'][1];v=g['bufferViews'][a['bufferView']];offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',12)
 assert g['nodes'][0]['extras']['ontologyid']=='FMA:7214'
 assert len(g['nodes'])==len(g['meshes'])==1 and not any(k in g['nodes'][0] for k in ['matrix','translation','rotation','scale'])
 vertices=[list(struct.unpack_from('<fff',binary,offset+i*stride)) for i in range(a['count'])]
 assert all(math.isfinite(x) for p in vertices for x in p)
 center=[(min(p[i] for p in vertices)+max(p[i] for p in vertices))/2 for i in range(3)]
 vertices=[[p[i]-center[i] for i in range(3)] for p in vertices]
 for i,p in enumerate(vertices):struct.pack_into('<fff',binary,offset+i*stride,*p)
 lo=[min(p[i] for p in vertices) for i in range(3)];hi=[max(p[i] for p in vertices) for i in range(3)];a.update(min=lo,max=hi)
 ia=g['accessors'][0];iv=g['bufferViews'][ia['bufferView']];indices=list(struct.unpack_from('<'+'H'*ia['count'],binary,iv.get('byteOffset',0)+ia.get('byteOffset',0)));assert max(indices)<len(vertices) and len(indices)%3==0
 faces=[indices[i:i+3] for i in range(0,len(indices),3)];assert all(len(set(f))==3 for f in faces)
 mid='HRA_OVARY_L';pid='hra-ovary-left';sid='FMA7214';g['nodes'][0]['name']=mid;g['meshes'][0]['name']=mid
 js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary+=b'\0'*((-len(binary))%4);blob=struct.pack('<III',0x46546c67,2,28+len(js)+len(binary))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(binary),0x004e4942)+binary
 soft=json.dumps([{'id':mid,'v':[round(x,8) for p in vertices for x in p],'f':indices}],separators=(',',':')).encode()
 (P/f'packs/{pid}.glb').write_bytes(blob);(P/f'software/{pid}.json').write_bytes(soft)
 sha=lambda b:hashlib.sha256(b).hexdigest()
 c=json.loads((P/'catalog.json').read_text());s={k:None for k in ['frenchName','arabicName','latinName','description','function','origin','insertion','innervation','vascularization','lymphaticDrainage','clinicalNotes']}
 s.update(id=sid,canonicalId=sid,sourceId='HBM499.JLMB.357',canonicalName='left ovary',englishName='left ovary',synonyms=['ovary','ovaire gauche','مبيض أيسر'],system='reproductive',subsystem='female_reproductive',region='pelvis',type='organ',parentStructure=[],children=[],relatedStructures=[],gender='female',modelAssetIds=[mid],source='Human Reference Atlas',sourceReferences=[DOI,URL],sceneSpace=pid,validationStatus='MEDICAL_REVIEW_PENDING',classificationStatus='source-ID matched; expert review pending',translationStatusByLanguage={'en':'SOURCE_MATCHED','fr':'MISSING','ar':'MISSING','la':'MISSING'},metadataCompleteness={k:False for k in ['description','function','innervation','vascularization','clinicalNotes']},displayNote='Isolated reference organ. Not registered to the BodyParts3D male body. External surface only; no follicles or internal anatomy.')
 c['structures']=[x for x in c['structures'] if x['id']!=sid]+[s];c['meshes'][mid]=dict(id=mid,structureId=sid,system='reproductive',triangles=len(faces),vertices=len(vertices),bounds=[lo,hi],watertight=None,sourceSha256=sha(raw),packId=pid,sceneSpace=pid)
 pack=dict(id=pid,system='reproductive',url=f'/packs/{pid}.glb',bytes=len(blob),sha256=sha(blob),meshIds=[mid],triangles=len(faces),softwareUrl=f'/software/{pid}.json',softwareBytes=len(soft),softwareSha256=sha(soft),sceneSpace=pid,source='Human Reference Atlas')
 c['packs']=[x for x in c['packs'] if x['id']!=pid]+[pack];c['version']='atlas-'+sha(json.dumps({'packs':c['packs'],'structures':c['structures']},sort_keys=True).encode())[:12];(P/'catalog.json').write_text(json.dumps(c,separators=(',',':'),ensure_ascii=False))
 manifest=dict(title='3D Reference Organ for Ovary, Female, Left v1.1',creators=['Kristen Browne','Heidi Schlehlein'],year=2022,publisher='HuBMAP',source=URL,doi=DOI,license='CC BY 4.0',licenseURL='https://creativecommons.org/licenses/by/4.0/',licenseEvidence='data/source/hra/3d-vh-f-ovary-l.md',retrievalDate='2026-09-13',sourceSha256=sha(raw),metadataSha256=sha((S/'3d-vh-f-ovary-l.md').read_bytes()),modifications=['Translated vertices to local origin; no scale or orientation change','Mesh identifier renamed','Materials recolored at runtime','CPU fallback retains all 424 triangles'],sourceCenterMeters=center,sourceVertices=len(vertices),triangles=len(faces),registrationStatus='NOT_REGISTERED',medicalStatus='MEDICAL_REVIEW_PENDING')
 (R/'data/curation/hra-ovary-provenance.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Imported left ovary:',len(vertices),'vertices',len(faces),'triangles;',len(blob),'bytes')
if __name__=='__main__':main()
