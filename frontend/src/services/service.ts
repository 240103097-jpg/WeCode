import {createApiService} from './apiService';
import type {LearningService} from './types';
// Compile-time branch removes mock curriculum from the default production build.
export async function loadService():Promise<{service:LearningService;mock:boolean}>{
 if(import.meta.env.VITE_SERVICE_MODE==='mock'){
  if(import.meta.env.PROD)throw new Error('Mock mode is for development and tests only. Build with real API mode.');
  const {mockService}=await import('./mockService');return {service:mockService,mock:true};
 }
 if(import.meta.env.VITE_SERVICE_MODE&&import.meta.env.VITE_SERVICE_MODE!=='api')throw new Error('VITE_SERVICE_MODE must be api or mock.');
 return {service:createApiService({baseUrl:import.meta.env.VITE_API_BASE_URL||'/api/v1',storage:window.sessionStorage,onUnauthorized:()=>window.dispatchEvent(new Event('wecode:unauthorized'))}),mock:false};
}
