import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from civ_img import upload_image, add_to_post
from civlib import trpc
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

BASE = os.path.expanduser('~/资产/发布-MOSS-LoRA-大肥鱼/previews')
V_Q_SFT, V_P_SFT, V_Q_BASE, V_P_BASE = 3469536, 3469541, 3469542, 3469543

PLAN = [
    # (文件名, [versionId...])
    ('01_cover_duo_hug.png',      [V_Q_SFT, V_P_SFT]),
    ('02_duo_feed_rice.png',      [V_Q_SFT, V_P_SFT]),
    ('03_both_forms_static.png',  [V_Q_SFT, V_P_SFT]),
    ('06_qban_aquarium.png',      [V_Q_SFT]),
    ('07_qban_knit.png',          [V_Q_SFT]),
    ('11_qban_cyberpunk.png',     [V_Q_SFT]),
    ('12_chinese_text.png',       [V_Q_SFT]),
    ('05_prop_stand.png',         [V_P_SFT, V_P_BASE]),
    ('08_prop_jk_sakura.png',     [V_P_SFT]),
    ('09_prop_summer_beach.png',  [V_P_SFT]),
    ('10_prop_cafe.png',          [V_P_SFT]),
    ('04_qban_stand.png',         [V_Q_BASE]),
]

def one(name, vid, key, w, h):
    st, d = trpc('post.create', {"modelVersionId": vid})
    if st != 200: raise RuntimeError(f'建post失败 {st}: {str(d)[:150]}')
    pid = d['result']['data']['json']['id']
    st2, d2 = add_to_post(pid, key, os.path.join(BASE, name), w, h)
    if st2 != 200: raise RuntimeError(f'addImage失败 {st2}: {str(d2)[:150]}')
    return pid, d2['result']['data']['json']['id']

results = []
for name, vids in PLAN:
    p = os.path.join(BASE, name)
    w, h = Image.open(p).size
    t0 = time.time()
    key = upload_image(p)['key']
    for vid in vids:
        pid, iid = one(name, vid, key, w, h)
        results.append({'file': name, 'versionId': vid, 'postId': pid, 'imageId': iid})
        print(f'  ✅ {name:<28} -> v{vid} post={pid} img={iid}', flush=True)
    print(f'     (上传+关联 {time.time()-t0:.1f}s)', flush=True)

json.dump(results, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'state', 'civitai_gallery.json'), 'w'), ensure_ascii=False, indent=1)
print(f'\n共 {len(results)} 条图片关联')
