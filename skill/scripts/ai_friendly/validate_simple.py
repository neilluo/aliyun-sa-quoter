"""简单验证工具 - 不执行代码，直接检查文件内容。

Usage:
    python -m ai_friendly.validate_simple <product_code>
"""

import re
import sys
from pathlib import Path


def validate_product_file(file_path: str):
    """验证产品定义文件。"""
    errors = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查必需常量
    required_patterns = [
        (r'^CODE\s*[:=]', "CODE"),
        (r'^NAME\s*[:=]', "NAME"),
        (r'^DISPLAY_NAME\s*[:=]', "DISPLAY_NAME"),
        (r'^CATEGORY\s*[:=]', "CATEGORY"),
        (r'^PARAMS\s*[:=]', "PARAMS"),
        (r'^MODULES\s*[:=]', "MODULES"),
        (r'^PRODUCT\s*[:=]', "PRODUCT"),
    ]
    
    for pattern, name in required_patterns:
        if not re.search(pattern, content, re.MULTILINE):
            errors.append(f"缺少必需常量: {name}")
    
    # 检查是否使用了常量
    if 'Region.' in content or 'Category.' in content or 'DiskType.' in content:
        print("✅ 使用了 ai_friendly.constants 中的常量")
    else:
        print("⚠️  未使用常量，建议从 ai_friendly.constants 导入")
    
    return errors


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m ai_friendly.validate_simple <product_code>")
        print("Example: python -m ai_friendly.validate_simple ecs")
        sys.exit(1)
    
    product_code = sys.argv[1]
    scripts_dir = Path(__file__).parent.parent
    product_file = scripts_dir / "products" / f"{product_code}.py"
    
    if not product_file.exists():
        print(f"❌ 产品文件不存在: {product_file}")
        sys.exit(1)
    
    print(f"验证产品: {product_code}")
    print(f"文件: {product_file}")
    print()
    
    errors = validate_product_file(str(product_file))
    
    if errors:
        print("❌ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        print()
        print("提示: 运行以下命令测试产品")
        print(f"  python scripts/quoter.py info {product_code}")
        print(f"  python scripts/quoter.py price {product_code} --params '{{...}}'")
        sys.exit(0)


if __name__ == "__main__":
    main()
