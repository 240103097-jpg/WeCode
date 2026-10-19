// Parse declarations/calls only. Never import the app or execute mock/learner code.
import ts from '../../frontend/node_modules/typescript/lib/typescript.js';
import {readFileSync,readdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('../../',import.meta.url));
const typesPath=path.join(root,'frontend/src/services/types.ts');
const source=ts.createSourceFile(typesPath,readFileSync(typesPath,'utf8'),ts.ScriptTarget.Latest,true);
const interfaces={},methods={},enums={};
const fields=members=>members.filter(ts.isPropertySignature).map(m=>({name:m.name.getText(source),optional:!!m.questionToken}));
for(const node of source.statements){
 if(ts.isInterfaceDeclaration(node)){
  if(node.name.text==='LearningService')for(const method of node.members){methods[method.name.getText(source)]={input:method.parameters[0]?.type&&ts.isTypeLiteralNode(method.parameters[0].type)?fields(method.parameters[0].type.members):null};}
  else interfaces[node.name.text]=fields(node.members);
 }
 if(ts.isVariableStatement(node))for(const decl of node.declarationList.declarations){const expr=decl.initializer&&ts.isAsExpression(decl.initializer)?decl.initializer.expression:decl.initializer;if(expr&&ts.isArrayLiteralExpression(expr))enums[decl.name.getText(source)]=expr.elements.map(e=>e.text);}
}
const consumers={};
const files=[path.join(root,'frontend/src/App.tsx'),...readdirSync(path.join(root,'frontend/src/components')).filter(f=>f.endsWith('.tsx')&&!f.endsWith('.test.tsx')).map(f=>path.join(root,'frontend/src/components',f))];
for(const file of files){const ast=ts.createSourceFile(file,readFileSync(file,'utf8'),ts.ScriptTarget.Latest,true);function visit(node){if(ts.isCallExpression(node)&&ts.isPropertyAccessExpression(node.expression)&&node.expression.expression.getText(ast)==='service'){(consumers[node.expression.name.text]??=[]).push(path.relative(root,file));}ts.forEachChild(node,visit);}visit(ast);}
console.log(JSON.stringify({interfaces,methods,enums,consumers}));
