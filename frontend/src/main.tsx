import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './styles.css';
import {loadService} from './services/service';
const root=createRoot(document.getElementById('root')!);
loadService().then(({service,mock})=>root.render(<React.StrictMode><App service={service} mock={mock}/></React.StrictMode>)).catch(()=>root.render(<main><h1>WeCode could not start</h1><p role="alert">Check the service configuration and reload. No demo fallback was used.</p></main>));
