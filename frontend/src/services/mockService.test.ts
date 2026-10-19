import {describe,it,expect,beforeEach} from 'vitest';
import {createMockService,STORAGE_KEY} from './mockService';
import type {LearningService} from './types';
let values:Map<string,string>, service:LearningService;
beforeEach(()=>{values=new Map();service=createMockService({getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);}},0);});
describe('local mock accounts',()=>{
 it('validates registration, duplicate email and public passphrase without storing credentials',async()=>{
  await expect(service.register({name:'x',email:'bad'})).rejects.toThrow('valid demo email');
  const learner=await service.register({name:'Learner',email:'ONE@example.test'});
  expect(learner.email).toBe('one@example.test');
  await expect(service.register({name:'Other',email:'one@example.test'})).rejects.toThrow('already');
  await service.logout();expect(await service.session()).toBeNull();await expect(service.snapshot()).rejects.toThrow('Sign in');
  await expect(service.login({email:learner.email,passphrase:'wrong'})).rejects.toThrow('incorrect');
  await service.login({email:learner.email,passphrase:'practice-only'});
  expect((await service.session())?.id).toBe(learner.id);
  expect(values.get(STORAGE_KEY)).not.toMatch(/password|passphrase|practice-only/);
 });
 it('restores a local session and separates mock learner records',async()=>{
  await service.register({name:'First',email:'first@example.test'});await service.preferences({track:'Git',level:'Advanced'});
  await service.logout();await service.register({name:'Second',email:'second@example.test'});
  expect((await service.snapshot()).learner.levels.Git).toBe('Beginner');
  await service.login({email:'first@example.test',passphrase:'practice-only'});
  const restored=createMockService({getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);}},0);
  expect((await restored.session())?.name).toBe('First');expect((await restored.snapshot()).learner.levels.Git).toBe('Advanced');
 });
 it('preserves damaged data and reports save failure',async()=>{
  values.set(STORAGE_KEY,'broken');await expect(service.session()).rejects.toThrow('not been reset');expect(values.get(STORAGE_KEY)).toBe('broken');
  const failing=createMockService({getItem:()=>null,setItem:()=>{throw Error('blocked');}},0);
  await expect(failing.register({name:'Test',email:'test@example.test'})).rejects.toThrow('Could not save');
 });
});
