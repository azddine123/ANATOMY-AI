// Only signed, sourced facts may enter future student-facing medical explanations.
export function studentFact(fact){
 if(!fact || fact.status!=='MEDICALLY_REVIEWED' || !fact.value || !fact.reviewedBy || !/^\d{4}-\d{2}-\d{2}$/.test(fact.lastVerified??'')) return null;
 if(!Array.isArray(fact.sources)||!fact.sources.length||fact.sources.some(s=>!s.title||!s.license||!/^https:\/\//.test(s.url??'')))return null;
 return fact.value;
}
export function reviewedFacts(facts){return Object.entries(facts??{}).filter(([,f])=>studentFact(f)!==null).map(([field,fact])=>({field,value:fact.value,sources:fact.sources}));}
