import {describe,it,expect} from 'vitest';
import {units,answerRules} from './curriculum';
import {tracks,levels} from '../services/types';
describe('authored curriculum',()=>{
 it('covers every track/level exactly once with three distinct exercise types',()=>{
  expect(units).toHaveLength(9);expect(Object.keys(answerRules)).toHaveLength(27);
  for(const track of tracks)for(const level of levels){const matching=units.filter(u=>u.track===track&&u.level===level);expect(matching).toHaveLength(1);expect(matching[0].exercises.map(e=>e.type)).toEqual(['Quiz','Fix the Bug','Complete the Code']);}
  expect(new Set(units.map(u=>u.title)).size).toBe(9);
 });
 it('has unambiguous keys, explanatory feedback and explicit rejected examples',()=>{
  for(const unit of units){expect(unit.lesson.length).toBeGreaterThanOrEqual(2);expect(unit.example.length).toBeGreaterThan(20);
   for(const ex of unit.exercises){const rule=answerRules[ex.id];expect(rule.accepted.length).toBeGreaterThan(0);expect(rule.rejected.length).toBeGreaterThan(0);for(const rejected of rule.rejected)expect(rule.accepted).not.toContain(rejected);expect(rule.explanation.length).toBeGreaterThan(20);expect(rule.hint.length).toBeGreaterThan(10);if(ex.type==='Quiz')expect(ex.options?.filter(o=>rule.accepted.includes(o.id))).toHaveLength(1);}
  }
 });
});
