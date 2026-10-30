from pathlib import Path
import shutil,sys
upstream,site,fonts=map(Path,sys.argv[1:4])
requests=[]
for line in (upstream/'crates/text/web-fonts.txt').read_text().splitlines():
    line=line.split('#',1)[0].strip()
    if not line: continue
    when,family,style=[x.strip() for x in line.split('|')]
    requests.append((when,family,style))
manifest={}
for line in (fonts/'fonts/manifest.txt').read_text().splitlines():
    line=line.split('#',1)[0].strip()
    if not line: continue
    family,style,path,scripts,license_id,license_path,known_name,source=[x.strip() for x in line.split('|',7)]
    manifest[(family,style)]=(path,license_path,known_name)
for when,family,style in requests:
    if (family,style) not in manifest: continue
    path,license_path,known_name=manifest[(family,style)]
    source=fonts/path
    if not source.is_file(): raise SystemExit('pinned Craft font file missing: '+path)
    target=site/'fonts'/known_name[:16]/Path(path).name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,target)
    license_source=fonts/license_path
    if license_source.is_file(): shutil.copy2(license_source,target.with_name(target.name+'.OFL.txt'))
print('Packaged',sum(1 for _,family,style in requests if (family,style) in manifest),'available runtime Craft web fonts')
