const PREFIX='anatomy-ai:v1:';
export function read(key,fallback){try{const x=JSON.parse(localStorage.getItem(PREFIX+key));return x??fallback;}catch{return fallback;}}
export function write(key,value){try{localStorage.setItem(PREFIX+key,JSON.stringify(value));return true;}catch{return false;}}
export function nextReview(previous,correct,now=Date.now()){const attempts=(previous?.attempts??0)+1;const streak=correct?(previous?.streak??0)+1:0;const days=correct?Math.min(30,2**Math.max(0,streak-1)):0;return{attempts,correct:(previous?.correct??0)+(correct?1:0),streak,due:now+(days?days*86400000:600000)};}
export function quizOptions(answer,pool,random=Math.random){const others=pool.filter(x=>x.id!==answer.id);for(let i=others.length-1;i>0;i--){let j=Math.floor(random()*(i+1));[others[i],others[j]]=[others[j],others[i]];}return[answer,...others.slice(0,3)].sort(()=>random()-.5);}
