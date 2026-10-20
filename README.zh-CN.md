# dsh-swiss-grid（中文）

给 DeepSeek Harness 增加**瑞士网格系统**能力的插件：先计算版面网格（版心、栏、基线、字级），
再生成**可直接付印的 SVG → PDF 海报、书籍跨页、杂志版面、展览图形**，并附带**网格结构图**
作为"确实对齐网格"的证明。

技能内容是对 Josef Müller-Brockmann《平面设计中的网格系统》（1961/1981）的方法整理与工具化，
不是扫描件、不是翻印：方法摘要 + 参数表 + 渲染工具链。

![用附带 builder 生成的海报示例](skills/swiss-grid-design/assets/example/poster_preview.jpg)

## 包含什么

- **技能 `swiss-grid-design`**：规则、7 步工作流、几何/字体速查、交付 QA 门槛；
- **参考文档**：方法本体、A4–A0 与 8/20/32 格参数表、SVG→PDF 输出管线与坑、检查清单、版式配方；
- **零依赖工具**：`poster_builder.py`（参数化海报生成器，含出血/裁切标记/网格图/PDF/TrimBox）、
  `grid_calculator.py`（几何与字级计算器）、`verify_print_pdf.py`（PDF 验收）；
- **示例产物**：预览图与 spec；PDF 请本地生成（不随包分发字体子集）。

## 安装

### 作为 DSH 插件（推荐）

从 GitHub 安装：

```sh
dsh plugin --profile desktop add github:summersummer-liu/dsh-swiss-grid
```

发布到 npm 后：

```sh
dsh plugin add dsh-swiss-grid
```

重启一次 `dsh web` / 桌面端让 profile 重新组合；技能目录中会出现 **`swiss-grid-design`**，
用 `/swiss-grid-design` 调用，或直接说"用网格系统做一张海报"。

> 把 `OWNER` 换成实际 GitHub 账号。插件是标准 DSH bundle：
> `package.json` → `dsh.bundle.patch` → `cordis.patch.yml` → `index.js` 注册 `skills/*/SKILL.md`。

### 只装技能（不用插件系统）

把 `skills/swiss-grid-design` 复制到 `~/.dsh/skills/` 即可，效果相同。

## 快速开始

依赖：Python 3.10+；PDF 输出需要 Microsoft Edge 或 Chromium；`pymupdf`/`Pillow` 可选
（预览与 PDF 验收）。

```sh
# 1. 算网格
python skills/swiss-grid-design/assets/grid_calculator.py --preset a2-32

# 2. 复制 builder 到项目里，改 TEXTS / ART / 颜色后生成
python poster_builder.py --preset a2-32 --outdir out --grid --pdf --preview

# 3. 验收 PDF
python skills/swiss-grid-design/assets/verify_print_pdf.py \
  --pdf out/poster_a2-32.pdf --trim 420x594 --bleed 3
```

会输出：作品 PDF（含 3mm 出血、裁切标记、TrimBox/BleedBox）、网格结构图 PDF、SVG/HTML 源、
`spec.md`、预览 JPG。验收器检查页面尺寸、TrimBox/BleedBox、真实文本、Type0（非 Type3）字体、
四角裁切标记。

## 规则一句话

所有元素吸附栏线/行线/基线；单元格高 = 整数行；字级 = 基线的倍数（24pt = 3×8 = 2×12 = 1×24）；
书刊/跨页页边距用 上1:内1:外2:下3，单页海报可用对称侧边距；图注与图片只占整行/整格；
交付永远是"作品 + 网格结构图"两件套。

## 文件结构

```
index.js                 ctx.skills 技能提供者
cordis.patch.yml         DSH bundle patch
skills/swiss-grid-design/ 技能本体（SKILL.md、references、assets）、示例
test/provider.test.js    加载器与 frontmatter 测试（node --test）
scripts/                 安装/改名脚本
```

## 版权与归属

方法归属 Josef Müller-Brockmann《Grid systems in graphic design》（Niggli, 1981；中译本
上海人民美术出版社 2016）。本项目是**独立整理与工具实现**，与作者、出版社、版权方无隶属关系，
未分发原书页面、扫描件或图版。

示例中的展览名、日期、机构、艺术家均为虚构；示例预览图使用构建机已安装字体渲染，
**不随包分发任何字体文件**。使用微软雅黑等商业字体时请自行确认授权——工具链同样支持开源
TrueType 中文字体（见技能内字体说明）。

代码与文档：MIT（见 `LICENSE`、`NOTICE`）。
