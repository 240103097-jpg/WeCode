import {unitStatus,tracks,type Snapshot} from '../services/types';
export function LearningIndex({snapshot,practice=false}:{snapshot:Snapshot;practice?:boolean}) {
 const selected=snapshot.units.find(u=>u.track===snapshot.learner.activeTrack&&u.level===snapshot.learner.levels[snapshot.learner.activeTrack]);
 const continueUnit=selected&&unitStatus(selected,snapshot.progress[selected.id]).complete?snapshot.units.find(u=>u.track===snapshot.learner.activeTrack&&!unitStatus(u,snapshot.progress[u.id]).complete)??selected:selected;
 if(practice) return <div className="unit-list">{snapshot.units.map((unit,i)=>{
  const status=unitStatus(unit,snapshot.progress[unit.id]);
  return <a href={'#unit/'+unit.id} className="unit-row" key={unit.id}><span className="unit-number">{String(i+1).padStart(2,'0')}</span><div className="unit-info"><span className="eyebrow">{unit.track} / {unit.level}</span><h3>{unit.title}</h3><p>Quiz · Fix the Bug · Complete the Code</p></div><div className="row-progress"><span className={status.complete?'green':''}>{status.complete?'✓ Complete':`${status.steps}/4 steps`}</span><small>{status.independent}/3 independent</small></div><span className="row-arrow" aria-hidden="true">↗</span></a>;
 })}</div>;
 return <div className="learning-routes">{tracks.map((track,trackIndex)=><section className="path-section" key={track} aria-label={track+' learning path'}><div className="path-header"><span className="track-number">{String(trackIndex+1).padStart(2,'0')}</span><div><span className="eyebrow">LEARNING TRACK</span><h2>{track}</h2></div><span className="path-access-note">ALL LEVELS AVAILABLE</span></div><ol className="pixel-route">{snapshot.units.filter(u=>u.track===track).map((unit,i)=>{
  const status=unitStatus(unit,snapshot.progress[unit.id]);
  const current=continueUnit?.id===unit.id;
  const state=status.complete?'completed':current?'current':'available';
  return <li key={unit.id} className={'path-stop '+state}><a href={'#unit/'+unit.id} aria-current={current?'step':undefined}><span className="node-marker" aria-hidden="true">{status.complete?'✓':String(i+1).padStart(2,'0')}</span><div className="node-content"><div className="node-topline"><span className="eyebrow">{unit.level}</span><span className="node-state">{status.complete?'Completed':current?'Current position':'Available'}{status.complete&&current?' · Current position':''}</span></div><h3>{unit.title}</h3><p>{unit.summary}</p><div className="node-meta"><span>{status.steps}/4 steps</span><span>{status.independent}/3 independent</span><span className="row-arrow" aria-hidden="true">→</span></div></div></a></li>;
 })}</ol></section>)}</div>;
}
