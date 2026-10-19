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

describe('independent track preferences',()=>{
 it('preserves each level across track switches and service reloads',async()=>{
  await service.register({name:'Learner',email:'learner@example.test'});await service.markRead('python-beginner');
  for(const track of ['Python','SQL','Git'] as const) for(const level of ['Beginner','Intermediate','Advanced'] as const){await service.preferences({track,level,onboarded:true});const snapshot=await service.snapshot();expect(snapshot.learner.activeTrack).toBe(track);expect(snapshot.learner.levels[track]).toBe(level);}
  await service.preferences({track:'SQL',level:'Beginner'});const restored=createMockService({getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);}},0);
  expect((await restored.session())?.levels).toEqual({Python:'Advanced',SQL:'Beginner',Git:'Advanced'});expect((await restored.session())?.onboarded).toBe(true);expect((await restored.snapshot()).progress['python-beginner'].read).toBe(true);
 });
});

import {units,answerRules} from '../data/curriculum';
import {unitStatus} from './types';
describe('authored practice behavior',()=>{
 it('checks every authored positive/negative example and unlocks hints only after incorrect work',async()=>{
  await service.register({name:'Learner',email:'learner@example.test'});
  for(const unit of units)for(const ex of unit.exercises){
   const input={unitId:unit.id,exerciseId:ex.id},rule=answerRules[ex.id];
   await expect(service.hint(input)).rejects.toThrow('Try an answer first');
   const wrong=await service.submit({...input,answer:rule.rejected[0]});expect(wrong.correct).toBe(false);expect(wrong.text).toBe(rule.incorrect);
   expect(await service.hint(input)).toBe(rule.hint);
   for(const answer of rule.accepted)expect((await service.submit({...input,answer})).correct).toBe(true);
  }
 });
 it('requires a correct submission after reveal and never calls assisted-only work independent',async()=>{
  await service.register({name:'Learner',email:'learner@example.test'});const unit=units[0];await service.markRead(unit.id);
  for(const ex of unit.exercises){const input={unitId:unit.id,exerciseId:ex.id};const solution=await service.solution(input);expect(solution.answer).toBe(answerRules[ex.id].accepted[0]);expect((await service.snapshot()).progress[unit.id].exercises[ex.id].correct).toBe(false);const result=await service.submit({...input,answer:solution.answer});expect(result).toMatchObject({correct:true,assisted:true});}
  const data=await service.snapshot();expect(unitStatus(unit,data.progress[unit.id])).toEqual({solved:3,independent:0,steps:4,complete:true});
 });
 it('normalizes outer whitespace/CRLF only and rejects blank, oversize and unrelated code',async()=>{
  await service.register({name:'Learner',email:'learner@example.test'});const input={unitId:units[0].id,exerciseId:units[0].exercises[1].id};
  expect((await service.submit({...input,answer:' \r\nint(age) + 1\r\n '})).correct).toBe(true);
  expect((await service.submit({...input,answer:'int(age)+1'})).correct).toBe(false);
  expect((await service.submit({...input,answer:'globalThis.executed = true'})).correct).toBe(false);
  expect('executed' in globalThis).toBe(false);
  await expect(service.submit({...input,answer:'  '})).rejects.toThrow('1 and 4,000');await expect(service.submit({...input,answer:'x'.repeat(4001)})).rejects.toThrow('1 and 4,000');
 });
});
