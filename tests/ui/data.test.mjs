import test from 'node:test';
import assert from 'node:assert/strict';
import {validateResidual,frame,total,money,json} from '../../demo/src/data.js';
const baseline={cell_ids:['a','b'],annual:[10,20],replay:[[5,10],[15,30]],annual_population_weighted_index:30,replay_population_weighted_index:[15,45]};
const residual={...baseline,plan_id:'balanced',annual:[1,2],replay:[[.5,1],[1.5,3]]};
test('same frame selection retains exact annual and hourly outputs',()=>{assert.equal(frame(baseline,null),baseline.annual);assert.equal(frame(baseline,1),baseline.replay[1]);assert.equal(total(baseline,0),15);assert.equal(frame(baseline,5),undefined)});
test('reject residual from wrong plan, grid ordering, absent hour or corrupt values',()=>{assert.equal(validateResidual(residual,baseline,{id:'balanced'}),residual);for(const bad of [{...residual,plan_id:'financial'},{...residual,cell_ids:['b','a']},{...residual,replay:[]},{...residual,annual:[-1,2]},{...residual,replay:[[NaN,1],[1,2]]}])assert.throws(()=>validateResidual(bad,baseline,{id:'balanced'}));});
test('financial units keep negative returns and missing values visible',()=>{assert.equal(money(-2500000),'−$2.5m');assert.equal(money(null),'—')});

test('HTML fallback and malformed JSON produce an actionable loader error',async()=>{const original=globalThis.fetch;try{for(const response of [new Response('<!doctype html>',{headers:{'content-type':'text/html'}}),new Response('{broken',{headers:{'content-type':'application/json'}})]){globalThis.fetch=async()=>response;await assert.rejects(()=>json('/data/missing.json'),{message:'Scenario data is unavailable. Check the local server and try again.'});}}finally{globalThis.fetch=original}});
