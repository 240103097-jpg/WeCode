import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe,it,expect } from 'vitest';
import App from './App';
import {mockService} from './services/mockService';
describe('workspace shell',()=>{
 it('recovers from a simulated service failure',async()=>{await mockService.simulateFailure();render(<App/>);expect(await screen.findByRole('alert')).toHaveTextContent('Please retry');await userEvent.click(screen.getByRole('button',{name:'Retry'}));expect(await screen.findByText('Your workspace starts here')).toBeVisible();});
 it('shows honest empty state and functional navigation',async()=>{
  render(<App/>);expect(screen.getByRole('status')).toHaveTextContent('Loading');
  expect(await screen.findByText('Your workspace starts here')).toBeVisible();
  await userEvent.click(screen.getByRole('link',{name:'Progress'}));
  expect(await screen.findByRole('heading',{name:'Progress'})).toBeVisible();
 });
});
