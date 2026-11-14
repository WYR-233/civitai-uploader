import sys, os, json, hashlib, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from civlib import _req, trpc

def upload_image(path):
    size = os.path.getsize(path)
    name = os.path.basename(path)
    ext = os.path.splitext(name)[1].lstrip('.').lower()
    mime = {'png':'image/png','jpg':'image/jpeg','jpeg':'image/jpeg','webp':'image/webp'}.get(ext,'image/png')
    st, body, _ = _req('https://civitai.com/api/v1/image-upload/multipart', 'POST',
                       {'filename': name, 'type': 'Image', 'size': size, 'mimeType': mime})
    if st != 200: raise RuntimeError(f'申请失败 {st}: {body[:200]}')
    d = json.loads(body)
    chunk = d['chunkSize']; parts = []
    with open(path, 'rb') as f:
        for u in d['urls']:
            pn = u['partNumber']; f.seek((pn-1)*chunk); blob = f.read(chunk)
            st2, b2, h2 = _req(u['url'], 'PUT', blob, {'Content-Type': mime},
                               proxy=False, raw=True, auth=False, timeout=600)
            if st2 not in (200,201): raise RuntimeError(f'分片{pn} 失败 {st2}: {b2[:200]}')
            parts.append({'ETag': h2.get('ETag'), 'PartNumber': pn})
    st3, b3, _ = _req('https://civitai.com/api/upload/complete', 'POST',
                      {'bucket': d['bucket'], 'key': d['key'], 'type': 'Image',
                       'uploadId': d['uploadId'], 'parts': parts, 'backend': d.get('backend')})
    if st3 != 200: raise RuntimeError(f'complete 失败 {st3}: {b3[:200]}')
    return {'key': d['key'], 'size': size}

def add_to_post(post_id, key, path, width=None, height=None):
    sha = hashlib.sha256(open(path,'rb').read()).hexdigest().upper()
    payload = {"postId": post_id, "url": key, "metadata": {"hash": sha}}
    if width and height: payload.update({"width": width, "height": height})
    return trpc('post.addImage', payload)
