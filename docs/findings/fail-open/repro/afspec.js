const fs=require('fs');
const html=fs.readFileSync('/Users/skyefortier/xps-app/templates/index.html','utf8').split('\n');
function extractFn(name){const re=new RegExp('^(async )?function '+name+'\\(');const s=html.findIndex(l=>re.test(l));let d=0,seen=false;for(let i=s;i<html.length;i++){for(const ch of html[i]){if(ch==='{'){d++;seen=true}else if(ch==='}')d--}if(seen&&d===0)return html.slice(s,i+1).join('\n')}}
const state={peaks:[]};
const env=new Function('state',['getPeak','peakToBackendSpec'].map(extractFn).join('\n')+'\nreturn {peakToBackendSpec};')(state);
const adv1={id:2,name:'Adventitious 1',shape:'GL',center:284.95,fwhm:1.4,amplitude:5000,glMix:30,fixCenter:false,_afCenterMin:284.80,_afCenterMax:285.30,_afFwhmMin:0.8,_afFwhmMax:3.0};
const g={id:1,name:'Graphite',shape:'asym-GL',center:284.5,fwhm:0.7,amplitude:20000,glMix:30,asymmetry:0.25,_afCenterMin:284.2,_afCenterMax:284.8,_afFwhmMin:0.4,_afFwhmMax:1.2,_afAsymMin:0.1,_afAsymMax:0.5};
state.peaks=[g,adv1];
console.log(JSON.stringify(state.peaks.map(env.peakToBackendSpec)));
