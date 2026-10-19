import type {Learner,LearningService,Snapshot,Feedback} from './types';
export class ApiServiceError extends Error {constructor(public code:string,message:string,public status=0){super(message);}}
interface Credential {accessToken:string;expiresAt:string;}
interface TokenStore {getItem(key:string):string|null;setItem(key:string,value:string):void;removeItem(key:string):void;}
export const API_SESSION_KEY='wecode.api.session.v1';
export function createApiService({baseUrl='/api/v1',storage,fetcher=fetch,onUnauthorized=()=>{},now=Date.now}:{baseUrl?:string;storage:TokenStore;fetcher?:typeof fetch;onUnauthorized?:()=>void;now?:()=>number}):LearningService {
 const base=baseUrl.replace(/\/$/,'');
 let generation=0;
 function clear(){generation++;storage.removeItem(API_SESSION_KEY);onUnauthorized();}
 function credential():Credential|null{
  try{const raw=storage.getItem(API_SESSION_KEY);if(!raw)return null;const value=JSON.parse(raw);if(typeof value.accessToken!=='string'||!Number.isFinite(Date.parse(value.expiresAt))||Date.parse(value.expiresAt)<=now()){clear();return null;}return value;}catch{clear();return null;}
 }
 async function request<T>(path:string,method='GET',body?:unknown,anonymous=false,logoutCredential?:Credential):Promise<T>{
  const current=anonymous?null:(logoutCredential??credential());
  if(!anonymous&&!current)throw new ApiServiceError('unauthorized','Your session has ended. Sign in again.',401);
  const revision=generation;
  let response:Response;
  try{response=await fetcher(base+path,{method,headers:{Accept:'application/json',...(body!==undefined?{'Content-Type':'application/json'}:{}),...(current?{Authorization:'Bearer '+current.accessToken}:{})},...(body!==undefined?{body:JSON.stringify(body)}:{}),cache:'no-store'});}catch{throw new ApiServiceError('network',method==='GET'?'Could not reach the server. Check the connection and retry.':'Could not confirm this change. It may have been saved. Refresh your workspace before trying again.');}
  if(revision!==generation)throw new ApiServiceError('stale','This account session has changed. Sign in again.');
  if(!response.ok){
   if(response.status===401&&!anonymous){clear();throw new ApiServiceError('unauthorized','Your session has ended. Sign in again.',401);}
   let code='server';try{const error=await response.json();if(typeof error.error?.code==='string')code=error.error.code;}catch{/* Never expose raw proxy/HTML/debug output. */}
   const messages:Record<string,string>={validation:'Check the entered fields and try again.',credentials:'Email or password is incorrect.',duplicate:'An account already uses this email. Sign in instead.','hint-locked':'Try an answer first. Hints unlock after an incorrect submission.','not-found':'This learning item is unavailable. Return to Learning Paths.',unavailable:'The service is temporarily unavailable. Refresh your workspace and retry.',internal:'The server could not complete this request. Refresh your workspace and retry.'};
   throw new ApiServiceError(code,messages[code]??'The server could not complete this request. Refresh your workspace and retry.',response.status);
  }
  if(response.status===204)return undefined as T;
  try{const value=await response.json() as T;if(revision!==generation)throw new ApiServiceError('stale','This account session has changed. Sign in again.');return value;}catch(error){if(error instanceof ApiServiceError)throw error;throw new ApiServiceError('response','The server returned an unreadable response. Refresh your workspace before trying again.');}
 }
 async function authenticate(path:string,input:unknown){
  if(storage.getItem(API_SESSION_KEY))clear();else generation++;
  const result=await request<{learner:Learner;accessToken:string;expiresAt:string}>(path,'POST',input,true);
  storage.setItem(API_SESSION_KEY,JSON.stringify({accessToken:result.accessToken,expiresAt:result.expiresAt}));
  return result.learner;
 }
 const exercise=(unitId:string,exerciseId:string)=>'/me/units/'+encodeURIComponent(unitId)+'/exercises/'+encodeURIComponent(exerciseId);
 return {
  session:async()=>{if(!credential())return null;try{return await request<Learner>('/me');}catch(error){if(error instanceof ApiServiceError&&error.status===401)return null;throw error;}},
  register:input=>{if(!input.password||input.password.length<12||input.password.length>128)return Promise.reject(new ApiServiceError('validation','Use a private password between 12 and 128 characters.'));return authenticate('/auth/register',{name:input.name.trim(),email:input.email.trim().toLowerCase(),password:input.password});},
  login:input=>authenticate('/auth/login',{email:input.email.trim().toLowerCase(),password:input.passphrase}),
  logout:async()=>{const token=credential();clear();try{if(token)await request('/auth/session','DELETE',undefined,false,token);}catch(error){if(!(error instanceof ApiServiceError&&error.status===401))throw error;}},
  snapshot:()=>request<Snapshot>('/me/snapshot'),
  profile:input=>request<void>('/me','PATCH',{name:input.name.trim()}),
  preferences:input=>request<void>('/me/preferences','PATCH',input),
  markRead:id=>request<void>('/me/units/'+encodeURIComponent(id)+'/lesson-read','PUT',{read:true}),
  submit:input=>request<Feedback>(exercise(input.unitId,input.exerciseId)+'/submissions','POST',{answer:input.answer.replace(/\r\n/g,'\n').trim()}),
  hint:input=>request<string>(exercise(input.unitId,input.exerciseId)+'/hints','POST'),
  solution:input=>request<{answer:string;explanation:string}>(exercise(input.unitId,input.exerciseId)+'/solution-reveal','PUT'),
  simulateFailure:async()=>{throw new ApiServiceError('unsupported','Failure simulation is available only in explicit mock mode.');},
 };
}
