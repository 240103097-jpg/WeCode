import { type LearningService, type Learner, type Snapshot, type UnitProgress, tracks, levels } from './types';
import { units, answerRules } from '../data/curriculum';
export const DEMO_PASSPHRASE = 'practice-only';
export const STORAGE_KEY = 'wecode.mock.v1';
interface Account { learner: Learner; progress: Record<string, UnitProgress>; attempts: Snapshot['attempts']; }
interface Store { version: 1; sessionId: string | null; accounts: Account[]; }
export interface StorageAdapter { getItem(key: string): string | null; setItem(key: string, value: string): void; }
export class ServiceError extends Error { constructor(public code: string, message: string) { super(message); } }
export function createMockService(storage: StorageAdapter, delay = 180): LearningService {
 let failNext = false;
 async function operation<T>(fn: (s: Store) => T, write = false): Promise<T> {
  await new Promise(r => setTimeout(r, delay));
  if (failNext) { failNext = false; throw new ServiceError('unavailable', 'The demo service could not respond. Your progress is unchanged. Please retry.'); }
  let store: Store;
  try {
   const raw = storage.getItem(STORAGE_KEY);
   store = raw ? JSON.parse(raw) : {version: 1, sessionId: null, accounts: []};
   if (store.version !== 1 || !Array.isArray(store.accounts) || !('sessionId' in store)) throw Error();
  } catch { throw new ServiceError('storage', 'Local demo data is unavailable. Allow browser storage, or use a fresh browser profile if data is damaged, then retry. Existing data has not been reset.'); }
  const result = fn(store);
  if (write) { try { storage.setItem(STORAGE_KEY, JSON.stringify(store)); } catch { throw new ServiceError('storage', 'Could not save demo progress. Check browser storage permissions and retry.'); } }
  return structuredClone(result);
 }
 function account(s: Store): Account { const a = s.accounts.find(a => a.learner.id === s.sessionId); if (!a) throw new ServiceError('unauthorized','Sign in to your local demo account.'); return a; }
 function exercise(s: Store, unitId: string, exerciseId: string) {
  const a = account(s), unit = units.find(u => u.id === unitId), ex = unit?.exercises.find(e => e.id === exerciseId);
  if (!unit || !ex) throw new ServiceError('not-found', 'This exercise is unavailable. Return to Learning Paths.');
  const progress = a.progress[unitId] ??= {read:false, exercises:{}};
  const state = progress.exercises[exerciseId] ??= {correct:false, independent:false, revealed:false, hintCount:0};
  return {a, unit, ex, state, rule: answerRules[exerciseId]};
 }
 return {
  session: () => operation(s => s.accounts.find(a => a.learner.id === s.sessionId)?.learner ?? null),
  register: input => operation(s => {
   const name = input.name.trim(), email = input.email.trim().toLowerCase();
   if (name.length < 2 || name.length > 60 || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) throw new ServiceError('validation','Enter a display name (2–60 characters) and valid demo email.');
   if (s.accounts.some(a => a.learner.email === email)) throw new ServiceError('duplicate','A local account already uses this email. Sign in instead.');
   const learner: Learner = {id:crypto.randomUUID(), name, email, activeTrack:'Python', levels:{Python:'Beginner',SQL:'Beginner',Git:'Beginner'},onboarded:false};
   s.accounts.push({learner,progress:{},attempts:[]}); s.sessionId = learner.id; return learner;
  },true),
  login: input => operation(s => { const a = s.accounts.find(a => a.learner.email === input.email.trim().toLowerCase()); if (!a || input.passphrase !== DEMO_PASSPHRASE) throw new ServiceError('credentials','Email or demo passphrase is incorrect. Use a registered local email and practice-only.'); s.sessionId=a.learner.id; return a.learner; },true),
  logout: () => operation(s => {s.sessionId=null;},true),
  snapshot: () => operation(s => {const a=account(s);return {learner:a.learner,units,progress:a.progress,attempts:a.attempts};}),
  preferences: input => operation(s => {if (!tracks.includes(input.track) || !levels.includes(input.level)) throw new ServiceError('validation','Choose a listed track and level.');const a=account(s);a.learner.activeTrack=input.track;a.learner.levels[input.track]=input.level;if(input.onboarded)a.learner.onboarded=true;},true),
  profile: input => operation(s => {const name=input.name.trim();if(name.length<2 || name.length>60)throw new ServiceError('validation','Use a display name of 2–60 characters.');account(s).learner.name=name;},true),
  markRead: id => operation(s => {if(!units.some(u=>u.id===id))throw new ServiceError('not-found','Unit not found.');const a=account(s);(a.progress[id]??={read:false,exercises:{}}).read=true;},true),
  submit: input => operation(s => {
   const {a,state,rule}=exercise(s,input.unitId,input.exerciseId);
   const answer=input.answer.replace(/\r\n/g,'\n').trim();
   if(!answer || answer.length>4000)throw new ServiceError('validation','Enter an answer between 1 and 4,000 characters.');
   const correct=rule.accepted.includes(answer); const assisted=state.revealed;
   if(correct){state.correct=true;if(!assisted)state.independent=true;}
   const text=correct?rule.explanation:rule.incorrect;
   a.attempts.push({id:crypto.randomUUID(),exerciseId:input.exerciseId,answer,correct,assisted,createdAt:new Date().toISOString(),feedback:text});
   return {correct,text,assisted};
  },true),
  hint: input => operation(s => {const {a,state,rule}=exercise(s,input.unitId,input.exerciseId);if(!a.attempts.some(a=>a.exerciseId===input.exerciseId&&!a.correct))throw new ServiceError('hint-locked','Try an answer first. Hints unlock after an incorrect submission.');state.hintCount++;return rule.hint;},true),
  solution: input => operation(s => {const {state,rule}=exercise(s,input.unitId,input.exerciseId);state.revealed=true;return {answer:rule.accepted[0],explanation:rule.explanation};},true),
  simulateFailure: async () => {failNext=true;},
 };
}
// Only this adapter touches browser storage. UI consumes the typed asynchronous interface.
export const mockService: LearningService = createMockService({getItem:key=>window.localStorage.getItem(key),setItem:(key,value)=>window.localStorage.setItem(key,value)});
