"""给已发布的 Civitai 模型设置 tags。

用法：python3 civ_tags.py [modelId]
默认 modelId=3050927（大肥鱼 LoRA）。标签名单读 civ_versions.TAGS。

为什么要读模型再写：model.upsert 必填 name/type/uploadType/status 四项，
拿到当前值原样回传，避免改 tag 时把模型信息带歪。
接口细节：tagsOnModels=[{"name": "maid"}]，名字不存在会自动建 tag；
传 "tags" 字段不会报错但会被静默忽略（zod strip）。
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from civlib import trpc
import civ_versions as V

MODEL_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 3050927


def get_model(mid):
    st, d = trpc('model.getById', {"id": mid})
    if st != 200:
        raise SystemExit(f'读模型失败 {st}: {str(d)[:300]}')
    return d['result']['data']['json']


def set_tags(mid, names, dry=False):
    m = get_model(mid)
    payload = {
        "id": mid, "name": m['name'], "type": m['type'],
        "uploadType": m['uploadType'], "status": m['status'],
        "tagsOnModels": [{"name": n.strip()} for n in names if n.strip()],
    }
    if dry:
        print(json.dumps(payload, ensure_ascii=False, indent=1))
        return
    st, d = trpc('model.upsert', payload)
    if st != 200:
        raise SystemExit(f'写 tags 失败 {st}: {str(d)[:400]}')
    cur = get_model(mid).get('tagsOnModels') or []
    print(f'✅ 已设 {len(cur)} 个 tag：')
    for t in sorted(cur, key=lambda x: x['tag']['name']):
        flag = ' (分类)' if t['tag'].get('isCategory') else ''
        print(f"   {t['tag']['id']:>8}  {t['tag']['name']}{flag}")


if __name__ == '__main__':
    set_tags(MODEL_ID, V.TAGS, dry='--dry' in sys.argv)
