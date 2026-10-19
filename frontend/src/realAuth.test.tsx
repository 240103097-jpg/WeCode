import {render,screen} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {it,expect,vi} from 'vitest';
import App from './App';
import {createApiService} from './services/apiService';
it('keeps failed real login mode and credentials feedback visible without anonymous remount',async()=>{
 const values=new Map<string,string>();const fetcher=vi.fn<typeof fetch>().mockResolvedValue(new Response(JSON.stringify({error:{code:'credentials'}}),{status:401}));
 const service=createApiService({storage:{getItem:k=>values.get(k)??null,setItem:(k,v)=>{values.set(k,v);},removeItem:k=>{values.delete(k);}},fetcher,onUnauthorized:()=>window.dispatchEvent(new Event('wecode:unauthorized'))});
 render(<App service={service} mock={false}/>);
 await screen.findByText('Make room for learning.');
 await userEvent.click(screen.getByRole('button',{name:'Sign in'}));
 await userEvent.type(screen.getByLabelText('Email'),'unknown@example.test');await userEvent.type(screen.getByLabelText('Password'),'incorrect-password');
 await userEvent.click(screen.getByRole('button',{name:'Sign in →'}));
 expect(await screen.findByRole('alert')).toHaveTextContent('Email or password is incorrect.');
 expect(screen.getByRole('heading',{name:'Welcome back.'})).toBeVisible();
 expect(screen.getByLabelText('Email')).toHaveValue('unknown@example.test');
});

it('keeps the signed-out screen when an obsolete startup request fails after session invalidation',async()=>{
 let reject!:(error:Error)=>void;
 const {createMockService}=await import('./services/mockService');
 const store=new Map<string,string>();const service=createMockService({getItem:k=>store.get(k)??null,setItem:(k,v)=>{store.set(k,v);}},0);
 service.session=()=>new Promise((_,fail)=>{reject=fail;});
 const {act}=await import('@testing-library/react');
 render(<App service={service} mock={false}/>);
 await act(async()=>{window.dispatchEvent(new Event('wecode:unauthorized'));reject(new Error('obsolete private session response'));});
 expect(await screen.findByRole('heading',{name:'Make room for learning.'})).toBeVisible();
 expect(screen.queryByText('obsolete private session response')).not.toBeInTheDocument();
});
