"""Local catalogue gateway. No fabricated LLM responses; generation returns 503 until integrated."""
from pathlib import Path
import json,os,time,hmac,hashlib,difflib,unicodedata
from collections import defaultdict,deque
from typing import Literal
from fastapi import FastAPI,Depends,Header,HTTPException
from pydantic import BaseModel,Field,ConfigDict
ROOT=Path(__file__).resolve().parents[1]
CAT=json.load(open(ROOT/'public/catalog.json')); STRUCTURES={s['id']:s for s in CAT['structures']}
app=FastAPI(title='Anatomy AI catalogue gateway',version='0.1.0');hits=defaultdict(deque)
def authorize(authorization:str|None=Header(default=None)):
 expected=os.getenv('ANATOMY_GATEWAY_TOKEN')
 if not expected:raise HTTPException(503,'Gateway authentication is not configured')
 token=(authorization or '').removeprefix('Bearer ')
 if not hmac.compare_digest(token,expected):raise HTTPException(401,'Invalid authentication')
 key=hashlib.sha256(token.encode()).hexdigest();q=hits[key];now=time.monotonic()
 while q and q[0]<now-60:q.popleft()
 if len(q)>=30:raise HTTPException(429,'Rate limit exceeded')
 q.append(now)
class Query(BaseModel):
 model_config=ConfigDict(extra='forbid')
 query:str=Field(min_length=1,max_length=300)
 language:Literal['en','fr','ar']='en'
class Action(BaseModel):
 model_config=ConfigDict(extra='forbid')
 type:Literal['select','isolate','hide','show','opacity']
 ids:list[str]=Field(min_length=1,max_length=30)
 value:float|None=Field(default=None,ge=0,le=1)
class Commands(BaseModel):
 actions:list[Action]=Field(min_length=1,max_length=10)
def norm(s):return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
@app.get('/health')
def health():return {'status':'ok','catalogueVersion':CAT['version'],'generationAvailable':False}
@app.post('/v1/resolve',dependencies=[Depends(authorize)])
def resolve(q:Query):
 query=norm(q.query);matches=[]
 for s in STRUCTURES.values():
  names=[s.get(k) for k in ['id','canonicalName','frenchName','arabicName','latinName']]+s['synonyms']
  score=max([1 if query==norm(n) else .8 if query in norm(n) else difflib.SequenceMatcher(None,query,norm(n)).ratio()*.65 for n in names if n],default=0)
  if score>=.6:matches.append((score,s))
 matches.sort(key=lambda x:-x[0]);best=matches[:5]
 return {'mode':'catalogue-retrieval','results':[{'id':s['id'],'name':s.get({'en':'englishName','fr':'frenchName','ar':'arabicName'}[q.language])or s['canonicalName'],'sources':s['sourceReferences']} for _,s in best], 'actions':[{'type':'isolate','ids':[best[0][1]['id']]}]if best else []}
@app.post('/v1/scene/validate',dependencies=[Depends(authorize)])
def validate(c:Commands):
 for a in c.actions:
  if any(i not in STRUCTURES for i in a.ids):raise HTTPException(422,'Unknown anatomical ID')
  if a.type=='opacity' and a.value is None:raise HTTPException(422,'Opacity requires value')
 return c.model_dump(exclude_none=True)
@app.post('/v1/tutor',dependencies=[Depends(authorize)])
def tutor(q:Query):raise HTTPException(503,'Generative tutor is not integrated. Use catalogue retrieval.')
