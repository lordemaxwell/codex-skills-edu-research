# Codex Skills for Education Research

这个仓库是给教师或研究助理分发 Codex skills 的干净发布包，当前包含两个可直接安装的 skills：

- `literature-harvest`: 面向教育经济和教育技术选题的文献搜集与 Zotero 导入 workflow。
- `stata-research`: 面向教育经济和 applied micro research 的 Stata coding 与 empirical workflow skill。

仓库只保留可发布内容，不包含本机虚拟环境、浏览器 profile、登录状态、运行结果和临时缓存。

## 仓库结构

```text
codex-skills-edu-research-release/
  README.md
  install.ps1
  .gitignore
  skills/
    literature-harvest/
      .env.example
      .gitignore
      requirements.txt
      SKILL.md
      agents/
      references/
      scripts/
    stata-research/
      SKILL.md
      agents/
      references/
```

## 安装逻辑

目标安装位置：

- 如果机器设置了 `CODEX_HOME`，安装到 `$env:CODEX_HOME\skills`
- 否则默认安装到 `$HOME\.codex\skills`

`stata-research` 是文档型 skill，复制后即可使用。  
`literature-harvest` 是 executable workflow，除了复制文件，还建议初始化 Python virtual environment、安装 Playwright 依赖并做一次环境检查。

## 推荐安装方式

在仓库根目录运行：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\install.ps1 -SetupLiteratureHarvest
```

如果老师机器上的 Python 不在默认路径，显式指定：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\install.ps1 -SetupLiteratureHarvest -PythonPath "D:\Python\Python311\python.exe"
```

如果只想复制 skills，不做依赖初始化：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\install.ps1
```

安装完成后，重启 Codex 以重新加载 skills。

## `literature-harvest` 额外说明

这个 skill 依赖：

- Python 3.11 或兼容版本
- `venv`
- `pip`
- Playwright
- Chromium 或 Edge channel
- 可选的 Zotero Web API 配置

首次安装后，可在目标技能目录中查看或编辑：

- `skills/literature-harvest/.env.example`
- 复制为 `.env` 后再填写真实配置

关键环境变量：

- `LIT_HARVEST_PYTHON`
- `LIT_HARVEST_BROWSER_CHANNEL`
- `LIT_HARVEST_CNKI_HEADLESS`
- `ZOTERO_USER_ID`
- `ZOTERO_API_KEY`

## GitHub 首次上传清单

建议上传整个仓库目录，但只包含以下内容：

- `README.md`
- `install.ps1`
- `.gitignore`
- `skills/literature-harvest/SKILL.md`
- `skills/literature-harvest/requirements.txt`
- `skills/literature-harvest/.env.example`
- `skills/literature-harvest/.gitignore`
- `skills/literature-harvest/agents/openai.yaml`
- `skills/literature-harvest/references/*.md`
- `skills/literature-harvest/scripts/*.py`
- `skills/stata-research/SKILL.md`
- `skills/stata-research/agents/openai.yaml`
- `skills/stata-research/references/*.md`

## GitHub 排除清单

以下内容不要上传：

- `skills/literature-harvest/.env`
- `skills/literature-harvest/.venv/`
- `skills/literature-harvest/profiles/`
- `skills/literature-harvest/runs/`
- `skills/literature-harvest/downloads/`
- `skills/literature-harvest/manual_import/`
- `skills/literature-harvest/scripts/__pycache__/`
- `skills/literature-harvest/**/*.pyc`
- 任意浏览器登录状态、Cookies、机构访问缓存
- 任意临时测试输出、压缩包、截图

## 分发建议

最佳做法：

1. 先把这个仓库上传到 GitHub，作为唯一正式版本。
2. 老师如果不想使用 `git clone`，直接从 GitHub 下载 ZIP 即可。
3. U 盘只作为离线传输或备份介质，不作为版本源。

底层逻辑很简单：  
GitHub 解决的是 `version control` 和后续更新；U 盘只解决一次性拷贝。
