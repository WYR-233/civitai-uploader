import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from civlib import upload_file
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.expanduser('~/资产/发布-MOSS-LoRA-大肥鱼')
LORAS = ['qban-sft-fused-qkv', 'qban-sft-split', 'prop-sft-fused-qkv', 'prop-sft-split',
         'qban-base-fused-qkv', 'qban-base-split', 'prop-base-fused-qkv', 'prop-base-split']
PREV = sorted(f for f in os.listdir(f'{BASE}/previews') if f.endswith('.png'))

jobs = [(f'{BASE}/{n}.safetensors', f'{n}.safetensors', 'application/octet-stream') for n in LORAS]
jobs += [(f'{BASE}/previews/{n}', n, 'image/png') for n in PREV]

results, t0 = {}, time.time()
def work(j):
    path, name, ctype = j
    r = upload_file(path, ctype, name)
    return name, {'url': str(r['url']), 'name': name, 'sizeKB': r['sizeKB'], 'sha256': None}

with ThreadPoolExecutor(max_workers=3) as ex:
    futs = {ex.submit(work, j): j[1] for j in jobs}
    for f in as_completed(futs):
        n = futs[f]
        try:
            name, info = f.result()
            results[name] = info
            print(f'  ✅ {name}  ({time.time()-t0:.0f}s 累计)', flush=True)
        except Exception as e:
            print(f'  ❌ {n}: {e}', flush=True)
            results[n] = {'error': str(e)}

json.dump(results, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state', 'civitai_uploads.json'), 'w'), ensure_ascii=False, indent=1)
ok = sum(1 for v in results.values() if 'error' not in v)
print(f'\n完成 {ok}/{len(jobs)}，总耗时 {time.time()-t0:.0f}s')
