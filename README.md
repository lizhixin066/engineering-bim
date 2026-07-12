# Engineering BIM - 大型工程综合技能

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

一个面向大型工程的专业技能框架，覆盖工程识图、工程量计算、CAD 转 BIM 模型、造价计价、施工安全、碳排放、进度计划、Excel计算表八大核心能力。

## 支持的专业

| 专业 | 识图 | 算量 | BIM | 计价 | 安全 | 碳排放 | 进度 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 土建工程 | Y | Y | Y | Y | Y | Y | Y |
| 市政工程 | Y | Y | Y | Y | Y | Y | Y |
| 公路工程 | Y | Y | Y | Y | Y | - | Y |
| 幕墙工程 | Y | Y | Y | Y | - | Y | Y |
| 钢结构工程 | Y | Y | - | Y | Y | Y | Y |
| 隧道工程 | Y | Y | Y | Y | Y | - | Y |

## 功能特性

### 核心能力
- **工程识图**: 支持 DWG/DXF/IFC/SKP/PDF/点云/GIS 等格式，12 种图元类型解析，块/外部参照处理，图纸比例自动识别，版本对比
- **工程量计算**: 混凝土/模板/钢筋(22G101)/土方(3种方法)/脚手架/钢结构/隧道/防水/保温/装饰/门窗/屋面，GB 50500 清单编码，完整公式推导
- **CAD 转 BIM**: 基于 IfcOpenShell 的 IFC4 模型生成，LOD100-500 分级，碰撞检测，4D/5D BIM，质量检查

### 扩展能力
- **工程造价计价**: 综合单价计算、人工/材料/机械单价表、措施费/规费/税金、材料价差调整、工程报价书生成
- **施工安全计算**: 脚手架承载力、模板支撑体系、深基坑支护(Rankine土压力)、塔吊基础验算、临边防护、临时用电
- **碳排放与绿色建筑**: 建材碳排放因子表、全寿命期碳排放计算、装配率计算、绿色建筑星级评价(GB/T 50378)、建筑能耗分析
- **施工组织与进度**: 双代号网络计划(CPM)、横道图生成、资源动态曲线、资源均衡优化、挣值法进度跟踪(EVM)
- **Excel计算表生成器**: 多模板(混凝土/钢筋/清单/造价)、公式联动、自动汇总、条件格式、数据校验

### 规范参考
- 120+ 项国家规范标准（GB/GB-T/JGJ/CJJ/JTG/TB/CECS）
- 覆盖通用基础、土建、市政、公路、幕墙、钢结构、隧道七大类
- 含规范使用优先级和版本替代检查清单

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
├── docker-compose.yml    # Docker Compose 配置
├── LICENSE               # MIT 许可证
├── push_to_github.py     # GitHub 推送工具
└── modules/              # 可独立编辑的模块 (14个)
    ├── _header.md        # 前置元数据
    ├── 01-drawing.md     # 工程识图
    ├── 02-quantity.md    # 工程量计算 (含公式与系数表)
    ├── 03-bim.md         # CAD转BIM
    ├── 04-standards.md   # 全部国家规范 (120+条)
    ├── 05-workflows.md   # 完整工作流
    ├── 06-utilities.md   # 实用工具
    ├── 07-deps.md        # 依赖库
    ├── 08-triggers.md    # 使用说明
    ├── 09-pricing.md     # 工程造价计价
    ├── 10-safety.md      # 施工安全计算
    ├── 11-carbon.md      # 碳排放与绿色建筑
    ├── 12-schedule.md    # 施工组织与进度
    └── 13-excel.md       # Excel计算表生成器
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
- `openpyxl` / `matplotlib` / `xlsxwriter` - 报告与Excel生成
- `geopandas` / `fiona` - GIS 支持

## 许可证

MIT License - 详见 [LICENSE](LICENSE)
