import type { Unit } from '../services/types';
export interface AnswerRule { accepted: string[]; explanation: string; incorrect: string; hint: string; }
export const units: Unit[] = [];
export const answerRules: Record<string, AnswerRule> = {};
