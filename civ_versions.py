# Civitai 四个版本的配置
COMMON = """
---

**触发词 / Trigger**: `{trigger}`
**推荐强度**: {strength} ｜ **采样**: 30 步 / CFG 3 / `euler` + `sgm_uniform`

**两个文件输出像素级完全相同**，只是 LoRA 内部权重排布不同：
- `{fused}` ← **推荐**，任何 ComfyUI 版本都能直接加载
- `{split}` ← 体积小 50MB，需要新版 ComfyUI（含 MOSS 原生支持）

> 想换背景就把背景写进提示词，不写会给你白底立绘。

**角色原设**: @上善无形（CC BY-NC-SA 4.0）｜ **二创参考**: @ZipZipPipe、@这个刀子真甜、@邦多利素世
**许可证**: CC BY-NC-SA 4.0（禁止商用 / 须署名 / 相同协议共享）
"""

VERSIONS = [
    dict(
        name="Q 版 · SFT 底模（chibi）",
        baseModel="MOSS Image",
        trainedWords=["qban_dafeiyu"],
        files=[("qban-sft-fused-qkv.safetensors", "Model"),
               ("qban-sft-split.safetensors", "Other")],
        desc="""**Q 版（chibi）—— 大头小身的可爱比例**

底模：[MOSS-Image-SFT](https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT)（OpenMOSS，Apache-2.0）

```
qban_dafeiyu, 1girl, solo, chibi, deep blue gradient hair, long wavy hair, ahoge,
blue eyes, whale fin ears, whale tail, white frilled maid headband, navy blue maid dress,
white apron with blue whale emblem, gold trim, standing, full body
```

可以和「正比版」**同时加载**，实现正比抱着 Q 版的构图（见预览图第一张）。
""" + COMMON.format(trigger="qban_dafeiyu", strength="0.6 ~ 0.8",
                    fused="qban-sft-fused-qkv.safetensors", split="qban-sft-split.safetensors")),
    dict(
        name="正比版 · SFT 底模（adult）",
        baseModel="MOSS Image",
        trainedWords=["dafeiyu"],
        files=[("prop-sft-fused-qkv.safetensors", "Model"),
               ("prop-sft-split.safetensors", "Other")],
        desc="""**正比版 —— 成年女性比例**

底模：[MOSS-Image-SFT](https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT)（OpenMOSS，Apache-2.0）

```
dafeiyu, 1girl, solo, adult woman, deep blue gradient hair, very long wavy hair, ahoge,
blue eyes, whale fin ears, whale tail, white frilled maid headband, navy blue maid dress,
white frilled apron with blue whale emblem, standing, full body
```

可以和「Q 版」**同时加载**，实现两人同框互动（见预览图第一、二张）。
""" + COMMON.format(trigger="dafeiyu", strength="0.4 ~ 0.6",
                    fused="prop-sft-fused-qkv.safetensors", split="prop-sft-split.safetensors")),
    dict(
        name="Q 版 · Base 底模（chibi）",
        baseModel="MOSS Image",
        trainedWords=["qban_dafeiyu"],
        files=[("qban-base-fused-qkv.safetensors", "Model"),
               ("qban-base-split.safetensors", "Other")],
        desc="""**Q 版（chibi）—— 大头小身的可爱比例**

底模：[MOSS-Image-Base](https://huggingface.co/OpenMOSS-Team/MOSS-Image-Base)（未做 SFT 的原版底模）

> 除非你明确在用 Base 底模，否则请下 **SFT** 版本。

```
qban_dafeiyu, 1girl, solo, chibi, deep blue gradient hair, long wavy hair, ahoge,
blue eyes, whale fin ears, whale tail, white frilled maid headband, navy blue maid dress,
white apron with blue whale emblem, gold trim, standing, full body
```
""" + COMMON.format(trigger="qban_dafeiyu", strength="0.6 ~ 0.8",
                    fused="qban-base-fused-qkv.safetensors", split="qban-base-split.safetensors")),
    dict(
        name="正比版 · Base 底模（adult）",
        baseModel="MOSS Image",
        trainedWords=["dafeiyu"],
        files=[("prop-base-fused-qkv.safetensors", "Model"),
               ("prop-base-split.safetensors", "Other")],
        desc="""**正比版 —— 成年女性比例**

底模：[MOSS-Image-Base](https://huggingface.co/OpenMOSS-Team/MOSS-Image-Base)（未做 SFT 的原版底模）

> 除非你明确在用 Base 底模，否则请下 **SFT** 版本。

```
dafeiyu, 1girl, solo, adult woman, deep blue gradient hair, very long wavy hair, ahoge,
blue eyes, whale fin ears, whale tail, white frilled maid headband, navy blue maid dress,
white frilled apron with blue whale emblem, standing, full body
```
""" + COMMON.format(trigger="dafeiyu", strength="0.4 ~ 0.6",
                    fused="prop-base-fused-qkv.safetensors", split="prop-base-split.safetensors")),
]

MODEL_DESC = """**DeepSeek 娘「大肥鱼」/ 鲸鱼娘 —— 穿女仆装、长着兽耳和鲸鱼尾巴的少女**

基于 [MOSS-Image](https://huggingface.co/OpenMOSS-Team/MOSS-Image-SFT)（OpenMOSS，Apache-2.0）训练的角色 LoRA。

**包含两个独立的 LoRA，四个版本**：

| | 触发词 | 说明 |
|---|---|---|
| **Q 版** | `qban_dafeiyu` | chibi 比例，大头小身 |
| **正比版** | `dafeiyu` | 成年女性比例 |

画风统一，可以单独使用，也可以**同时加载**——正比抱着 Q 版、两人同框互动都是可以的。

每个形态都提供 **SFT 底模** 和 **Base 底模** 两个版本。**大多数人选 SFT 就对了**。

---

## 推荐设置

- **强度**：Q 版 0.6 ~ 0.8 ｜ 正比版 0.4 ~ 0.6
- **采样**：30 步 / CFG 3 / `euler` + `sgm_uniform`
- **ComfyUI**：需要带 MOSS 支持的版本

## ⚠️ 旧版 ComfyUI 兼容性

如果你用旧版 ComfyUI 加载 `*-split.safetensors`，会看到大量：

```
lora key not loaded: lora_unet_layers_N_proj_q.lora_up.weight
```

**这不是模型坏了**，是 ComfyUI 版本太旧、没有 MOSS 的 split→fused 键映射。三种解法：

1. 换 `*-fused-qkv.safetensors`（**推荐**，立即可用）
2. 升级 ComfyUI 到含 MOSS 原生支持的版本（commit `b1a247c` 或更新）
3. 如果你在用 `comfyui-moss-Image` 自定义节点，它定义的 `MOSSImage` 类与核心同名不同类，会让映射判定失败——需要让该节点继承 `comfy.model_base.MOSSImage`

---

## 版权与来源

**角色原设**：[@上善无形](https://www.bilibili.com/opus/1231977657712771073)（B站）｜ **CC BY-NC-SA 4.0**
**形象二创参考**：@ZipZipPipe、@这个刀子真甜、@邦多利素世（B站）

训练素材取自上述创作者公开发布的设定图（均开放二创），以及以这些设定为视觉参考生成的辅助训练图。

## 许可证

**CC BY-NC-SA 4.0** —— 与角色原设同协议
- ⛔ 禁止商业使用（售卖、广告、付费服务等）
- ✅ 转载 / 二创须署名上述作者
- ✅ 衍生作品须采用相同协议

底模 MOSS-Image 本身为 Apache-2.0，由 OpenMOSS 发布。

**HuggingFace 镜像**：[WYR233/MOSS-Image-LoRA-DeepSeek-Whale-Girl-DaFeiYu](https://huggingface.co/WYR233/MOSS-Image-LoRA-DeepSeek-Whale-Girl-DaFeiYu)
"""

# Civitai tag 名单（2026-11-14 已实测全部生效）
# ⚠️ 写 tag 用 civ_tags.py：接口吃的是 tagsOnModels=[{"name": ...}]，不是这里的列表本身；
#    名字不存在会自动建 tag；anime / character 是分类(isCategory)，不能当普通 tag 塞。
TAGS = ["moss image", "moss-image", "deepseek", "whale girl", "大肥鱼", "dafeiyu",
        "鲸鱼娘", "chibi", "comfyui", "女仆", "maid"]
