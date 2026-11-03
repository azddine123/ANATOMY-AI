export const SYSTEMS = {
 skeletal:{fr:'Squelette & articulations',en:'Skeleton & joints',ar:'الهيكل العظمي والمفاصل',color:'#daceb0',icon:'bone'},
 muscular:{fr:'Muscles & tendons',en:'Muscles & tendons',ar:'العضلات والأوتار',color:'#c47670',icon:'biceps-flexed'},
 cardiovascular:{fr:'Cardiovasculaire',en:'Cardiovascular',ar:'القلب والأوعية الدموية',color:'#e0667a',icon:'heart-pulse'},
 nervous:{fr:'Système nerveux',en:'Nervous system',ar:'الجهاز العصبي',color:'#e6c272',icon:'brain'},
 respiratory:{fr:'Respiratoire',en:'Respiratory',ar:'الجهاز التنفسي',color:'#c68b9a',icon:'wind'},
 digestive:{fr:'Digestif',en:'Digestive',ar:'الجهاز الهضمي',color:'#c18c6b',icon:'waypoints'},
 urinary:{fr:'Urinaire',en:'Urinary',ar:'الجهاز البولي',color:'#b380a1',icon:'bean'},
 lymphatic:{fr:'Lymphatique',en:'Lymphatic',ar:'الجهاز اللمفاوي',color:'#7caf8b',icon:'network'},
 endocrine:{fr:'Endocrinien',en:'Endocrine',ar:'الغدد الصماء',color:'#a694ca',icon:'hexagon'},
 reproductive:{fr:'Reproducteur',en:'Reproductive',ar:'الجهاز التناسلي',color:'#c18aa8',icon:'sprout'},
 sensory:{fr:'Organes sensoriels',en:'Sensory organs',ar:'أعضاء الحس',color:'#83babd',icon:'eye'},
 integumentary:{fr:'Peau & tissus',en:'Skin & tissues',ar:'الجلد والأنسجة',color:'#ceae8c',icon:'layers'},
 other:{fr:'Autres structures',en:'Other structures',ar:'بنى أخرى',color:'#abb1b5',icon:'shapes'}
};
export const initialScene=()=>({systems:['skeletal','muscular'],hidden:[],selected:[],isolated:null,opacity:{},locked:[],xray:false,clipping:{axis:'none',value:0},explode:0});
export function reduceScene(state,cmd,catalog){
 const s=structuredClone(state);const ids=cmd.ids??[];
 if(ids.some(i=>!catalog.structures.some(x=>x.id===i)))throw new Error('Unknown anatomical ID');
 switch(cmd.type){
 case 'select':s.selected=cmd.multi?[...new Set([...s.selected,...ids])]:ids;break;
 case 'system':if(!SYSTEMS[cmd.system])throw new Error('Unknown system');s.systems=cmd.visible?[...new Set([...s.systems,cmd.system])]:s.systems.filter(x=>x!==cmd.system);s.isolated=null;break;
 case 'isolate':if(new Set([...meshSet(catalog,ids)].map(id=>catalog.meshes[id].sceneSpace??'bodyparts3d')).size>1)throw new Error('Reference organs cannot be overlaid on an unregistered body');s.isolated=ids; s.selected=ids;s.hidden=s.hidden.filter(id=>!ids.includes(id));s.clipping={axis:'none',value:0};s.explode=0;break;
 case 'hide':s.hidden=[...new Set([...s.hidden,...ids.filter(i=>!s.locked.includes(i))])];break;
 case 'show':s.hidden=s.hidden.filter(i=>!ids.includes(i));break;
 case 'opacity':if(!Number.isFinite(cmd.value)||cmd.value<0||cmd.value>1)throw new Error('Invalid opacity');for(const id of ids)if(!s.locked.includes(id))s.opacity[id]=cmd.value;break;
 case 'lock':s.locked=s.locked.includes(ids[0])?s.locked.filter(i=>!ids.includes(i)):[...s.locked,...ids];break;
 case 'xray':s.xray=!s.xray;break;
 case 'clip':if(!['none','x','y','z'].includes(cmd.axis)||!Number.isFinite(cmd.value))throw new Error('Invalid plane');s.clipping={axis:cmd.axis,value:cmd.value};break;
 case 'reset':return initialScene();
 case 'explode':s.explode=cmd.value;break;
 default:throw new Error('Unsupported scene command');
 }return s;
}
export class SceneStore{
 constructor(catalog){this.catalog=catalog;this.state=initialScene();this.past=[];this.future=[];this.listeners=[];}
 subscribe(fn){this.listeners.push(fn);return()=>this.listeners=this.listeners.filter(x=>x!==fn);}
 emit(){for(const fn of this.listeners)fn(this.state);}
 dispatch(cmd){const next=reduceScene(this.state,cmd,this.catalog);this.past.push(this.state);if(this.past.length>60)this.past.shift();this.state=next;this.future=[];this.emit();}
 undo(){if(!this.past.length)return;this.future.push(this.state);this.state=this.past.pop();this.emit();}
 redo(){if(!this.future.length)return;this.past.push(this.state);this.state=this.future.pop();this.emit();}
 restore(s){if(s?.isolated)reduceScene(this.state,{type:'isolate',ids:s.isolated},this.catalog);if(!s||!Array.isArray(s.systems)||s.systems.some(x=>!SYSTEMS[x]))throw new Error('Invalid view');this.past.push(this.state);this.state=structuredClone(s);this.future=[];this.emit();}
}
export function meshSet(catalog,ids){return new Set(ids.flatMap(i=>catalog.structures.find(s=>s.id===i)?.modelAssetIds??[]));}
export function visibleMeshIds(catalog,state){
 const isolated=state.isolated?meshSet(catalog,state.isolated):null,hidden=meshSet(catalog,state.hidden);
 return new Set(Object.values(catalog.meshes).filter(m=>(isolated?isolated.has(m.id):!m.sceneSpace&&state.systems.includes(m.system))&&!hidden.has(m.id)).map(m=>m.id));
}
