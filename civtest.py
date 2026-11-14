import os, json, hashlib, urllib.request, urllib.error

KEY = open(os.path.expanduser('~/.secrets/civitai.token')).read().strip()
PROXY = 'http://127.0.0.1:9910'
os.environ.pop('no_proxy', None); os.environ.pop('NO_PROXY', None)
opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY}))

def api(method, url, body=None, headers=None):
    h = {'Authorization': f'Bearer {KEY}', 'Referer': 'https://civitai.com/models/0/wizard?step=3', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'}
    if headers: h.update(headers)
    data = json.dumps(body).encode() if body is not None else None
    if data: h['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with opener.open(req, timeout=60) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)

path = os.path.expanduser('~/资产/发布-MOSS-LoRA-大肥鱼/previews/04_qban_stand.png')
size = os.path.getsize(path)
name = 'qban-stand-test.png'
print(f'文件: {name}  {size/1048576:.2f}MB')

st, body, _ = api('POST', 'https://civitai.com/api/upload',
                  {'filename': name, 'size': size, 'contentType': 'image/png'})
print('1) 申请上传:', st)
d = json.loads(body)
print('   chunkSize:', d['chunkSize'], '| 分片:', len(d['urls']), '| key:', d['key'])

# 单片上传
with open(path, 'rb') as f: blob = f.read()
u = d['urls'][0]
req = urllib.request.Request(u['url'], data=blob, method='PUT',
                             headers={'Content-Type': 'image/png'})
op = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # R2 直连
try:
    with op.open(req, timeout=120) as r:
        etag = r.headers.get('ETag'); print('2) PUT 分片:', r.status, 'ETag:', etag)
except urllib.error.HTTPError as e:
    print('2) PUT 失败:', e.code, e.read()[:300]); raise SystemExit
except Exception as e:
    print('2) PUT 异常:', type(e).__name__, e); raise SystemExit

st, body, _ = api('POST', 'https://civitai.com/api/upload/complete',
    {'bucket': d['bucket'], 'key': d['key'], 'uploadId': d['uploadId'],
     'parts': [{'ETag': etag, 'PartNumber': u['partNumber']}]})
print('3) complete:', st, body[:400].decode(errors='replace'))
