import {render,screen,within} from '@testing-library/react';
import {it,expect} from 'vitest';
import {LearningIndex} from './LearningIndex';
import {SegmentedProgress} from './SegmentedProgress';
import {createMockService} from '../services/mockService';
import {units,answerRules} from '../data/curriculum';
it('keeps all levels accessible and distinguishes a completed unit from a selected available unit',async()=>{
 const data=new Map<string,string>();const api=createMockService({getItem:k=>data.get(k)??null,setItem:(k,v)=>{data.set(k,v);}},0);
 await api.register({name:'Learner',email:'learner@example.test'});
 const advanced=units.find(u=>u.track==='Python'&&u.level==='Advanced')!;
 await api.markRead(advanced.id);for(const ex of advanced.exercises)await api.submit({unitId:advanced.id,exerciseId:ex.id,answer:answerRules[ex.id].accepted[0]});
 render(<LearningIndex snapshot={await api.snapshot()}/>);
 expect(screen.getAllByRole('link')).toHaveLength(9);
 const current=screen.getByRole('link',{current:'step'});expect(current).toHaveAttribute('href','#unit/python-beginner');expect(within(current).getByText('Current position')).toBeVisible();
 const completed=screen.getByRole('link',{name:/Lazy iteration with generators/});expect(within(completed).getByText('Completed')).toBeVisible();
 for(const unit of units){const link=screen.getAllByRole('link').find(a=>a.getAttribute('href')==='#unit/'+unit.id);expect(link).toBeDefined();expect(link).not.toHaveAttribute('aria-disabled','true');}
});
it('exposes real completed counts to assistive technology without treating available work as complete',()=>{
 const view=render(<SegmentedProgress value={0} max={3} label="Python unit completion"/>);
 expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow','0');expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuetext','0 of 3 complete');
 view.rerender(<SegmentedProgress value={1} max={3} label="Python unit completion"/>);
 expect(screen.getByRole('progressbar',{name:'Python unit completion'})).toHaveAttribute('aria-valuenow','1');expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuemax','3');expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuetext','1 of 3 complete');
});
it('marks the same next incomplete unit as Continue Learning after the selected unit completes',async()=>{
 const data=new Map<string,string>();const api=createMockService({getItem:k=>data.get(k)??null,setItem:(k,v)=>{data.set(k,v);}},0);await api.register({name:'Learner',email:'learner@example.test'});
 const beginner=units.find(u=>u.track==='Python'&&u.level==='Beginner')!;await api.markRead(beginner.id);for(const ex of beginner.exercises)await api.submit({unitId:beginner.id,exerciseId:ex.id,answer:answerRules[ex.id].accepted[0]});
 render(<LearningIndex snapshot={await api.snapshot()}/>);
 expect(screen.getByRole('link',{current:'step'})).toHaveAttribute('href','#unit/python-intermediate');
 expect(within(screen.getByRole('link',{name:/Values, names & first steps/})).getByText('Completed')).toBeVisible();
});
