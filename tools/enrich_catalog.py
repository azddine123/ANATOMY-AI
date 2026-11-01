"""Small explicit editorial translation layer; missing fields remain null."""
import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
translations={
'kidney':['rein','كلية','Ren'],'stomach':['estomac','معدة','Gaster'],'humerus':['humérus','عظم العضد','Humerus'],'femur':['fémur','عظم الفخذ','Femur'],'tibia':['tibia','عظم الظنبوب','Tibia'],'fibula':['fibula','عظم الشظية','Fibula'],'patella':['patella','رضفة','Patella'],'radius':['radius','عظم الكعبرة','Radius'],'ulna':['ulna','عظم الزند','Ulna'],'scapula':['scapula','لوح الكتف','Scapula'],'clavicle':['clavicule','ترقوة','Clavicula'],'mandible':['mandibule','الفك السفلي','Mandibula'],'sternum':['sternum','عظم القص','Sternum'],'body of sternum':['corps du sternum','جسم القص',None],'xiphoid process':['processus xiphoïde','الناتئ الرهابي',None],'skin':['peau','جلد','Cutis'],'spleen':['rate','طحال','Splen'],'urinary bladder':['vessie','مثانة بولية','Vesica urinaria'],'testis':['testicule','خصية','Testis'],'thyroid gland':['glande thyroïde','غدة درقية',None],'adrenal gland':['glande surrénale','غدة كظرية',None],'pancreas':['pancréas','بنكرياس','Pancreas'],'gallbladder':['vésicule biliaire','مرارة',None],'appendix':['appendice','زائدة دودية',None],'tongue':['langue','لسان','Lingua'],'trachea':['trachée','رغامى','Trachea'],'esophagus':['œsophage','مريء','Oesophagus'],'pons':['pont','جسر',None],'corpus callosum':['corps calleux','جسم ثفني','Corpus callosum'],'hypothalamus':['hypothalamus','تحت المهاد','Hypothalamus'],'thalamus':['thalamus','مهاد','Thalamus'],'ureter':['uretère','حالب','Ureter'],'median nerve':['nerf médian','عصب متوسط','Nervus medianus'],'ulnar nerve':['nerf ulnaire','عصب زندي','Nervus ulnaris'],'radial nerve':['nerf radial','عصب كعبري','Nervus radialis'],'biceps brachii':['biceps brachial','عضلة ذات الرأسين العضدية','Musculus biceps brachii'],'heart':['cœur','قلب','Cor'],'lung':['poumon','رئة','Pulmo'],'liver':['foie','كبد','Hepar'],'brain':['cerveau','دماغ',None]
}
# Common laterality labels are editorial translations, never inferred anatomical relationships.
gender={'scapula':'f','clavicle':'f','patella':'f','fibula':'f','kidney':'m','femur':'m','humerus':'m','tibia':'m','radius':'m','ulna':'m','lung':'m','ureter':'m','thalamus':'m','testis':'m','adrenal gland':'f'}
cat=json.load(open(R/'public/catalog.json'));count=0
for s in cat['structures']:
 name=s['canonicalName'];base=name;side=None
 for prefix in ['left ','right ']:
  if name.startswith(prefix):base=name[len(prefix):];side=prefix.strip()
 if base in translations:
  fr,ar,latin=translations[base]
  if side:
   fr+=' '+('gauche' if side=='left' else ('droite' if gender.get(base)=='f' else 'droit'));ar+=' '+('يسرى' if base in ['kidney','patella','clavicle','adrenal gland','lung'] and side=='left' else 'يمنى' if base in ['kidney','patella','clavicle','adrenal gland','lung'] else 'أيسر' if side=='left' else 'أيمن');latin=None
  s.update(frenchName=fr,arabicName=ar,latinName=latin,translationStatus='editorial; anatomical reviewer pending');count+=1
 s['synonyms']=s.get('synonyms',[])
 if base=='kidney':s['synonyms']+=['renal','rénal','كلوي']
 if base=='patella':s['synonyms']+=['rotule','kneecap']
for s in cat['structures']:s['synonyms']=list(dict.fromkeys(s['synonyms']))
# OpenStax evaluated but excluded: current pages display NC-SA terms.
for s in cat['structures']:
 s.pop('descriptions',None);s.pop('descriptionSource',None)
cat['version']='bp3d4-'+hashlib.sha256(json.dumps({'packs':cat['packs'],'structures':cat['structures']},sort_keys=True).encode()).hexdigest()[:12]
(R/'public/catalog.json').write_text(json.dumps(cat,separators=(',',':'),ensure_ascii=False))
print('Translated concepts',count)
