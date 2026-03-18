"""产品定义验证工具。

AI 提示: 运行此文件验证产品定义是否正确。

Usage:
    python -m ai_friendly.validate <product_code>
    python -m ai_friendly.validate ecs

    # 或者直接运行产品文件
    python products/ecs.py
"""

import ast
import sys
from pathlib import Path
from typing import Any, Dict, List


def validate_product_file(file_path: str) -> List[str]:
    """验证产品定义文件。
    
    Args:
        file_path: 产品文件路径
        
    Returns:
        错误列表，空列表表示验证通过。
    """
    errors = []
    
    # 动态导入模块
    import importlib.util
    spec = importlib.util.spec_from_file_location("product", file_path)
    if not spec or not spec.loader:
        return [f"无法加载文件: {file_path}"]
    
    module = importlib.util.module_from_spec(spec)
    
    # 添加必要的路径
    scripts_dir = str(Path(file_path).parent.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    
    # 设置包名以支持相对导入
    module.__package__ = "products"
    
    try:
        spec.loader.exec_module(module)
    except ImportError as e:
        # 相对导入错误，尝试静态分析
        return _validate_by_ast(file_path)
    except Exception as e:
        return [f"加载模块失败: {e}"]
    
    # 检查必需常量
    required_constants = ["CODE", "NAME", "DISPLAY_NAME", "CATEGORY", "PARAMS", "MODULES"]
    for const in required_constants:
        if not hasattr(module, const):
            errors.append(f"缺少必需常量: {const}")
    
    if errors:
        return errors
    
    # 获取常量值
    code = getattr(module, "CODE", None)
    name = getattr(module, "NAME", None)
    display_name = getattr(module, "DISPLAY_NAME", None)
    category = getattr(module, "CATEGORY", None)
    
    # 检查常量类型
    if code and not isinstance(code, str):
        errors.append("CODE 必须是字符串")
    if name and not isinstance(name, str):
        errors.append("NAME 必须是字符串")
    if display_name and not isinstance(display_name, str):
        errors.append("DISPLAY_NAME 必须是字符串")
    if category and not isinstance(category, str):
        errors.append("CATEGORY 必须是字符串")
    
    # 检查 PARAMS 结构
    params = getattr(module, "PARAMS", [])
    if not isinstance(params, list):
        errors.append("PARAMS 必须是列表")
    else:
        for i, param in enumerate(params):
            if not isinstance(param, dict):
                errors.append(f"PARAMS[{i}] 必须是字典")
                continue
            if "name" not in param:
                errors.append(f"PARAMS[{i}] 缺少 'name' 字段")
            if "label" not in param:
                errors.append(f"PARAMS[{i}] 缺少 'label' 字段")
            if "type" not in param:
                errors.append(f"PARAMS[{i}] 缺少 'type' 字段")
            if "required" not in param:
                errors.append(f"PARAMS[{i}] 缺少 'required' 字段")
    
    # 检查 MODULES 结构
    modules = getattr(module, "MODULES", [])
    if not isinstance(modules, list):
        errors.append("MODULES 必须是列表")
    else:
        for i, mod in enumerate(modules):
            if not isinstance(mod, dict):
                errors.append(f"MODULES[{i}] 必须是字典")
                continue
            if "module_code" not in mod:
                errors.append(f"MODULES[{i}] 缺少 'module_code' 字段")
            if "config_template" not in mod:
                errors.append(f"MODULES[{i}] 缺少 'config_template' 字段")
    
    # 检查 PRODUCT dict
    if not hasattr(module, "PRODUCT"):
        errors.append("缺少 PRODUCT 导出")
    else:
        product = module.PRODUCT
        if not isinstance(product, dict):
            errors.append("PRODUCT 必须是字典")
        else:
            required_fields = ["code", "name", "display_name", "params", "build_modules", "format_summary"]
            for field in required_fields:
                if field not in product:
                    errors.append(f"PRODUCT 缺少 '{field}' 字段")
            
            # 检查函数是否可调用
            for func_name in ["build_modules", "format_summary"]:
                if func_name in product and not callable(product[func_name]):
                    errors.append(f"PRODUCT['{func_name}'] 必须是可调用对象")
    
    return errors


def _validate_by_ast(file_path: str) -> List[str]:
    """通过 AST 静态分析验证文件（不执行代码）。"""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # 查找顶层赋值
        constants = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        # 尝试获取值
                        if isinstance(node.value, ast.Constant):
                            constants[target.id] = node.value.value
                        elif isinstance(node.value, ast.List):
                            constants[target.id] = []
                        elif isinstance(node.value, ast.Dict):
                            constants[target.id] = {}
        
        # 检查必需常量
        required = ["CODE", "NAME", "DISPLAY_NAME", "CATEGORY", "PARAMS", "MODULES"]
        for const in required:
            if const not in constants:
                errors.append(f"缺少必需常量: {const}")
        
        # 检查 PRODUCT dict
        has_product = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "PRODUCT":
                        has_product = True
        
        if not has_product:
            errors.append("缺少 PRODUCT 导出")
        
        return errors
        
    except SyntaxError as e:
        return [f"语法错误: {e}"]
    except Exception as e:
        return [f"AST 分析失败: {e}"]


def main():
    """命令行入口。"""
    if len(sys.argv) < 2:
        print("Usage: python -m ai_friendly.validate <product_code>")
        print("Example: python -m ai_friendly.validate ecs")
        print("")
        print("Or run product file directly:")
        print("  python products/ecs.py")
        sys.exit(1)
    
    product_code = sys.argv[1]
    
    # 查找产品文件
    scripts_dir = Path(__file__).parent.parent
    product_file = scripts_dir / "products" / f"{product_code}.py"
    
    if not product_file.exists():
        print(f"❌ 产品文件不存在: {product_file}")
        sys.exit(1)
    
    print(f"验证产品: {product_code}")
    print(f"文件: {product_file}")
    print("")
    
    errors = validate_product_file(str(product_file))
    
    if errors:
        print("❌ 验证失败:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ 验证通过")
        print("")
        print("产品信息:")
        
        # 显示产品信息
        import importlib.util
        spec = importlib.util.spec_from_file_location("product", product_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"  代码: {getattr(module, 'CODE', 'N/A')}")
            print(f"  名称: {getattr(module, 'NAME', 'N/A')}")
            print(f"  显示名称: {getattr(module, 'DISPLAY_NAME', 'N/A')}")
            print(f"  分类: {getattr(module, 'CATEGORY', 'N/A')}")
            params = getattr(module, 'PARAMS', [])
            print(f"  参数数量: {len(params)}")
            modules = getattr(module, 'MODULES', [])
            print(f"  模块数量: {len(modules)}")
        
        sys.exit(0)


if __name__ == "__main__":
    main()
