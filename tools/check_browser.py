"""Read-only responsive checks for the built handbook; no application requests."""
import argparse,json,threading
from functools import partial
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser();parser.add_argument('--site');parser.add_argument('--output',default='.build/update-20261106');args=parser.parse_args()
root=Path(__file__).resolve().parents[1];out=root/args.output;out.mkdir(parents=True,exist_ok=True)
class Quiet(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=None
if args.site:base=args.site.rstrip('/')+'/'
else:
 server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(root/'build/html')))
 threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}/'
report={'site':base,'viewports':[],'errors':[]}
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/home/data/litieyun/app/docker/.build/google-chrome/opt/google/chrome/chrome',args=['--no-sandbox','--disable-gpu'])
  context=browser.new_context()
  page=context.new_page();page.on('pageerror',lambda error:report['errors'].append(str(error)))
  response=page.goto(base,wait_until='networkidle',timeout=60000);assert response.status==200
  paths=page.locator('.wy-menu-vertical li.toctree-l1 > a').evaluate_all('(xs)=>xs.map(x=>x.getAttribute("href"))')
  paths=list(dict.fromkeys(['index.html']+paths));assert len(paths)==15,len(paths)
  for width in [1440,390]:
   page.set_viewport_size({'width':width,'height':1000 if width==1440 else 844})
   for path in paths:
    response=page.goto(base+path,wait_until='domcontentloaded',timeout=60000);assert response.status==200
    page.locator('.document h1').wait_for()
    page.wait_for_function('Array.from(document.images).every(i=>i.complete)')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'),(width,path)
    assert page.locator('.document img').evaluate_all('(xs)=>xs.every(i=>i.naturalWidth>0)'),path
    body=page.locator('.document').inner_text();assert 'tnlearn' not in body.lower()
    if path in ['index.html','guide/service-hub.html','guide/deployment.html']:
     page.screenshot(path=str(out/f'{width}-{path.replace("/","-")}.png'),full_page=True)
   report['viewports'].append({'width':width,'pages':len(paths),'overflow':False,'broken_images':False})
  page.goto(base,wait_until='domcontentloaded');page.locator('.wy-nav-top [data-toggle="wy-nav-top"]').click();assert 'shift' in page.locator('.wy-nav-side').get_attribute('class')
  page.locator('.wy-menu-vertical a[href="guide/service-hub.html"]').click();page.wait_for_url('**/guide/service-hub.html');assert page.locator('.document h1').inner_text().startswith('服务台')
  page.goto(base+'search.html?q=%E6%9C%8D%E5%8A%A1%E5%8F%B0',wait_until='networkidle');page.wait_for_function('document.querySelectorAll(".search li").length>0',timeout=30000)
  assert '服务台与资源管理' in page.locator('.search').inner_text()
  report.update(mobile_navigation=True,chinese_search=True,pdf_link=page.locator('a[href*="time-reshape-guide.pdf"]').first.get_attribute('href'))
  assert not report['errors'],report['errors'];browser.close()
finally:
 if server:server.shutdown();server.server_close()
(out/'browser-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
