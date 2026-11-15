import {readPolityResponse} from './codec.js';

export class PolityLoader {
  constructor({workerFactory,fetcher=(...args)=>fetch(...args)}={}) {
    this.fetcher=fetcher;this.pending=new Map();this.sequence=0;
    try {
      this.worker=workerFactory?workerFactory():typeof Worker!=='undefined'?new Worker(new URL('./polity-worker.js',import.meta.url),{type:'module'}):null;
    } catch {this.worker=null;}
    if(this.worker) {
      this.worker.onmessage=event=>{
        const {id,collection,error}=event.data,request=this.pending.get(id);if(!request)return;
        this.pending.delete(id);if(error)request.reject(new Error(error));else request.resolve(collection);
      };
      this.worker.onerror=()=>{
        for(const request of this.pending.values())request.reject(new Error('Polity decoder worker failed; retry loading'));
        this.pending.clear();this.worker.terminate();this.worker=null;
      };
    }
  }
  async load(url) {
    const response=await this.fetcher(url);
    if(!response.ok)throw new Error(`Polity download failed (${response.status})`);
    if(!this.worker)return readPolityResponse(response);
    const bytes=await response.arrayBuffer(),id=++this.sequence;
    // The worker may have failed while the request was downloading.
    if(!this.worker)return readPolityResponse(new Response(bytes));
    return new Promise((resolve,reject)=>{
      this.pending.set(id,{resolve,reject});
      try {this.worker.postMessage({id,bytes},[bytes]);}
      catch(error){this.pending.delete(id);reject(error);}
    });
  }
}
