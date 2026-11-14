import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from civlib import trpc
import civ_versions as V

MODEL_ID = 3050927
up = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state', 'civitai_uploads.json')))
existing = {3469536: 0}   # versionId -> VERSIONS 索引
log = {}

def mk_files(cfg, vid):
    out = []
    for fname, ftype in cfg['files']:
        u = up[fname]
        st, d = trpc('modelFile.upsert', {
            "modelVersionId": vid, "name": fname, "url": u['url'],
            "sizeKB": round(u['sizeKB']), "type": ftype,
        })
        if st != 200:
            raise RuntimeError(f'挂文件 {fname} 失败 {st}: {str(d)[:200]}')
        fid = d['result']['data']['json']['id']
        out.append({'name': fname, 'fileId': fid, 'type': ftype})
        print(f'      ✅ 文件 {fname} -> fileId {fid}', flush=True)
    return out

for idx, cfg in enumerate(V.VERSIONS):
    if idx in existing.values():
        vid = [k for k, v in existing.items() if v == idx][0]
        print(f'\n[{idx+1}/4] {cfg["name"]} 已存在 vid={vid}，补挂文件', flush=True)
    else:
        print(f'\n[{idx+1}/4] 创建 {cfg["name"]}', flush=True)
        st, d = trpc('modelVersion.upsert', {
            "modelId": MODEL_ID, "name": cfg['name'], "baseModel": cfg['baseModel'],
            "description": cfg['desc'], "trainedWords": cfg['trainedWords'],
        })
        if st != 200:
            raise RuntimeError(f'建版本失败 {st}: {str(d)[:300]}')
        vid = d['result']['data']['json']['id']
        print(f'    ✅ versionId = {vid}', flush=True)
    log[cfg['name']] = {'versionId': vid, 'files': mk_files(cfg, vid)}
    time.sleep(0.5)

json.dump(log, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state', 'civitai_versions.json'), 'w'), ensure_ascii=False, indent=1)
print('\n全部完成')
for k, v in log.items():
    print(f'  {k}: vid={v["versionId"]} 文件={len(v["files"])}')
