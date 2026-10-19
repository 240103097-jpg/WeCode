export const tracks = ['Python', 'SQL', 'Git'] as const;
export const levels = ['Beginner', 'Intermediate', 'Advanced'] as const;
export type Track = typeof tracks[number];
export type Level = typeof levels[number];
export type ExerciseType = 'Quiz' | 'Fix the Bug' | 'Complete the Code';
export interface Exercise { id: string; type: ExerciseType; prompt: string; code?: string; options?: { id: string; text: string }[]; }
export interface Unit { id: string; track: Track; level: Level; title: string; summary: string; lesson: string[]; example: string; takeaway: string; exercises: Exercise[]; }
export interface Attempt { id: string; exerciseId: string; answer: string; correct: boolean; assisted: boolean; createdAt: string; feedback: string; }
export interface ExerciseProgress { correct: boolean; independent: boolean; revealed: boolean; hintCount: number; }
export interface UnitProgress { read: boolean; exercises: Record<string, ExerciseProgress>; }
export interface Learner { id: string; name: string; email: string; activeTrack: Track; levels: Record<Track, Level>; onboarded: boolean; }
export interface Snapshot { learner: Learner; units: Unit[]; progress: Record<string, UnitProgress>; attempts: Attempt[]; }
export interface Feedback { correct: boolean; text: string; assisted: boolean; }
export interface LearningService {
 session(): Promise<Learner | null>;
 register(input: {name: string; email: string}): Promise<Learner>;
 login(input: {email: string; passphrase: string}): Promise<Learner>;
 logout(): Promise<void>;
 snapshot(): Promise<Snapshot>;
 preferences(input: {track: Track; level: Level; onboarded?: boolean}): Promise<void>;
 profile(input: {name: string}): Promise<void>;
 markRead(unitId: string): Promise<void>;
 submit(input: {unitId: string; exerciseId: string; answer: string}): Promise<Feedback>;
 hint(input: {unitId: string; exerciseId: string}): Promise<string>;
 solution(input: {unitId: string; exerciseId: string}): Promise<{answer: string; explanation: string}>;
 simulateFailure(): Promise<void>;
}
export function unitStatus(unit: Unit, progress?: UnitProgress) {
 const solved = unit.exercises.filter(e => progress?.exercises[e.id]?.correct).length;
 const independent = unit.exercises.filter(e => progress?.exercises[e.id]?.independent).length;
 return { solved, independent, complete: !!progress?.read && solved === 3, steps: solved + (progress?.read ? 1 : 0) };
}
