import {readPolityResponse} from './codec.js';
self.onmessage=async event=>{
  const {id,bytes}=event.data;
  try {const collection=await readPolityResponse(new Response(bytes));self.postMessage({id,collection});}
  catch(error){self.postMessage({id,error:error.message});}
};
