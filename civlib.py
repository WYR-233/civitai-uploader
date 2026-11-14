import os, json, hashlib, urllib.request, urllib.error, time
KEY = open(os.path.expanduser('~/.secrets/civitai.token')).read().strip()
PROXY = 'http://127.0.0.1:9910'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
for k in ('no_proxy','NO_PROXY','all_proxy','ALL_PROXY'):
    os.environ.pop(k, None)
_pxy = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
_direct = urllib.request.ProxyHandler({})

def _req(url, method='GET', body=None, headers=None, proxy=True, timeout=180, raw=False, auth=True):
    h = {'User-Agent': UA, 'Referer': 'https://civitai.com/models/0/wizard?step=3'}
    if auth: h['Authorization'] = f'Bearer {KEY}'
    if headers: h.update(headers)
    data = body if raw else (json.dumps(body).encode() if body is not None else None)
    if data is not None and not raw and 'Content-Type' not in h:
        h['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    op = urllib.request.build_opener(_pxy if proxy else _direct)
    try:
        with op.open(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)

def trpc(proc, payload):
    st, body, _ = _req(f'https://civitai.com/api/trpc/{proc}', 'POST', {'json': payload})
    try: d = json.loads(body)
    except Exception: d = {'raw': body[:400].decode(errors='replace')}
    return st, d

def upload_file(path, content_type='application/octet-stream', label=None):
    """完整上传：申请→分片PUT→complete，返回 {url, name, sizeKB, key, sha256}"""
    size = os.path.getsize(path)
    name = label or os.path.basename(path)
    st, body, _ = _req('https://civitai.com/api/upload', 'POST',
                       {'filename': name, 'size': size, 'contentType': content_type})
    if st != 200:
        raise RuntimeError(f'申请上传失败 {st}: {body[:300]}')
    d = json.loads(body)
    chunk = d['chunkSize']
    parts = []
    with open(path, 'rb') as f:
        for u in d['urls']:
            pn = u['partNumber']
            f.seek((pn - 1) * chunk)
            blob = f.read(chunk)
            st2, b2, h2 = _req(u['url'], 'PUT', blob, {'Content-Type': content_type},
                               proxy=False, raw=True, timeout=900, auth=False)
            if st2 not in (200, 201):
                raise RuntimeError(f'分片 {pn} 失败 {st2}: {b2[:200]}')
            parts.append({'ETag': h2.get('ETag'), 'PartNumber': pn})
            print(f'      分片 {pn}/{len(d["urls"])} OK ({len(blob)/1048576:.0f}MB)', flush=True)
    st3, b3, _ = _req('https://civitai.com/api/upload/complete', 'POST',
                      {'bucket': d['bucket'], 'key': d['key'], 'uploadId': d['uploadId'], 'parts': parts})
    if st3 != 200:
        raise RuntimeError(f'complete 失败 {st3}: {b3[:300]}')
    return {'url': json.loads(b3), 'name': name, 'sizeKB': round(size/1024, 1),
            'size': size, 'key': d['key'], 'path': path}
