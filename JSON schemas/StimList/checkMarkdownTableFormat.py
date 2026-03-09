import re


def is_markdown_table(text: str) -> bool:
    """
    验证输入文本是否是 Markdown 表格格式
    
    Markdown 表格的基本结构:
    - 第一行是表头
    - 第二行是分隔线 (包含 | 和 -)
    - 后续行是数据行
    
    例如:
    | Header 1 | Header 2 |
    | -------- | -------- |
    | Cell 1   | Cell 2   |
    """
    if not text or not isinstance(text, str):
        return False
    
    lines = text.strip().split('\n')
    
    if len(lines) < 2:
        return False
    
    for line in lines:
        if not line.strip().startswith('|') or not line.strip().endswith('|'):
            return False
    
    separator_pattern = r'^\s*\|\s*[-:]+[-:\s|]*\|\s*$'
    if not re.match(separator_pattern, lines[1]):
        return False
    
    for i, line in enumerate(lines):
        if i == 1:
            continue
        
        cells = line.split('|')
        if len(cells) < 3:
            return False
    
    return True


def main():
    import sys
    
    if len(sys.argv) > 1:
        input_text = ' '.join(sys.argv[1:])
    else:
        print("请输入要验证的 Markdown 表格文本 (支持多行输入，输入空行结束):")
        lines = []
        while True:
            try:
                line = input()
                if not line.strip():
                    break
                lines.append(line)
            except EOFError:
                break
        input_text = '\n'.join(lines)
    
    if is_markdown_table(input_text):
        print("✓ 输入是有效的 Markdown 表格格式")
        sys.exit(0)
    else:
        print("✗ 输入不是有效的 Markdown 表格格式")
        sys.exit(1)


if __name__ == "__main__":
    main()
