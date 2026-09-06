import pymupdf as fitz
import pytesseract
from PIL import Image
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import io
import time
import shutil


# ============================================================
# 自动查找 Tesseract OCR
# ============================================================

def find_tesseract():

    # 先尝试从系统 PATH 中寻找
    tesseract_cmd = shutil.which("tesseract")

    if tesseract_cmd:
        return tesseract_cmd

    # 如果 PATH 中没有，再检查 Windows 常见安装位置
    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]

    for path in possible_paths:

        if Path(path).exists():
            return path

    return None


tesseract_cmd = find_tesseract()

if tesseract_cmd:

    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


# ============================================================
# 判断一页 PDF 自带的文字层是否可以直接使用
# ============================================================

def text_layer_is_good(text):

    if not text:
        return False

    text = text.strip()

    # 文字太少，可能是扫描页
    if len(text) < 60:
        return False

    # 如果出现大量 Unicode 乱码替代字符，
    # 则认为文字层质量较差
    if text.count("\ufffd") / max(len(text), 1) > 0.01:
        return False

    # 至少应包含一定数量的字母或数字
    useful_chars = sum(
        c.isalnum()
        for c in text
    )

    if useful_chars / max(len(text), 1) < 0.20:
        return False

    return True


# ============================================================
# OCR 单页
# ============================================================

def ocr_page(page):

    # 如果电脑没有找到 Tesseract，
    # 此时无法进行 OCR
    if not tesseract_cmd:

        raise RuntimeError(
            "未找到 Tesseract OCR。"
            "请先安装 Tesseract，"
            "或将 tesseract.exe 加入系统 PATH。"
        )

    # 提高页面渲染清晰度，方便 OCR
    matrix = fitz.Matrix(
        2.5,
        2.5
    )

    pix = page.get_pixmap(
        matrix=matrix,
        alpha=False
    )

    image = Image.open(
        io.BytesIO(
            pix.tobytes("png")
        )
    )

    text = pytesseract.image_to_string(
        image,
        lang="eng",
        config="--psm 3"
    )

    return text


# ============================================================
# 转换一个 PDF
# ============================================================

def convert_pdf(
    pdf_path,
    output_folder
):

    doc = fitz.open(
        pdf_path
    )

    md_content = [
        f"# {pdf_path.stem}",
        ""
    ]

    direct_pages = 0
    ocr_pages = 0
    failed_pages = 0

    total_pages = len(doc)

    for page_number, page in enumerate(
        doc,
        1
    ):

        print(
            f"    第 {page_number}/{total_pages} 页：",
            end="",
            flush=True
        )

        try:

            # =================================================
            # 优先读取 PDF 自带文字层
            # =================================================

            text = page.get_text(
                "text",
                sort=True
            )

            # =================================================
            # 文字层正常
            # =================================================

            if text_layer_is_good(text):

                direct_pages += 1

                method = "直接提取"

                print(
                    "直接提取"
                )

            # =================================================
            # 文字层不足，自动 OCR
            # =================================================

            else:

                print(
                    "文字层不足，OCR...",
                    end="",
                    flush=True
                )

                text = ocr_page(
                    page
                )

                ocr_pages += 1

                method = "OCR"

                print(
                    "完成"
                )

        except Exception as e:

            failed_pages += 1

            text = ""

            method = "失败"

            print(
                f"失败：{e}"
            )

        # =====================================================
        # Markdown 中加入 PDF 页码
        # =====================================================

        md_content.append(
            f"<!-- Page {page_number} | {method} -->"
        )

        md_content.append(
            ""
        )

        if text.strip():

            md_content.append(
                text.strip()
            )

        else:

            md_content.append(
                "<!-- 本页没有提取到有效文字 -->"
            )

        md_content.append(
            ""
        )

    doc.close()

    # ========================================================
    # 输出 Markdown
    # ========================================================

    output_path = (
        output_folder /
        f"{pdf_path.stem}.md"
    )

    output_path.write_text(
        "\n".join(md_content),
        encoding="utf-8"
    )

    return {
        "pages": total_pages,
        "direct": direct_pages,
        "ocr": ocr_pages,
        "failed_pages": failed_pages
    }


# ============================================================
# 创建图形界面
# ============================================================

root = tk.Tk()

root.withdraw()


# ============================================================
# 检查 Tesseract 状态
# ============================================================

if tesseract_cmd:

    print(
        f"Tesseract OCR：{tesseract_cmd}"
    )

else:

    messagebox.showwarning(
        "未找到 Tesseract OCR",
        "程序没有找到 Tesseract OCR。\n\n"
        "普通文字型 PDF 仍然可以直接提取。\n"
        "但是扫描型 PDF 无法进行 OCR。\n\n"
        "如果需要识别扫描型 PDF，"
        "请先安装 Tesseract OCR。"
    )


# ============================================================
# 选择 PDF 文件夹
# ============================================================

messagebox.showinfo(
    "PDF 批量转 Markdown",
    "请选择存放 PDF 的文件夹。"
)

input_folder = filedialog.askdirectory(
    title="选择 PDF 文件夹"
)

if not input_folder:

    messagebox.showinfo(
        "已取消",
        "没有选择 PDF 文件夹。"
    )

    raise SystemExit


# ============================================================
# 选择 Markdown 输出文件夹
# ============================================================

messagebox.showinfo(
    "PDF 批量转 Markdown",
    "请选择 Markdown 输出文件夹。\n\n"
    "如果已经有部分 Markdown，程序会自动跳过同名文件。"
)

output_folder = filedialog.askdirectory(
    title="选择 Markdown 输出文件夹"
)

if not output_folder:

    messagebox.showinfo(
        "已取消",
        "没有选择输出文件夹。"
    )

    raise SystemExit


input_folder = Path(
    input_folder
)

output_folder = Path(
    output_folder
)


# ============================================================
# 扫描文件夹
# ============================================================

all_items = list(
    input_folder.iterdir()
)

pdf_files = []

suspicious_pdf_files = []


for file in all_items:

    if not file.is_file():
        continue

    # ========================================================
    # 正常 PDF
    # ========================================================

    if file.suffix.lower() == ".pdf":

        pdf_files.append(
            file
        )

    # ========================================================
    # 文件名中出现 pdf，
    # 但扩展名却不是标准 .pdf
    #
    # 用于发现可能被程序漏掉的异常 PDF
    # ========================================================

    elif "pdf" in file.name.lower():

        suspicious_pdf_files.append(
            file
        )


pdf_files = sorted(
    pdf_files,
    key=lambda x: x.name.lower()
)


# ============================================================
# 没有 PDF
# ============================================================

if not pdf_files:

    messagebox.showwarning(
        "没有找到 PDF",
        "这个文件夹里没有识别到 PDF 文件。"
    )

    raise SystemExit


# ============================================================
# 显示扫描结果
# ============================================================

print()
print("=" * 70)
print("PDF 文件扫描")
print("=" * 70)

print(
    f"文件夹内项目总数：{len(all_items)}"
)

print(
    f"识别到 PDF：{len(pdf_files)}"
)


# ============================================================
# 如果发现疑似 PDF
# ============================================================

if suspicious_pdf_files:

    print()

    print(
        "⚠ 发现以下文件名包含 PDF，"
        "但扩展名不是标准 .pdf："
    )

    print()

    for file in suspicious_pdf_files:

        print(
            f"    {repr(file.name)}"
        )

        print(
            f"        扩展名：{repr(file.suffix)}"
        )

    print()


print("=" * 70)


# ============================================================
# 开始批量转换
# ============================================================

print()
print("=" * 70)
print("PDF 批量转 Markdown")
print("=" * 70)

print(
    f"PDF 文件夹：{input_folder}"
)

print(
    f"输出文件夹：{output_folder}"
)

print(
    f"PDF 数量：{len(pdf_files)}"
)

print("=" * 70)
print()


# ============================================================
# 转换统计
# ============================================================

successful = []

failed = []

skipped = []


start_time = time.time()


# ============================================================
# 批量处理 PDF
# ============================================================

for index, pdf_path in enumerate(
    pdf_files,
    1
):

    print()

    print(
        f"[{index}/{len(pdf_files)}] "
        f"{pdf_path.name}"
    )


    # ========================================================
    # 计算对应 Markdown 文件路径
    # ========================================================

    md_path = (
        output_folder /
        f"{pdf_path.stem}.md"
    )


    # ========================================================
    # 如果同名 Markdown 已经存在
    #
    # 直接跳过
    # 不打开 PDF
    # 不 OCR
    # 不覆盖原文件
    # ========================================================

    if md_path.exists():

        skipped.append(
            pdf_path.name
        )

        print(
            "    ↷ 已存在同名 MD，直接跳过"
        )

        continue


    # ========================================================
    # 不存在同名 Markdown
    # 开始正常转换
    # ========================================================

    try:

        result = convert_pdf(
            pdf_path,
            output_folder
        )

        successful.append(
            (
                pdf_path.name,
                result
            )
        )

        print(
            f"    ✓ 完成 | "
            f"总页数 {result['pages']} | "
            f"直接提取 {result['direct']} | "
            f"OCR {result['ocr']} | "
            f"失败页 {result['failed_pages']}"
        )


    except Exception as e:

        failed.append(
            (
                pdf_path.name,
                str(e)
            )
        )

        print(
            f"    ✗ 整篇失败：{e}"
        )


# ============================================================
# 计算耗时
# ============================================================

elapsed = (
    time.time() -
    start_time
)


# ============================================================
# 生成转换报告
# ============================================================

report_path = (
    output_folder /
    "_PDF转MD转换报告.txt"
)


with open(
    report_path,
    "w",
    encoding="utf-8"
) as report:

    report.write(
        "PDF 批量转 Markdown 转换报告\n"
    )

    report.write(
        "=" * 60 +
        "\n\n"
    )


    # ========================================================
    # 基本信息
    # ========================================================

    report.write(
        f"PDF 文件夹：{input_folder}\n"
    )

    report.write(
        f"输出文件夹：{output_folder}\n"
    )

    report.write(
        f"PDF 总数：{len(pdf_files)}\n"
    )

    report.write(
        f"新转换成功：{len(successful)}\n"
    )

    report.write(
        f"已存在，跳过：{len(skipped)}\n"
    )

    report.write(
        f"失败：{len(failed)}\n"
    )

    report.write(
        f"总耗时：{elapsed / 60:.1f} 分钟\n"
    )

    if tesseract_cmd:

        report.write(
            f"Tesseract：{tesseract_cmd}\n\n"
        )

    else:

        report.write(
            "Tesseract：未找到\n\n"
        )


    # ========================================================
    # 疑似异常 PDF
    # ========================================================

    if suspicious_pdf_files:

        report.write(
            "========== 疑似异常 PDF ==========\n\n"
        )

        report.write(
            "以下文件名包含 PDF，"
            "但扩展名不是标准 .pdf，"
            "因此没有进行转换：\n\n"
        )

        for file in suspicious_pdf_files:

            report.write(
                f"{file.name}\n"
            )

            report.write(
                f"扩展名：{repr(file.suffix)}\n\n"
            )


    # ========================================================
    # 成功文件
    # ========================================================

    report.write(
        "========== 新转换成功文件 ==========\n\n"
    )


    if successful:

        for name, result in successful:

            report.write(
                f"{name}\n"
            )

            report.write(
                f"总页数：{result['pages']}\n"
            )

            report.write(
                f"直接提取：{result['direct']}\n"
            )

            report.write(
                f"OCR：{result['ocr']}\n"
            )

            report.write(
                f"失败页：{result['failed_pages']}\n\n"
            )

    else:

        report.write(
            "本次没有新的 PDF 需要转换。\n\n"
        )


    # ========================================================
    # 已存在，跳过
    # ========================================================

    if skipped:

        report.write(
            "\n"
            "========== 已存在，跳过文件 ==========\n\n"
        )

        for name in skipped:

            report.write(
                f"{name}\n"
            )


    # ========================================================
    # 失败文件
    # ========================================================

    if failed:

        report.write(
            "\n"
            "========== 转换失败文件 ==========\n\n"
        )

        for name, error in failed:

            report.write(
                f"{name}\n"
            )

            report.write(
                f"错误：{error}\n\n"
            )


# ============================================================
# 控制台最终结果
# ============================================================

print()
print("=" * 70)
print("全部处理完成")
print("=" * 70)

print(
    f"PDF 总数：{len(pdf_files)}"
)

print(
    f"新转换成功：{len(successful)}"
)

print(
    f"已存在，跳过：{len(skipped)}"
)

print(
    f"失败：{len(failed)}"
)

if suspicious_pdf_files:

    print(
        f"疑似异常 PDF：{len(suspicious_pdf_files)}"
    )

print(
    f"耗时：{elapsed / 60:.1f} 分钟"
)

print(
    f"输出位置：{output_folder}"
)

print(
    f"转换报告：{report_path}"
)

print("=" * 70)


# ============================================================
# 最终弹窗
# ============================================================

message = (
    f"PDF 总数：{len(pdf_files)}\n"
    f"新转换成功：{len(successful)}\n"
    f"已存在，跳过：{len(skipped)}\n"
    f"失败：{len(failed)}\n"
)

if suspicious_pdf_files:

    message += (
        f"疑似异常 PDF："
        f"{len(suspicious_pdf_files)}\n"
    )

message += (
    "\n"
    f"耗时：{elapsed / 60:.1f} 分钟\n\n"
    f"Markdown 已保存到：\n"
    f"{output_folder}\n\n"
    f"转换报告：\n"
    f"{report_path}"
)


messagebox.showinfo(
    "转换完成",
    message
)