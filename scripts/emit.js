#!/usr/bin/env node
const fs=require('fs');const path=require('path');
const AVTP_TO_TYPE={a:'audio',v:'video',t:'text',p:'image',k:'keyboard'};
function normalizeAvtpComponent(k,v){const c=Object.assign({},v);if(!c.type&&AVTP_TO_TYPE[k])c.type=AVTP_TO_TYPE[k];if(!c.name)c.name=`${k}_${c.label||'comp'}`;return c;}
function normalizeRoutine(rect){if(Array.isArray(rect.components))return{name:rect.name||`r_${rect.id||'?'}`,components:rect.components};if(Array.isArray(rect.avtpComponents))return{name:rect.name||`r_${rect.id||'?'}`,components:rect.avtpComponents};if(rect.avtpData&&typeof rect.avtpData==='object'){const cs=[];for(const[k,v]of Object.entries(rect.avtpData)){if(v&&v.enabled!==false)cs.push(normalizeAvtpComponent(k,v));}return{name:rect.name||`r_${rect.id||'?'}`,components:cs};}return{name:rect.name||`r_${rect.id||'?'}`,components:[]};}
function normalize(input){if(Array.isArray(input.flowchart)){const rs=[],ls=[];for(const it of input.flowchart){if(it.type==='Loop'||it.nRounds!==undefined||it.n_rounds!==undefined)ls.push(it);else rs.push(it);}return{routines:rs,loops:ls};}if(Array.isArray(input.routineRects)){return{routines:input.routineRects.map(normalizeRoutine),loops:input.loops||[]};}if(Array.isArray(input.routines)){return{routines:input.routines.map(normalizeRoutine),loops:input.loops||[]};}throw new Error('unknown input format');}
const args=process.argv.slice(2);if(args.length!==2){process.stderr.write('Usage: node emit.js <input.json> <output.psyexp>\n');process.exit(2);}
const inp=args[0];const outp=args[1];
if(!fs.existsSync(inp)){process.stderr.write(`[emit] no input: ${inp}\n`);process.exit(3);}
let data;try{data=JSON.parse(fs.readFileSync(inp,'utf8'));}catch(e){process.stderr.write(`[emit] parse fail: ${e.message}\n`);process.exit(4);}
let norm;try{norm=normalize(data);}catch(e){process.stderr.write(`[emit] normalize fail: ${e.message}\n`);process.exit(5);}
process.stderr.write(`[emit] normalized: ${norm.routines.length} routines, ${norm.loops.length} loops\n`);
let conv;try{const m=require(path.resolve(__dirname,'json2psyexp.js'));conv=m.convertToPsyExpXML;if(typeof conv!=='function')throw new Error('not a function');}catch(e){process.stderr.write(`[emit] load fail: ${e.message}\n`);process.exit(6);}
let xml;try{xml=conv(norm);}catch(e){process.stderr.write(`[emit] convert fail: ${e.message}\n`);if(e.stack)process.stderr.write(e.stack+'\n');process.exit(7);}
if(typeof xml!=='string'||!xml.length){process.stderr.write('[emit] empty output\n');process.exit(8);}
fs.writeFileSync(outp,xml,'utf8');
process.stdout.write(`[emit] OK  ${inp} -> ${outp} (${xml.length} bytes)\n`);
