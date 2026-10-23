# 发布到 GitHub 与 Read the Docs

仓库为 [MillenRosen/time-reshape-docs](https://github.com/MillenRosen/time-reshape-docs)，默认分支 `main`。Read the Docs 项目为 `time-reshape`，公开地址为 <https://time-reshape.readthedocs.io/zh-cn/latest/>。首次发布与验收记录见 [PUBLISHING.md](PUBLISHING.md)。以下创建步骤用于说明部署方法，已有项目不重复创建。

## 1. 先完成本地检查

```bash
source .venv/bin/activate
make check
```

构建把警告视为失败，并检查所有生成页面的站内链接、锚点、图片、脚本和 CSS 资源。中文全文搜索使用 `jieba` 分词。首次发布还需在浏览器检查桌面和手机布局、移动端目录、中文搜索及下载按钮。

## 2. 创建并上传独立仓库

在已经登录 GitHub CLI 的环境中：

```bash
gh auth status
gh repo create MillenRosen/time-reshape-docs --public \
  --description '时光重塑使用手册：安装、史实问答、遗迹复原与账号指南' \
  --source . --remote origin --push
git push origin --tags
```

执行前应确认 `gh api user --jq .login` 显示正确账号，且当前目录是文档仓库。若仓库已创建，不重复创建；核对远端后使用普通 `git push`。不要强制推送或覆盖其他已有项目。

`tools/github-docs-workflow.yml` 提供可选的 GitHub Actions 验证模板。需要时将它放入 `.github/workflows/docs.yml`；写入该位置需要 GitHub 凭据具有工作流权限。当前发布只需要公开仓库权限，使用 Read the Docs 构建。

## 3. 导入 Read the Docs

1. 登录 [Read the Docs Community](https://app.readthedocs.org/)。
2. 点击 **Add project**，在 GitHub 仓库中选择 `time-reshape-docs`。如果没有列出，检查 Read the Docs GitHub App 是否获准访问该新仓库。
3. 项目语言选 **Simplified Chinese / zh-cn**，默认分支选 `main`。Sphinx 的 `source/conf.py` 中语言代码使用 `zh_CN`，与平台 API 的写法不同。
4. 配置文件路径为根目录 `.readthedocs.yaml`，Sphinx 配置为 `source/conf.py`。
5. 提交导入并等待首个构建，确认结果为成功。
6. 打开 **View docs**，检查首页、问答指南、安装页、搜索和移动端目录。

可以手动配置仓库 URL `https://github.com/MillenRosen/time-reshape-docs` 导入；这种方式还需要配置 GitHub webhook 或安装 GitHub App，才能在后续推送时自动构建。

当前 `.readthedocs.yaml` 使用 Ubuntu 24.04、Python 3.11，并从 `source/requirements.txt` 安装锁定的文档依赖；无 GPU 依赖，不配置应用口令，不启用尚未验证的 PDF 构建。

## 4. 发布确认

- GitHub 上 `main` 的提交与本地预期提交一致。
- 本地严格构建与内部链接检查通过；启用可选 GitHub Actions 时也检查其结果。
- Read the Docs 的构建成功，构建记录对应刚上传的提交。
- 公开站点可访问，站内链接和中文搜索可用。
- 下载按钮进入实际的软件页面，不把 iOS 工程 ZIP 称为 IPA。
- 后续普通推送能触发 Read the Docs 构建，或明确记录所采用的手动构建方式。

公开地址、构建编号和验证结果应记录在 `PUBLISHING.md`，不要把“配置已准备”写成“已部署成功”。

## 5. 后续更新

更新正文、版本或下载入口 → `make check` → Git 提交与推送 → 等待 Read the Docs 构建 → 检查公开页面。保留历史标签，回溯时使用普通修复提交或对应版本构建，不重写已有历史。

当前项目通过 API 导入，采用手动触发云端构建；尚未连接 GitHub App/webhook，不应假定每次推送都会自动发布。推送后可以在 [构建列表](https://app.readthedocs.org/projects/time-reshape/builds/) 点击 **Build version / latest**，或运行：

```bash
python3 tools/build_readthedocs.py --token-file /path/outside/repo/readthedocs.token
```

凭据文件仅供本人读取，放在仓库之外。命令只输出构建地址；请求成功不等于构建成功，需核对该构建的结果及提交号。以后在项目的 **Settings → Integrations** 连接 GitHub 后，用一次正常推送验证自动构建，再更新本说明。

平台参考：[添加项目](https://docs.readthedocs.com/platform/stable/intro/add-project.html)、[配置文件](https://docs.readthedocs.com/platform/stable/config-file/)、[API v3](https://docs.readthedocs.com/platform/stable/api/v3.html)。
