# Engineering BIM - 大型工程综合技能

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

一个面向大型工程的专业技能框架，覆盖工程识图、工程量计算、CAD 转 BIM 模型三大核心能力。

## 支持的专业

| 专业 | 识图 | 算量 | BIM |
|------|:--:|:--:|:--:|
| 土建工程 | Y | Y | Y |
| 市政工程 | Y | Y | Y |
| 公路工程 | Y | Y | Y |
| 幕墙工程 | Y | Y | Y |
| 钢结构工程 | Y | Y | - |
| 隧道工程 | Y | Y | Y |

## 功能特性

- **工程识图**: 支持 DWG/DXF/IFC/SKP/PDF/点云/GIS 等格式，12 种图元类型解析，块/外部参照处理，图纸比例自动识别，版本对比
- **工程量计算**: 混凝土/模板/钢筋(16G101)/土方(3种方法)/脚手架/钢结构/隧道，GB 50500 清单编码
- **CAD 转 BIM**: 基于 IfcOpenShell 的 IFC4 模型生成，LOD100-500 分级，碰撞检测，4D/5D BIM，质量检查
- **规范参考**: 32 项国家标准（GB/JGJ/JTG/CJJ）

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 装配技能
python assemble.py
```

### Docker 运行

```bash
# 构建镜像
docker build -t engineering-bim .

# 运行容器
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  engineering-bim python /app/scripts/parse_drawing.py /app/data/sample.dxf
```

## 项目结构

```
engineering-bim/
├── SKILL.md              # 装配后的技能文件
├── assemble.py           # 模块装配脚本
├── requirements.txt      # Python 依赖
├── Dockerfile            # Docker 容器配置
├── LICENSE               # MIT 许可证
└── modules/              # 可独立编辑的模块
    ├── _header.md        # 前置元数据
    ├── 01-drawing.md     # 工程识图
    ├── 02-quantity.md    # 工程量计算
    ├── 03-bim.md         # CAD转BIM
    ├── 04-standards.md   # 专业规范
    ├── 05-workflows.md   # 完整工作流
    ├── 06-utilities.md   # 实用工具
    ├── 07-deps.md        # 依赖库
    └── 08-triggers.md    # 使用说明
```

## 模块化框架

本项目采用模块化设计，编辑 `modules/` 下的任意 `.md` 文件后运行装配脚本即可重新生成 `SKILL.md`：

```bash
python assemble.py          # 装配所有模块
python assemble.py --check  # 检查模块完整性
python assemble.py --watch  # 监听文件变化自动装配
```

添加新模块：在 `modules/` 下创建 `.md` 文件，然后在 `assemble.py` 的 `MODULES` 列表中按顺序加入。

## 依赖库

- `ezdxf` - DXF 文件读写
- `ifcopenshell` - IFC 文件创建与编辑
- `numpy` / `shapely` / `pandas` - 数值与几何计算
- `open3d` / `laspy` - 点云处理
- `openpyxl` / `matplotlib` - 报告生成
- `geopandas` / `fiona` - GIS 支持

## 许可证

MIT License - 详见 [LICENSE](LICENSE)