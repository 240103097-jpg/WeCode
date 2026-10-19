import {readFileSync,readdirSync} from 'node:fs';
const directory=new URL('../dist/assets/',import.meta.url);
const files=readdirSync(directory).filter(name=>name.endsWith('.js'));
if(!files.length)throw new Error('Build first');
const text=files.map(name=>readFileSync(new URL(name,directory),'utf8')).join('\n');
for(const secret of ['Two integer values are added to produce the integer 5.','int(age) + 1','wecode.mock.v1','answerRules'])if(text.includes(secret))throw new Error('Mock curriculum/storage leaked into real production bundle: '+secret);
console.log('PASS real production bundle excludes mock service/storage and authored answer fixtures');
