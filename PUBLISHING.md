# 发布记录

本手册独立于应用代码，覆盖 **时光重塑 v0.11.2 / build 16**。

| 项目 | 地址或结果 |
| --- | --- |
| 公开手册 | <https://time-reshape.readthedocs.io/zh-cn/latest/> |
| 安装与下载 | <https://time-reshape.readthedocs.io/zh-cn/latest/downloads.html> |
| GitHub | <https://github.com/MillenRosen/time-reshape-docs> |
| 分支 | `main` |
| Read the Docs | `time-reshape`，语言 `zh-cn`，Python 3.11 |
| 首轮内容提交 | `22730ddec6bd3082c10fc3447067533c68e2abcf` |
| 首轮构建验收 | [35344949](https://app.readthedocs.org/projects/time-reshape/builds/35344949/)，2026-10-23，成功 |

构建使用仓库根目录的 `.readthedocs.yaml`。手册不依赖应用服务器运行；安装包与网页预览链接仍指向现有应用服务，下载时按页面提示输入服务访问口令。未公开任何服务口令或用户数据。

## 维护与回溯

后续更新正文、截图、安装包信息或地址，提交到 `main` 后手动触发 Read the Docs 构建，核对提交与构建结果。当前未配置自动构建的 GitHub 集成；操作方法见 [DEPLOYMENT.md](DEPLOYMENT.md)。

由于开发服务器到 GitHub 常规 Git 传输线路不稳定，首次上传使用 GitHub 官方 Git Data API，上传后逐项核对 Git blob、tree 与 commit 哈希，确保远端和本地一致。后续网络正常时可使用常规 `git push origin main`。

文档版本标签为 `docs-v0.11.2`，可在 GitHub 或本地检出该标签回溯本次交付。

本地严格构建、站内资源与手机浏览器检查见 [checks/validation.json](checks/validation.json)。上线后的浏览器检查另行保存在 `checks/readthedocs.json`，其中明确标明验证时的提交和构建。

完整在线验收对应 [构建 35345257](https://app.readthedocs.org/projects/time-reshape/builds/35345257/) 与提交 `fe8e536d4fc2bf4d4cbd989b53f159bc64df5516`：12 个内容页、1440 / 390 像素视口、手机目录、中文搜索、下载链接与校验值通过，未发现页面脚本或 HTTP 错误。此后补充的窄屏表格优化在 360 / 390 像素本地浏览器检查通过。最终 `main` 的云端构建状态可在 [构建列表](https://app.readthedocs.org/projects/time-reshape/builds/) 按提交号核对。

## PDF 阅读版

PDF 复用全部 12 个内容页，增加封面、带页码的目录、章节书签和页眉页脚；保留图片、表格与链接，使用 A4 和嵌入的中文字体。初版为 23 页。生成文件不直接提交 Git，由同一份网页源码和 `tools/pdf.css` 构建，便于后续同步更新。

- [下载 PDF](https://time-reshape.readthedocs.io/zh-cn/latest/_downloads/time-reshape-guide.pdf)
- [平台 PDF 下载](https://time-reshape.readthedocs.io/_/downloads/zh-cn/latest/pdf/)
- 本地输出：`build/pdf/TimeReshape-User-Guide.pdf`
- 本地验收：`checks/pdf.json`（页数、正文完整性、目录目标、链接与嵌入字体）

网页版的首页、安装下载页和各页页脚提供 PDF 入口。Read the Docs 的 PDF 步骤会自动生成和检查文件，然后随网页发布。字体库版本不同可能带来轻微分页差异；变更排版依赖时需重新检查视觉效果。
