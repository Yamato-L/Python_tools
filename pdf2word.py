from pdf2docx import Converter


def pdf_to_word(pdf_path, word_path):
    # 创建转换器对象
    cv = Converter(pdf_path)

    # 转换PDF为Word文档
    cv.convert(word_path, start=0, end=None)

    # 关闭转换器
    cv.close()
    print(f"PDF已成功转换为Word文档：{word_path}")


# 使用示例
pdf_path = "example.pdf"  # 替换为你的PDF文件路径
word_path = "output.docx"  # 输出的Word文件路径
pdf_to_word(pdf_path, word_path)

