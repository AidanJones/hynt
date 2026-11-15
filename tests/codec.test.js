import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {gunzipSync,gzipSync} from 'node:zlib';
import {unpackRing,unpackCollection,readPolityResponse} from '../atlas/codec.js';
test('integer deltas and exact exceptions retain coordinate precision',()=>{
  assert.deepEqual(unpackRing({d:[0,0,1235,1235,-1235,-1235],e:[[1,0.123456789012345,0.123456789012345]]},10000),[[0,0],[0.123456789012345,0.123456789012345],[0,0]]);
});
test('browser decoder reads actual generated geometry and source properties',async()=>{
  const manifest=JSON.parse(readFileSync(new URL('../atlas/data/manifest.json',import.meta.url)));
  const chunk=manifest.chunks.find(c=>c.from<=117&&117<c.to);
  const bytes=readFileSync(new URL('../atlas/data/'+chunk.url,import.meta.url));
  const collection=unpackCollection(JSON.parse(gunzipSync(bytes)));
  assert.equal(collection.features.length,chunk.features);
  assert.ok(collection.features.some(f=>f.properties.name==='Roman Empire'&&f.properties.from<=117&&117<f.properties.to));
  assert.deepEqual(await readPolityResponse(new Response(bytes)),collection);
  assert.deepEqual(await readPolityResponse(new Response(gunzipSync(bytes))),collection);
});
test('failed, corrupt and unsupported packages fail explicitly',async()=>{
  await assert.rejects(()=>readPolityResponse(new Response('Unavailable',{status:503})),/503/);
  await assert.rejects(()=>readPolityResponse(new Response(new Uint8Array([31,139,0,1]))));
  assert.throws(()=>unpackCollection({format:'unknown'}),/Unsupported/);
});
