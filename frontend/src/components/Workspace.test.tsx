import {render,screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {it,expect} from 'vitest';
import {Workspace} from './Workspace';
import {units} from '../data/curriculum';
import {createMockService} from '../services/mockService';
it('supports quiz feedback/retry/hint, a separate solution and the two text exercise types',async()=>{
 const values=new Map<string,string>(),api=createMockService({getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);}},0);await api.register({name:'Learner',email:'learner@example.test'});
 const unit=units[0];const refresh=async()=>{};
 render(<Workspace unit={unit} service={api} refresh={refresh}/>);
 await userEvent.click(screen.getByRole('button',{name:'Mark lesson as read'}));
 await userEvent.click(screen.getByRole('radio',{name:'23'}));await userEvent.click(screen.getByRole('button',{name:'Check answer →'}));expect(await screen.findByRole('status')).toHaveTextContent('Not quite');
 await userEvent.click(screen.getByRole('button',{name:'Get a hint'}));expect(await screen.findByText('Look for the result of integer addition.')).toBeVisible();
 await userEvent.click(screen.getByRole('button',{name:'Show Solution'}));expect(await screen.findByText('AUTHORED SOLUTION · ASSISTED WORK')).toBeVisible();
 await userEvent.click(screen.getByRole('radio',{name:'5'}));await userEvent.click(screen.getByRole('button',{name:'Try again →'}));expect(await screen.findByRole('status')).toHaveTextContent('Correct · assisted');
 await userEvent.click(screen.getByRole('button',{name:/Fix the Bug/}));await userEvent.type(screen.getByLabelText('Your answer'),'int(age) + 1');await userEvent.click(screen.getByRole('button',{name:'Check answer →'}));expect(await screen.findByRole('status')).toHaveTextContent('independently solved');
 await userEvent.click(screen.getByRole('button',{name:/Complete the Code/}));await userEvent.type(screen.getByLabelText('Your answer'),'print');await userEvent.click(screen.getByRole('button',{name:'Check answer →'}));expect(await screen.findByRole('status')).toHaveTextContent('independently solved');
 const saved=await api.snapshot();expect(saved.progress[unit.id].read).toBe(true);expect(saved.attempts).toHaveLength(4);expect(saved.progress[unit.id].exercises[unit.exercises[0].id].independent).toBe(false);
});
