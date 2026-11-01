from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]/'data/source'
BASE='https://dbarchive.biosciencedbc.jp/data/bodyparts3d/LATEST/'
FILES=['isa_parts_list_e.txt','isa_inclusion_relation_list.txt','isa_element_parts.txt','isa_BP3D_4.0_obj_99.zip']
def get(name):
 p=ROOT/name
 if not p.exists():
  with urlopen(BASE+name,timeout=120) as r,open(str(p)+'.tmp','wb') as f:
   while b:=r.read(1024*1024):f.write(b)
  Path(str(p)+'.tmp').rename(p)
 print(name,p.stat().st_size,flush=True)
 return {'file':name,'url':BASE+name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
if __name__=='__main__':
 ROOT.mkdir(parents=True,exist_ok=True)
 with ThreadPoolExecutor(4) as pool:r=list(pool.map(get,FILES))
 (ROOT/'provenance.json').write_text(json.dumps(r,indent=2))
 for n,u in [('license.html','https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html'),('Z-Anatomy-License.txt','https://raw.githubusercontent.com/Z-Anatomy/Models-of-human-anatomy/master/License.txt')]:
  (ROOT/n).write_bytes(urlopen(u,timeout=30).read())
