import test from 'node:test';
import assert from 'node:assert/strict';
import {EraStore,representativeYear,updateFilters} from '../atlas/layers.js';
import {PolityLoader} from '../atlas/polity-loader.js';

test('change-point filtering selects exactly the same records at every civil year',()=>{
  const collection={features:[{properties:{id:'a',from:-10,to:1}},{properties:{id:'b',from:1,to:5}},{properties:{id:'c',from:3,to:7}}]};
  const active=year=>collection.features.filter(f=>f.properties.from<=year&&year<f.properties.to).map(f=>f.properties.id);
  for(let year=-12;year<=10;year++){if(year===0)continue;assert.deepEqual(active(representativeYear(collection,year)),active(year));}
});
test('unchanged map state avoids redundant GPU property changes',()=>{
  const calls=[],map={getLayer:()=>true,setFilter:(...args)=>calls.push(['filter',...args]),setLayoutProperty:(...args)=>calls.push(['layout',...args]),setPaintProperty:(...args)=>calls.push(['paint',...args])};
  const state={year:117,focus:'',polity:true};
  updateFilters(map,state,.58,117);assert.equal(calls.length,7);calls.length=0;
  updateFilters(map,{...state,year:118},.58,117);assert.equal(calls.length,0);
  updateFilters(map,{...state,year:119},.65,117);assert.deepEqual(calls.map(c=>c[0]),['paint']);
});
test('worker decode requests resolve to their own era even when replies arrive out of order',async()=>{
  const sent=[],worker={postMessage:message=>sent.push(message),terminate(){}};
  const loader=new PolityLoader({workerFactory:()=>worker,fetcher:async()=>new Response('{}')});
  const a=loader.load('a'),b=loader.load('b');
  await new Promise(resolve=>setTimeout(resolve,0));
  worker.onmessage({data:{id:sent[1].id,collection:{name:'b'}}});
  worker.onmessage({data:{id:sent[0].id,collection:{name:'a'}}});
  assert.deepEqual(await Promise.all([a,b]),[{name:'a'},{name:'b'}]);
});
test('worker failure rejects pending work and retry falls back to the compatible decoder',async()=>{
  const worker={postMessage(){},terminate(){}};
  const loader=new PolityLoader({workerFactory:()=>worker,fetcher:async()=>new Response('{"type":"FeatureCollection","features":[]}')});
  const pending=loader.load('a');const rejected=assert.rejects(pending,/worker failed/);
  await new Promise(resolve=>setTimeout(resolve,0));worker.onerror();await rejected;
  assert.deepEqual(await loader.load('a'),{type:'FeatureCollection',features:[]});
});
test('an evicted failing request cannot erase a newer cached request for the same era',async()=>{
  const requests=[],loader={load:url=>new Promise((resolve,reject)=>requests.push({url,resolve,reject}))};
  const store=new EraStore({chunks:[]},{loader});
  const original=store.load({url:'a'});const caught=assert.rejects(original,/old request/);
  const others=['b','c','d','e'].map(url=>store.load({url}));
  const latest=store.load({url:'a'});requests[0].reject(new Error('old request'));await caught;
  assert.equal(store.cache.get('a'),latest);
  for(const request of requests.slice(1))request.resolve({type:'FeatureCollection',features:[]});
  await Promise.all([...others,latest]);
});
