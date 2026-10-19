import {readFileSync} from 'node:fs';
const css=readFileSync(new URL('../src/styles.css',import.meta.url),'utf8');
const token=name=>{const value=css.match(new RegExp(`--${name}:\\s*(#[0-9a-f]{6})`,'i'))?.[1];if(!value)throw Error(`Missing ${name}`);return value;};
function luminance(hex){const rgb=hex.slice(1).match(/../g).map(x=>parseInt(x,16)/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4);return rgb[0]*.2126+rgb[1]*.7152+rgb[2]*.0722;}
function contrast(a,b){const [light,dark]=[luminance(a),luminance(b)].sort((x,y)=>y-x);return (light+.05)/(dark+.05);}
const checks=[];
for(const background of ['bg','surface','elevated'])for(const foreground of ['text','muted','yellow','green','error'])checks.push([`${foreground} on ${background}`,token(foreground),token(background),4.5]);
for(const fill of ['yellow','green'])checks.push([`dark ink on ${fill}`,token('bg'),token(fill),4.5]);
for(const bg of ['bg','surface','elevated'])checks.push([`control boundary on ${bg}`,token('control'),token(bg),3]);
checks.push(['hover text',token('text'),'#22382C',4.5],['selected text',token('text'),'#252616',4.5],['selected muted',token('muted'),'#252616',4.5],['selected yellow',token('yellow'),'#252616',4.5],['disabled text','#C2C9BD','#263044',4.5],['focus on hover',token('yellow'),'#22382C',3]);
let failed=0;
for(const [name,foreground,background,minimum] of checks){const ratio=contrast(foreground,background);const pass=ratio>=minimum;if(!pass)failed++;console.log(`${pass?'PASS':'FAIL'} ${name}: ${ratio.toFixed(2)}:1 (>=${minimum})`);}
if(failed)process.exitCode=1;
