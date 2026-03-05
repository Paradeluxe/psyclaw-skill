import fitz
import sys
import re

def extract_pages(input_path, page_spec, output_path):
    # 打开输入 PDF
    doc = fitz.open(input_path)
    total_pages = len(doc)
    
    # 解析页码规格
    pages_to_extract = []
    
    # 处理逗号分隔的页码规格，如 "1,3,5-7"
    parts = page_spec.split(',')
    for part in parts:
        part = part.strip()
        # 处理范围，如 "5-7"
        if '-' in part:
            start, end = part.split('-')
            try:
                start = int(start)
                end = int(end)
                # 确保页码在有效范围内，且从1开始
                start = max(1, start)
                end = min(total_pages, end)
                if start <= end:
                    pages_to_extract.extend(range(start - 1, end))  # 转换为0-based索引
            except ValueError:
                print(f"无效的页码范围: {part}")
                sys.exit(1)
        else:
            # 处理单个页码，如 "3"
            try:
                page_num = int(part)
                # 确保页码在有效范围内
                if 1 <= page_num <= total_pages:
                    pages_to_extract.append(page_num - 1)  # 转换为0-based索引
                else:
                    print(f"页码 {page_num} 超出范围 (1-{total_pages})")
                    sys.exit(1)
            except ValueError:
                print(f"无效的页码: {part}")
                sys.exit(1)
    
    # 去重并排序
    pages_to_extract = sorted(list(set(pages_to_extract)))
    
    if not pages_to_extract:
        print("没有有效的页码可提取")
        sys.exit(1)
    
    # 创建新的 PDF 文档
    output_doc = fitz.open()
    
    # 提取指定页码
    for page_idx in pages_to_extract:
        # 复制页面到新文档
        output_doc.insert_pdf(doc, from_page=page_idx, to_page=page_idx)
    
    # 保存输出 PDF
    output_doc.save(output_path)
    
    # 关闭文档
    doc.close()
    output_doc.close()
    
    print(f"成功提取页码 {page_spec} 到 {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("用法: python extract_pages.py <输入PDF路径> <页码规格> <输出PDF路径>")
        print("页码规格示例: 1 (单个页码), 1-3 (页码范围), 1,3,5-7 (混合)")
        sys.exit(1)
    
    input_path = sys.argv[1]
    page_spec = sys.argv[2]
    output_path = sys.argv[3]
    
    extract_pages(input_path, page_spec, output_path)