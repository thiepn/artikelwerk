import { readFile, writeFile } from 'node:fs/promises';

const path='scripts/verify-source.mjs';
let source=await readFile(path,'utf8');
const needle=`requireFragment(html, 'const APP_VERSION = "1.2.0";', 'application version 1.2.0');`;
const replacement=`requireFragment(html, 'const APP_VERSION = "1.3.0";', 'application version 1.3.0');
requireFragment(html, 'id="settingsBtn"', 'Settings entrypoint');
requireFragment(html, 'id="settingsModal"', 'Settings dialog');
requireFragment(html, 'const ARTICLE_CONTROLS_KEY = "artikelwerk_article_controls";', 'article-control preference storage');
requireFragment(html, 'const SettingsManager = {', 'article-control preference manager');
requireFragment(html, 'data-article-controls', 'article-control layout styling contract');
requireFragment(html, 'value="bottom-bar"', 'Bottom Bar article controls option');
requireFragment(html, 'value="stacked"', 'Stacked article controls option');`;
if(!source.includes(needle)) throw new Error('Expected v1.2 source-contract marker was not found.');
if(source.includes('application version 1.3.0')) throw new Error('v1.3 source contract is already present.');
source=source.replace(needle,replacement);
await writeFile(path,source,'utf8');
console.log('Updated source verification contract for Artikelwerk v1.3.0 article controls.');
