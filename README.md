# 时光重塑 · 使用手册

面向使用者的中文手册，覆盖 Android **v0.11.2 / build 16** 与网页预览。独立于应用仓库，使用 Sphinx、MyST Markdown 和 Read the Docs 主题构建。

[在线阅读](https://time-reshape.readthedocs.io/zh-cn/latest/) · [安装与下载](https://time-reshape.readthedocs.io/zh-cn/latest/downloads.html) · [GitHub 仓库](https://github.com/MillenRosen/time-reshape-docs)

参考 [MillenRosen/tnlearn_doc](https://github.com/MillenRosen/tnlearn_doc) 的文档组织，采用玉绿与米白配色、圆圆形象、实际界面截图和手机适配。

## 本地构建

需要 Python 3.11 或更新版本。构建不依赖应用后端、GPU、用户数据或密钥。

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r source/requirements.txt
make check
make serve
```

打开 `http://127.0.0.1:8056/`。生成文件位于 `build/html/`，不提交 Git。Windows 可以直接执行：

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python -m pip install -r source/requirements.txt
.venv\Scripts\sphinx-build -b html -n -W --keep-going source build/html
.venv\Scripts\python tools/check_site.py build/html
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
| `tools/github-docs-workflow.yml` | 可选的 GitHub 构建与内部链接检查模板 |

更新下载入口或安装包时，修改 `source/_data/release.json`，同步更新版本说明，再执行 `make check`。下载页链接到现有受口令保护的应用服务；手册不公开服务访问口令，也不包含安装包、账号数据库、原始用户视频或服务器配置。

发布步骤与验收见 [DEPLOYMENT.md](DEPLOYMENT.md)。图片来源见 [ASSETS.md](ASSETS.md)。
