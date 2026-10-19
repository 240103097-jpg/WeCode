/** A visual fraction of completed work; every filled cell derives from saved counts. */
export function SegmentedProgress({value,max,label}:{value:number;max:number;label:string}) {
 const cells=max*4;
 const filled=Math.round(Math.max(0,Math.min(value,max))/max*cells);
 return <div className="segmented-progress" role="progressbar" aria-label={label} aria-valuemin={0} aria-valuemax={max} aria-valuenow={value} aria-valuetext={`${value} of ${max} complete`}>
  {Array.from({length:cells},(_,i)=><span key={i} aria-hidden="true" className={i<filled?'filled':''}/>)}
 </div>;
}
