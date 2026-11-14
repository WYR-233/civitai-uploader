# civitai-uploader

Civitai **内部 API** 上传工具包（官方没有模型上传 API，这套是从前端 JS 里逆出来的）。

> 完整接口说明与坑位见记忆卡：`~/deepseek-memory/memory/工作/AI生图/2026-11-14_Civitai自动化上传全流程.md`

## 环境要求

- Python 3（只用标准库 + Pillow）
- 代理在 `127.0.0.1:9910`（geph5 http 口），脚本里 `PROXY` 可改
- Token：`~/.secrets/civitai.token`（32 位，Full Access），**不要硬编码进代码**

## 脚本

| 文件 | 干什么 |
| --- | --- |
| `civlib.py` | 底层：`_req` / `trpc` / `upload_file`（R2 分片）。所有脚本都 import 它 |
| `civtest.py` | ⚠️ **会真的上传一张图** 做连通性测试，无参数直接跑 |
| `civ_versions.py` | 纯配置：4 个版本的 `name` / `baseModel` / `description` / 文件清单 / `TAGS` |
| `civ_upload_all.py` | 按 `civ_versions.py` 的文件清单批量传模型文件 → `state/civitai_uploads.json` |
| `civ_img.py` | 传单张图（Backblaze multipart，返回 UUID key）+ `add_to_post` 挂进版本 |
| `civ_gallery.py` | 批量传 `previews/` 并把每张图挂到指定版本 → `state/civitai_gallery.json` |
| `civ_build.py` | 建版本 + 挂文件 + 发版本（`modelVersion.upsert` → `publish`） |
| `state/` | 各步产物 JSON，下一步脚本靠它续跑，**别删** |

## 典型流程（从零发一个模型）

```
1. civlib.trpc('model.upsert', {...})          建模型，拿到 modelId
2. civ_upload_all.py                           传 8 个 safetensors
3. civ_build.py                                建 4 个版本 + 挂文件 + 发版本
4. civ_gallery.py                              传图 + 挂图
5. civlib.trpc('model.publish', ...)           发模型
6. civlib.trpc('modelVersion.publish', {...})  每版都要单独 publish
7. civlib.trpc('modelVersion.update', {coverImageId, ...})  封面（图必须已发布）
```

## 五个必踩的坑（简版）

1. `post.addImage` 的 `url` 要 **UUID key**（`/api/v1/image-upload/multipart` 返回的），不是完整 URL
2. 传文件分片时 presigned PUT **不能带 Authorization 头**（会报 `Missing x-amz-content-sha256`）
3. tRPC 入参必须包在 `{"json": {...}}` 里，否则只报 "Invalid input" 没细节
4. 模型和**每个版本**都要各自 `publish`，漏了公开 API 一直 404
5. 设 tag 要用 `tagsOnModels: [{"name": "maid"}]`；传 `tags` 不报错但会被**静默忽略**（名字不存在会自动建 tag）

## 本次已发布

- 模型：https://civitai.com/models/3050927 （modelId `3050927`）
- 4 个版本 × 2 个文件，17 条图片关联
- `state/civitai_versions.json` 里有 versionId 对照表
