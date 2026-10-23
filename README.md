# 时光重塑 · 使用手册

面向使用者的中文手册，覆盖 Android **v0.11.2 / build 16** 与网页预览。独立于应用仓库，使用 Sphinx、MyST Markdown 和 Read the Docs 主题构建。

[在线阅读](https://time-reshape.readthedocs.io/zh-cn/latest/) · [PDF 使用手册](https://time-reshape.readthedocs.io/zh-cn/latest/_downloads/time-reshape-guide.pdf) · [安装与下载](https://time-reshape.readthedocs.io/zh-cn/latest/downloads.html) · [GitHub 仓库](https://github.com/MillenRosen/time-reshape-docs)

参考 [MillenRosen/tnlearn_doc](https://github.com/MillenRosen/tnlearn_doc) 的文档组织，采用玉绿与米白配色、圆圆形象、实际界面截图和手机适配。

## 本地构建

需要 Python 3.11 或更新版本。完整构建在 Linux / WSL 中运行，额外使用 Pango 与 Noto CJK 中文字体；构建不依赖应用后端、GPU、用户数据或密钥。Ubuntu 首次准备可安装 `fontconfig fonts-noto-cjk libpango-1.0-0 libpangoft2-1.0-0`。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r source/requirements.txt -r source/requirements-pdf.txt
make check
make serve
```

打开 `http://127.0.0.1:8056/`。网页位于 `build/html/`，PDF 位于 `build/pdf/TimeReshape-User-Guide.pdf`，均不提交 Git。`make pdf` 生成两种格式，`make check` 额外检查站内资源、PDF 正文、书签、链接与嵌入字体。

Windows 只预览 HTML 时可以执行以下命令。完整 PDF 构建请使用 WSL / Linux，或直接下载 Read the Docs 生成的文件；仅构建 HTML 时本机的 PDF 下载入口尚不可用。

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r source/requirements.txt
.venv\Scripts\sphinx-build -a -b html -n -W --keep-going source build/html
.venv\Scripts\python -m http.server 8056 --bind 127.0.0.1 --directory build/html
```

## 内容与维护

| 路径 | 内容 |
| --- | --- |
| `source/index.md` | 首页与导航 |
| `source/quick-start.md` | 第一次体验 |
| `source/downloads.md` | APK、iPhone 状态、安装与校验 |
| `source/guide/` | 连接、问答、影像、相机、账号与数据 |
| `source/faq.md` | 用户常见问题 |
| `source/releases.md` | 面向用户的版本说明 |
| `source/_data/release.json` | 版本、构建号、下载入口与校验值 |
| `source/_static/` | 本地样式、脚本和图片 |
| `.readthedocs.yaml` | Read the Docs 云端构建配置 |
| `tools/build_pdf.py` / `tools/pdf.css` | 从网页正文自动排版的 PDF 构建与打印样式 |
| `tools/check_pdf.py` | PDF 文字完整性、链接与嵌入字体验证 |
| `tools/github-docs-workflow.yml` | 可选的 GitHub 构建与内部链接检查模板 |

更新下载入口或安装包时，修改 `source/_data/release.json`，同步更新版本说明，再执行 `make check`。下载页链接到现有受口令保护的应用服务；手册不公开服务访问口令，也不包含安装包、账号数据库、原始用户视频或服务器配置。

发布步骤与验收见 [DEPLOYMENT.md](DEPLOYMENT.md)。图片来源见 [ASSETS.md](ASSETS.md)。

## PDF 与网页同步

PDF 从 Sphinx 生成的 HTML 提取正文，按首页目录自动收录所有内容页；保留截图、表格、提示和资料链接，并为跨页引用分配独立锚点。正文无需维护第二份副本。打印版使用 A4、嵌入中文字体、专用封面与带页码的目录；网页导航、搜索控件和重复的 PDF 下载提示不进入纸面版。

Read the Docs 在每次构建中同时生成网页与 PDF。网页下载入口使用相对地址，始终指向同一次构建的 PDF；平台浮动菜单也可下载 PDF。修改内容或打印样式后运行 `make check`，发布时按部署说明触发新构建即可。字体或 PDF 排版依赖升级后应重新检查分页与截图。
