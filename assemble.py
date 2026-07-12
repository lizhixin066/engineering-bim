"""
engineering-bim 技能装配脚本
====================
将 modules/ 目录下的模块文件按顺序拼接为 SKILL.md

用法:
    python assemble.py           # 默认装配
    python assemble.py --watch   # 监听文件变化自动装配 (需安装 watchdog)
    python assemble.py --check   # 仅检查模块完整性，不装配

模块加载顺序由 MODULES 列表定义。
添加新模块: 在 modules/ 下创建 .md 文件，然后加入 MODULES 列表。
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# 框架配置 - 修改此列表即可调整模块顺序和内容
# ============================================================

SKILL_DIR = Path(__file__).parent
MODULES_DIR = SKILL_DIR / "modules"
OUTPUT_FILE = SKILL_DIR / "SKILL.md"

# 模块加载顺序（按文件名排序确保一致性）
MODULES = [
    "_header.md",       # 前置元数据 + 技能概述
    "01-drawing.md",    # 工程识图
    "02-quantity.md",   # 工程量计算
    "03-bim.md",        # CAD转BIM
    "04-standards.md",  # 专业规范
    "05-workflows.md",  # 完整工作流
    "06-utilities.md",  # 实用工具
    "07-deps.md",       # 依赖库
    "08-triggers.md",   # 使用说明
    "09-pricing.md",    # 工程造价计价
    "10-safety.md",     # 施工安全计算
    "11-carbon.md",     # 碳排放与绿色建筑
    "12-schedule.md",   # 施工组织与进度
    "13-excel.md",      # Excel计算表生成器
    "14-api-registry.md", # 函数注册表 (API Registry)
]


def assemble() -> str:
    """
    装配所有模块为完整的 SKILL.md 内容
    返回: 装配后的完整内容
    """
    parts = []
    missing = []
    total_size = 0

    for module_name in MODULES:
        module_path = MODULES_DIR / module_name
        if not module_path.exists():
            missing.append(module_name)
            parts.append(f"\n<!-- [WARNING] 模块缺失: {module_name} -->\n")
            continue

        content = module_path.read_text(encoding="utf-8")
        parts.append(content)
        total_size += len(content)

    # 末尾添加生成时间戳
    parts.append(f"\n<!-- 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 模块数: {len(MODULES) - len(missing)} | 文件大小: {total_size:,} bytes -->\n")

    result = "\n\n".join(parts)

    # 清理多余空行
    while "\n\n\n" in result:
        result = result.replace("\n\n\n", "\n\n")

    if missing:
        print(f"[WARNING] 缺失模块: {', '.join(missing)}")

    return result


def check() -> bool:
    """检查模块完整性"""
    all_ok = True
    print(f"模块目录: {MODULES_DIR}")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"\n模块列表 ({len(MODULES)} 个):")

    for i, name in enumerate(MODULES):
        path = MODULES_DIR / name
        exists = "OK" if path.exists() else "MISSING"
        size = path.stat().st_size if path.exists() else 0
        if not path.exists():
            all_ok = False
        print(f"  [{i+1:2d}] {exists:7s} {name:25s} ({size:>8,} bytes)")

    print(f"\n状态: {'全部就绪' if all_ok else '存在缺失模块'}")
    return all_ok


def build():
    """执行装配"""
    print("=" * 60)
    print("  engineering-bim 技能装配")
    print("=" * 60)

    check()

    print("\n正在装配...")
    content = assemble()

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    size = OUTPUT_FILE.stat().st_size

    print(f"装配完成 -> {OUTPUT_FILE}")
    print(f"文件大小: {size:,} bytes ({len(content):,} chars)")
    print(f"模块数: {len(MODULES)}")


def watch():
    """监听模式（需要 watchdog）"""
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("[ERROR] 监听模式需要安装 watchdog: pip install watchdog")
        sys.exit(1)

    class ModuleHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith('.md'):
                print(f"\n[检测到变更] {os.path.basename(event.src_path)}")
                build()

    print("监听模式启动，修改 modules/*.md 将自动装配...")
    print("按 Ctrl+C 退出\n")

    observer = Observer()
    observer.schedule(ModuleHandler(), str(MODULES_DIR), recursive=False)
    observer.start()

    try:
        while True:
            observer.join(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n监听已停止")
    observer.join()


if __name__ == "__main__":
    os.chdir(SKILL_DIR)

    if "--watch" in sys.argv or "-w" in sys.argv:
        # 先构建一次再监听
        build()
        watch()
    elif "--check" in sys.argv or "-c" in sys.argv:
        check()
    else:
        build()