import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe,it,expect,beforeEach } from 'vitest';
import App from './App';
import {createMockService} from './services/mockService';
let store:Map<string,string>;
beforeEach(()=>{store=new Map();location.hash='Overview';});
function service(){return createMockService({getItem:k=>store.get(k)??null,setItem:(k,v)=>{store.set(k,v);}},0);}
describe('mock authentication UI',()=>{
 it('registers, restores session, signs out and handles wrong login',async()=>{
  const api=service(),view=render(<App service={api}/>);
  expect(screen.getByRole('status')).toHaveTextContent('Loading');
  await screen.findByText('Make room for learning.');
  await userEvent.type(screen.getByLabelText('Display name'),'Alex');await userEvent.type(screen.getByLabelText('Demo email'),'alex@example.test');await userEvent.click(screen.getByRole('button',{name:'Create demo account →'}));
  expect(await screen.findByRole('heading',{name:'Choose your starting point.'})).toBeVisible();
  await userEvent.click(screen.getByRole('button',{name:/SQL Think in data/}));await userEvent.selectOptions(screen.getByLabelText('SQL level'),'Intermediate');await userEvent.click(screen.getByRole('button',{name:'Open my workspace →'}));expect(await screen.findByText('CONTINUE LEARNING')).toBeVisible();view.unmount();render(<App service={service()}/>);expect(await screen.findByRole('heading',{name:'Overview'})).toBeVisible();
  await userEvent.click(screen.getByRole('button',{name:'Sign out'}));await screen.findByText('Make room for learning.');await userEvent.click(screen.getByRole('button',{name:'Sign in'}));
  await userEvent.type(screen.getByLabelText('Demo email'),'alex@example.test');await userEvent.type(screen.getByLabelText('Demo passphrase'),'wrong');await userEvent.click(screen.getByRole('button',{name:'Sign in →'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('incorrect');
 });
 it('recovers from a startup service failure',async()=>{const api=service();await api.simulateFailure();render(<App service={api}/>);expect(await screen.findByRole('alert')).toHaveTextContent('Please retry');await userEvent.click(screen.getByRole('button',{name:'Retry'}));expect(await screen.findByText('Make room for learning.')).toBeVisible();});
});

import {units,answerRules} from './data/curriculum';
it('renders saved progress, profile edits and recoverable settings errors without fake activity',async()=>{
 const api=service();await api.register({name:'Learner',email:'learner@example.test'});await api.preferences({track:'Python',level:'Beginner',onboarded:true});
 render(<App service={api}/>);expect(await screen.findByText('CONTINUE LEARNING')).toBeVisible();
 await userEvent.click(screen.getByRole('link',{name:'Progress'}));expect(await screen.findByText('No attempts yet. A good place to begin.')).toBeVisible();
 await userEvent.click(screen.getByRole('link',{name:'Settings'}));const field=await screen.findByLabelText('Display name');await userEvent.clear(field);await userEvent.type(field,'Renamed');await userEvent.click(screen.getByRole('button',{name:'Save profile'}));expect(await screen.findByRole('status')).toHaveTextContent('Profile saved');
 await userEvent.click(screen.getByRole('button',{name:'Test service recovery'}));expect(await screen.findByRole('alert')).toHaveTextContent('unchanged');await userEvent.click(screen.getByRole('button',{name:'Retry'}));expect(await screen.findByRole('heading',{name:'A space that feels like you.'})).toBeVisible();expect(screen.getByLabelText('Display name')).toHaveValue('Renamed');
});
it('shows assisted completion separately from independent solving after reload',async()=>{
 const api=service();await api.register({name:'Learner',email:'learner@example.test'});await api.preferences({track:'Python',level:'Beginner',onboarded:true});const unit=units[0];await api.markRead(unit.id);
 for(const ex of unit.exercises){await api.solution({unitId:unit.id,exerciseId:ex.id});await api.submit({unitId:unit.id,exerciseId:ex.id,answer:answerRules[ex.id].accepted[0]});}
 location.hash='Progress';render(<App service={service()}/>);
 expect(await screen.findByText('1 of 9 units complete')).toBeVisible();expect(screen.getByText('0/27')).toBeVisible();expect(screen.getAllByText('Correct · assisted')).toHaveLength(3);expect(screen.getByText('Showing the latest 3 of 3 submissions. Times are Asia/Almaty.')).toBeVisible();
});
