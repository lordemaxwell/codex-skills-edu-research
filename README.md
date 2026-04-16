# Codex Skills for Education Research

这是一个为**教育研究者、教师和研究助理**准备的工具包，用来提升文献整理和实证研究的效率。

目前包含两个可直接使用的功能模块：

* **literature-harvest**
  用于批量检索学术论文，并整理、导入到 Zotero

* **stata-research**
  用于 Stata 数据分析与实证研究支持

---

## 这个仓库适合谁？

* 做毕业论文的本科 / 硕士 / 博士生
* 从事教育研究的教师或研究助理
* 需要整理文献、处理数据的人

不需要编程基础，按步骤操作即可使用。

---

## 如何使用

### 第一步：下载

两种方式：

* 会用 GitHub：直接 `git clone`
* 不熟悉 GitHub：点击 **Code → Download ZIP** 下载并解压

---

### 第二步：安装

在项目文件夹中运行：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\install.ps1 -SetupLiteratureHarvest
```

如果你的 Python 不在默认路径，可以这样：

```powershell
PowerShell -ExecutionPolicy Bypass -File .\install.ps1 -SetupLiteratureHarvest -PythonPath "你的Python路径"
```

---

### 第三步：重启 Codex

安装完成后，重启 Codex，让新功能生效。

---

## 功能说明

### 1. literature-harvest（文献收集）

适合场景：

* 做文献综述
* 查找相关研究论文
* 整理参考文献

可以帮助你：

* 自动检索论文
* 整理文献信息
* 导入 Zotero（可选）

---

### 2. stata-research（数据分析）

适合场景：

* 进行数据分析
* 编写 Stata 代码
* 做实证研究

可以帮助你：

* 生成 Stata 代码
* 设计分析思路
* 提高分析效率

---

## 简单理解

可以把这个仓库当成一个：

👉 帮你做研究的工具包

主要解决两件事：

1. 更快找到文献
2. 更高效做数据分析

---

## 常见问题

### 需要技术基础吗？

不需要。
按照步骤操作即可使用。

---

### 必须用 Zotero 吗？

不必须，但推荐使用，方便管理文献。

---

### 可以只用其中一个模块吗？

可以，两个模块是独立的。

---

## 建议使用方式

* 写综述 → 用 `literature-harvest`
* 做分析 → 用 `stata-research`

