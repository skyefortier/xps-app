// node pagebg.js <spec.json> -> page's bg over ROI (as runFit computes it)
const fs=require('fs');
const html=fs.readFileSync('/Users/skyefortier/xps-app/templates/index.html','utf8').split('\n');
function extractFn(name){const re=new RegExp('^(async )?function '+name+'\\(');const s=html.findIndex(l=>re.test(l));if(s<0)throw new Error(name);let d=0,seen=false;for(let i=s;i<html.length;i++){for(const ch of html[i]){if(ch==='{'){d++;seen=true}else if(ch==='}')d--}if(seen&&d===0)return html.slice(s,i+1).join('\n')}}
const names=['_bgWindowIndices','computeBackgroundCore','shirleyBackground','smartBackground','smartExperimentalBackground','shirleyLinearBackground','linearBackground','tougaardBackground','_applyEndpointAveraging','manualAnchorBackground'];
const src=names.map(n=>{try{return extractFn(n)}catch(e){return ''}}).join('\n');
const env=new Function(src+'\nreturn {computeBackgroundCore};')();
const d=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const shift=d.ccShift||0; const corr=d.rawBE.map(b=>b-shift);
const lo=parseFloat(d.ui.roiMin), hi=parseFloat(d.ui.roiMax);
const L=isNaN(lo)?-Infinity:lo, H=isNaN(hi)?Infinity:hi;
const be=[],inten=[]; corr.forEach((b,i)=>{if(b>=L&&b<=H){be.push(b);inten.push(d.rawIntensity[i])}});
const ui=Object.assign({},d.ui); if(process.env.UIOV) Object.assign(ui,JSON.parse(process.env.UIOV));
const hw=require("fs").readFileSync("/dev/null");const w=(new Function(src+"\nreturn _bgWindowIndices;"))()(be,ui.bgStart,ui.bgEnd);console.log(JSON.stringify({be,inten,bg:env.computeBackgroundCore(be,inten,ui),win:w,ui}));
