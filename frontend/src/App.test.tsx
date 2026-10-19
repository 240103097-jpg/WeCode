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
  expect(await screen.findByRole('heading',{name:'Overview'})).toBeVisible();
  view.unmount();render(<App service={service()}/>);expect(await screen.findByRole('heading',{name:'Overview'})).toBeVisible();
  await userEvent.click(screen.getByRole('button',{name:'Sign out'}));await screen.findByText('Make room for learning.');await userEvent.click(screen.getByRole('button',{name:'Sign in'}));
  await userEvent.type(screen.getByLabelText('Demo email'),'alex@example.test');await userEvent.type(screen.getByLabelText('Demo passphrase'),'wrong');await userEvent.click(screen.getByRole('button',{name:'Sign in →'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('incorrect');
 });
 it('recovers from a startup service failure',async()=>{const api=service();await api.simulateFailure();render(<App service={api}/>);expect(await screen.findByRole('alert')).toHaveTextContent('Please retry');await userEvent.click(screen.getByRole('button',{name:'Retry'}));expect(await screen.findByText('Make room for learning.')).toBeVisible();});
});
