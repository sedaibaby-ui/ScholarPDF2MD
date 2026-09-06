# ScholarPDF2MD

ScholarPDF2MD 是一个面向学术研究和文献整理场景的 Windows PDF 批量转 Markdown 工具。

当前版本为 **v0.1.0 源码测试版**。

程序会优先读取 PDF 自带的文字层。当文字层内容不足或质量较差时，会自动调用 Tesseract OCR 进行文字识别，并将结果保存为 Markdown 文件。

> 当前版本主要面向英文 PDF。更多语言支持和更完整的 Markdown 格式保留功能将在后续版本中逐步完善。

## Features

- 批量将文件夹中的 PDF 转换为 Markdown
- 优先直接提取 PDF 自带文字层
- 文字层不足时自动启用 OCR
- 支持 Tesseract OCR
- 自动检测常见 Tesseract 安装位置
- 自动跳过已经存在的同名 Markdown 文件
- 不覆盖已有 Markdown 文件
- 自动生成转换报告
- 记录直接提取页、OCR 页和失败页数量
- 提供简单的 Windows 文件夹选择界面
- 支持通过 `.bat` 文件快速启动

## Requirements

运行源码版本需要：

- Windows
- Python 3
- Tesseract OCR

Python 依赖：

```text
PyMuPDF
pytesseract
Pillow
```

## Installation

### 1. 下载源码

点击 GitHub 仓库页面的：

```text
Code → Download ZIP
```

解压到任意文件夹。

### 2. 安装 Python 依赖

在源码目录打开命令行，运行：

```bash
pip install -r requirements.txt
```

### 3. 安装 Tesseract OCR

程序会自动尝试寻找：

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

以及：

```text
C:\Program Files (x86)\Tesseract-OCR\tesseract.exe
```

如果 Tesseract 已经加入系统 PATH，程序也可以自动检测。

如果没有安装 Tesseract，普通文字型 PDF 仍然可以尝试直接提取，但扫描型 PDF 无法进行 OCR。

## Usage

Windows 用户可以直接双击：

```text
启动_PDF自动转MD.bat
```

也可以通过命令行运行：

```bash
python PDF自动转MD.py
```

运行后：

1. 选择存放 PDF 的文件夹。
2. 选择 Markdown 输出文件夹。
3. 程序自动扫描 PDF。
4. 对每一页判断是否可以直接提取文字。
5. 文字层不足时自动使用 OCR。
6. 转换完成后生成 Markdown 文件和转换报告。

转换报告文件名为：

```text
_PDF转MD转换报告.txt
```

## How it works

程序对 PDF 页面采用两级处理方式。

首先尝试直接读取 PDF 的文字层。

如果检测到文字层内容过少、乱码较多或有效字符比例过低，则自动将该页面渲染为图像，并使用 Tesseract OCR 进行识别。

Markdown 中会保留页面处理信息，例如：

```html
<!-- Page 12 | 直接提取 -->
```

或：

```html
<!-- Page 13 | OCR -->
```

方便后续检查转换质量。

## Current limitations

这是一个早期测试版本，目前存在以下限制：

- OCR 默认语言为英文 `eng`
- 暂时不会完整恢复 PDF 原始排版
- 表格、脚注、公式和复杂多栏布局可能无法准确还原
- Markdown 主要保存文本内容
- 当前只扫描所选文件夹中的 PDF，不递归处理子文件夹
- OCR 需要用户自行安装 Tesseract
- 当前尚未提供 EXE 或 Windows 安装包

## Version

### v0.1.0

First public source-code test release.

主要功能：

- PDF 批量转 Markdown
- 自动检测 PDF 文字层
- OCR fallback
- 跳过已有 Markdown
- 转换结果统计
- 转换报告
- Tesseract 自动检测

## Project status

🚧 Early development / Source code test version

当前项目仍处于早期开发阶段。

如果你在使用过程中发现 PDF 无法转换、OCR 失败、文字顺序异常或其他问题，欢迎通过 GitHub Issues 提交反馈。

## Planned features

后续可能加入：

- 中文 OCR
- 中英文自动识别
- 更好的双栏论文解析
- 图片提取
- 表格识别
- Markdown 标题结构恢复
- 图形化操作界面
- Windows EXE
- Windows 安装包
- 更完善的错误报告

## Disclaimer

不同 PDF 的内部结构差异很大，因此无法保证所有文件都能够完整转换。

对于重要学术文献，请在转换后核对 Markdown 内容与原始 PDF。

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See the `LICENSE` file for details.
