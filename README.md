# Engineering BIM - 大型工程综合技能

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Modules](https://img.shields.io/badge/Modules-14-green.svg)](#项目结构)
[![Standards](https://img.shields.io/badge/规范-120%2B-blue.svg)](#规范参考)
[![SKILL.md](https://img.shields.io/badge/SKILL.md-186KB-green.svg)](SKILL.md)

> 面向大型工程的专业技能框架，覆盖工程全生命周期的识图、算量、BIM、计价、安全、碳排放、进度、Excel八大核心能力。
> 支持六大工程专业：土建 / 市政 / 公路 / 幕墙 / 钢结构 / 隧道。

---

## 目录

- [功能概览](#功能概览)
- [支持的专业](#支持的专业)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [项目统计](#项目统计)
- [快速开始](#快速开始)
- [使用示例](#使用示例)
- [项目结构](#项目结构)
- [模块化框架](#模块化框架)
- [规范参考](#规范参考)
- [依赖库](#依赖库)
- [更新日志](#更新日志)
- [许可证](#许可证)

---

## 功能概览

```
┌──────────────────────────────────────────────────────────────┐
│                  Engineering BIM 技能框架                     │
├────────────┬────────────┬────────────┬───────────────────────┤
│  工程识图   │  工程量计算  │  CAD转BIM  │  工程造价计价          │
│  12种图元   │  公式推导    │  IFC4标准  │  综合单价/报价书       │
│  图纸对比   │  GB清单编码  │  碰撞检测  │  措施费/规费/税金      │
├────────────┼────────────┼────────────┼───────────────────────┤
│  施工安全   │  碳排放计算  │  进度计划   │  Excel计算表          │
│  脚手架/基坑 │  碳排放因子  │  CPM/横道图 │  公式联动/自动汇总    │
│  塔吊/用电   │  绿建评价    │  挣值法EVM │  4种模板              │
└────────────┴────────────┴────────────┴───────────────────────┘
         土建 │ 市政 │ 公路 │ 幕墙 │ 钢结构 │ 隧道
```

## 支持的专业

| 专业 | 识图 | 算量 | BIM | 计价 | 安全 | 碳排放 | 进度 | Excel |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 土建工程 | Y | Y | Y | Y | Y | Y | Y | Y |
| 市政工程 | Y | Y | Y | Y | Y | Y | Y | Y |
| 公路工程 | Y | Y | Y | Y | Y | - | Y | Y |
| 幕墙工程 | Y | Y | Y | Y | - | Y | Y | Y |
| 钢结构工程 | Y | Y | - | Y | Y | Y | Y | Y |
| 隧道工程 | Y | Y | Y | Y | Y | - | Y | Y |

## 功能特性

### 核心能力

#### 1. 工程识图
- 支持格式：DWG/DXF/IFC/SKP/PDF/点云(LAS/LAZ/PLY)/GIS(SHP/GeoJSON/KML)
- 12种图元类型解析：LINE/POLYLINE/ARC/CIRCLE/TEXT/DIMENSION/INSERT/HATCH/SPLINE/ELLIPSE/POINT
- 图块定义提取与嵌套块递归展开，外部参照(Xref)处理
- 图纸比例自动识别（A0~A4图幅 + DIMSCALE）
- 图层分类识别（20+关键字映射），图纸版本对比

#### 2. 工程量计算
- 混凝土：含模板、扣减规则、梁柱节点规则、独立/条形/筏板基础
- 钢筋：锚固长度公式推导、搭接长度、C20~C50锚固表、梁/柱/板/墙/基础五类钢筋算量
- 土方：放坡系数表(人工/机械)、工作面宽度、沟槽/基坑/一般土方、方格网法(八公式零线处理)
- 构造柱/过梁/圈梁/压顶：马牙槎系数(一字0.06/L形0.10/丁字0.13/十字0.19)
- 砌体：砖用量表(115墙552/240墙529/365墙522/490墙518块/m³)
- 防水/保温/装饰装修/门窗/屋面工程量
- 市政/公路/幕墙/钢结构/隧道各专业完整算量函数
- GB 50500-2013清单编码表（约80条编码）

#### 3. CAD 转 BIM
- 基于IfcOpenShell的IFC4标准模型生成
- LOD 100~500分级（概念设计→竣工运维）
- 碰撞检测（几何相交+净距检查）
- 4D BIM（施工进度关联）+ 5D BIM（造价关联）
- BIM模型质量检查与验证

### 扩展能力

#### 4. 工程造价计价
- 综合单价计算（人工费+材料费+机械费+管理费+利润+风险费）
- 人工工日单价表（14种工种，2024~2026市场参考价）
- 常用材料单价表（18种材料）+ 机械台班单价表（10种机械）
- 措施项目费计算（安全文明施工/夜间施工/二次搬运/冬雨季/脚手架/模板）
- 规费与税金计算（一般计税9% / 简易计税3%）
- 工程报价书生成（封面+清单+费用汇总，Excel格式）
- 材料价差调整（超±5%自动调差）

#### 5. 施工安全计算
- 脚手架：立杆稳定性验算(N/φA≤f)、连墙件抗风验算
- 模板支撑体系：立杆稳定性、荷载计算
- 深基坑支护：Rankine主动/被动土压力、嵌固深度、支护形式推荐
- 塔吊基础：地基承载力、偏心距、抗倾覆验算
- 高处作业：临边防护栏杆计算
- 临时用电：电缆截面选型、电压降验算、变压器容量

#### 6. 碳排放与绿色建筑
- 建材碳排放因子表（21种材料，依据GB/T 51366-2019）
- 运输碳排放因子（公路/铁路/水路4种方式）
- 施工能源碳排放因子（电力分区域/柴油/汽油/天然气）
- 全寿命期碳排放计算（建材生产+运输+施工+运行+拆除）
- 装配式建筑装配率计算与评级（AAA/AA/A/B级）
- 绿色建筑星级评价（GB/T 50378-2019，一星/二星/三星）
- 建筑运行能耗计算（采暖/空调/照明/设备）

#### 7. 施工组织与进度
- 双代号网络计划（CPM关键路径法：ES/EF/LS/LF/TF/FF）
- 横道图（甘特图）生成（matplotlib，关键路径红色标注）
- 资源动态曲线（日需求量/峰值/不均衡系数）
- 资源均衡优化（启发式搜索，最小方差法）
- 标准施工工序模板（房建20道/公路15道/隧道14道工序）
- 挣值法进度跟踪（PV/EV/AC/SV/CV/SPI/CPI）

#### 8. Excel计算表生成器
- 统一样式系统（标题/表头/数据/小计/合计/输入项/公式项/备注）
- 混凝土工程量计算表（公式联动、自动合计）
- 钢筋工程量计算表（VLOOKUP理论重量查表、自动算重）
- 综合工程量清单汇总表（多专业分区、自动小计）
- 工程造价汇总表（税率联动、费用公式自动计算）
- 条件格式（负值红色/正值绿色）+ 数据校验下拉列表
- 一键生成完整工程工作簿（封面+目录+多Sheet）

## 技术架构

```
                    ┌─────────────┐
                    │  assemble.py │  模块装配引擎
                    └──────┬──────┘
                           │ 装配
    ┌──────────────────────┼──────────────────────┐
    │                      │                      │
    ▼                      ▼                      ▼
┌─────────┐         ┌──────────┐          ┌───────────┐
│ modules/ │  ──→    │ SKILL.md │   ──→    │  技能调用   │
│ 14个模块  │         │ 186KB    │          │           │
└─────────┘         └──────────┘          └───────────┘
    │
    ├── 01-drawing.md     工程识图（CAD解析/图块/比例/对比）
    ├── 02-quantity.md    工程量计算（公式/系数表/清单编码）
    ├── 03-bim.md         CAD转BIM（IFC4/LOD/碰撞检测）
    ├── 04-standards.md   规范标准（120+条国家规范）
    ├── 05-workflows.md   完整工作流（土建/公路/隧道）
    ├── 06-utilities.md   实用工具（坐标/单位/批量处理）
    ├── 07-deps.md        依赖库清单
    ├── 08-triggers.md    触发条件与处理原则
    ├── 09-pricing.md     造价计价（单价/措施费/税金/报价书）
    ├── 10-safety.md      安全计算（脚手架/基坑/塔吊/用电）
    ├── 11-carbon.md      碳排放（因子表/装配率/绿建/能耗）
    ├── 12-schedule.md    进度计划（CPM/横道图/资源/EVM）
    └── 13-excel.md       Excel生成器（4模板/公式联动）
```

## 项目统计

| 指标 | 数值 |
|------|------|
| 模块文件数 | 14 个 |
| SKILL.md 大小 | 186 KB (152,876 字符) |
| 国家规范标准 | 120+ 条 |
| 算量函数 | 60+ 个 |
| 碳排放因子 | 30+ 条 |
| 单价参考数据 | 40+ 条 |
| 清单编码 | ~80 条 |
| Python代码行 | 3,000+ 行 |

## 快速开始

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/lizhixin066/engineering-bim.git
cd engineering-bim

# 安装依赖
pip install -r requirements.txt

# 装配技能（生成 SKILL.md）
python assemble.py

# 检查模块完整性
python assemble.py --check

# 监听模式（修改自动装配）
python assemble.py --watch
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

# 或使用 docker-compose
docker-compose up -d
```

## 使用示例

### 示例1：解析CAD图纸并提取构件

```python
from drawing_parser import parse_cad_drawing

# 解析DWG/DXF文件
info = parse_cad_drawing("floor_plan.dxf")

# 查看图层和图元
print(f"图层: {info['layers']}")
print(f"线条: {len(info['entities']['lines'])}")
print(f"文字: {len(info['entities']['texts'])}")
```

### 示例2：混凝土工程量计算

```python
from quantity_calc import calculate_concrete_detail

# 计算柱混凝土量（含模板和扣减）
result = calculate_concrete_detail(columns, 'column')
print(f"混凝土量: {result['volume']:.2f} m³")
print(f"模板面积: {result['formwork']:.2f} m²")
```

### 示例3：脚手架安全验算

```python
from safety_calc import check_scaffold_stability

# 验算50m高落地式脚手架
result = check_scaffold_stability(height=50, step=1.8, span=1.5)
print(f"应力比: {result['应力比σ/f']}")
print(f"安全状态: {result['是否安全']}")
```

### 示例4：生成Excel工程量计算表

```python
from excel_generator import generate_full_project_workbook

# 一键生成完整工程Excel工作簿
generate_full_project_workbook(
    project_name="XX综合楼工程",
    output_path="工程量计算表.xlsx"
)
```

### 示例5：施工进度计划

```python
from schedule_calc import build_cpm_network, get_standard_sequence

# 获取房建标准工序
tasks = get_standard_sequence('building')

# 计算关键路径
cpm = build_cpm_network(tasks)
print(f"总工期: {cpm['project_duration']} 天")
print(f"关键路径: {' → '.join(cpm['critical_path'])}")
```

## 项目结构

```
engineering-bim/
├── SKILL.md              # 装配后的技能文件 (186KB)
├── assemble.py           # 模块装配脚本（支持 --check/--watch）
├── requirements.txt      # Python 依赖清单
├── Dockerfile            # Docker 容器配置
├── docker-compose.yml    # Docker Compose 配置
├── LICENSE               # MIT 许可证
├── README.md             # 项目说明文档
├── .gitignore            # Git 忽略规则
├── push_to_github.py     # GitHub 推送工具（纯Python标准库）
├── setup_github.bat      # GitHub 初始化脚本(Windows)
├── setup_github.sh       # GitHub 初始化脚本(Linux/Mac)
└── modules/              # 可独立编辑的模块 (14个)
    ├── _header.md        #   前置元数据 + 技能概述
    ├── 01-drawing.md     #   工程识图 (12.9KB)
    ├── 02-quantity.md    #   工程量计算 (48.5KB) ★核心
    ├── 03-bim.md         #   CAD转BIM (13.7KB)
    ├── 04-standards.md   #   全部国家规范 (14.7KB, 120+条)
    ├── 05-workflows.md   #   完整工作流 (4.1KB)
    ├── 06-utilities.md   #   实用工具 (4.3KB)
    ├── 07-deps.md        #   依赖库 (0.9KB)
    ├── 08-triggers.md    #   使用说明 (1.1KB)
    ├── 09-pricing.md     #   工程造价计价 (12.7KB)
    ├── 10-safety.md      #   施工安全计算 (15.9KB)
    ├── 11-carbon.md      #   碳排放与绿色建筑 (15.3KB)
    ├── 12-schedule.md    #   施工组织与进度 (15.8KB)
    └── 13-excel.md       #   Excel计算表生成器 (21.1KB)
```

## 模块化框架

本项目采用模块化设计，核心设计理念：

1. **独立编辑** — 每个模块文件独立，可单独修改不影响其他模块
2. **顺序装配** — `assemble.py` 的 `MODULES` 列表定义装配顺序
3. **自动生成** — 运行 `python assemble.py` 自动拼接生成 `SKILL.md`
4. **热重载** — `--watch` 模式监听文件变化，自动重新装配

```bash
python assemble.py          # 装配所有模块
python assemble.py --check  # 检查模块完整性
python assemble.py --watch  # 监听文件变化自动装配
```

添加新模块：
1. 在 `modules/` 下创建 `.md` 文件（如 `14-qa.md`）
2. 在 `assemble.py` 的 `MODULES` 列表中按顺序加入文件名
3. 运行 `python assemble.py` 重新装配

## 规范参考

本项目引用 **120+ 项国家规范标准**，按专业分类：

| 分类 | 规范数 | 主要规范 |
|------|:---:|---------|
| 通用基础 | 26 | GB 50500, GB 50854, GB/T 50353, GB 175, GB 1499 等 |
| 土建工程 | 26 | GB 50010, GB 50011, GB 50204, 22G101系列, 18G901系列 |
| 市政工程 | 16 | GB 50013, GB 50014, GB 50268, CJJ 1/2/37 等 |
| 公路工程 | 22 | JTG 3820, JTG B01, JTG D系列, JTG E系列, JTG F系列 |
| 幕墙工程 | 12 | JGJ 102, JGJ 133, GB/T 21086, GB/T 15227 等 |
| 钢结构工程 | 16 | GB 50017, GB 50205, GB 50661, JGJ 82/99/7 等 |
| 隧道工程 | 12 | JTG D70, JTG 3660, TB 10003, GB 50086 等 |

**规范优先级**：强制性条文 > 国家标准(GB) > 推荐性国标(GB/T) > 行业标准(JGJ/CJJ/JTG/TB) > 协会标准(CECS) > 标准图集(xxG)

## 依赖库

| 库 | 版本 | 用途 |
|----|------|------|
| ezdxf | ≥1.1.0 | DXF 文件读写 |
| ifcopenshell | ≥0.7.0 | IFC 文件创建与编辑 |
| numpy | ≥1.24 | 数值计算 |
| shapely | ≥2.0 | 几何计算 |
| pandas | ≥2.0 | 数据处理 |
| open3d | ≥0.17 | 点云处理与可视化 |
| laspy | ≥2.5 | LAS 点云格式 |
| openpyxl | ≥3.1 | Excel 工程量清单 |
| matplotlib | ≥3.7 | 图表可视化（横道图等） |
| xlsxwriter | ≥3.1 | 高级 Excel 导出 |
| geopandas | ≥0.13 | 地理数据处理 |
| fiona | ≥1.9 | 矢量数据读写 |
| opencv-python | ≥4.8 | 图像处理与 OCR |

## 更新日志

### v2.0 (2026-07-12) — 重大升级
- **新增5个功能模块**：造价计价、施工安全、碳排放与绿色建筑、施工组织与进度、Excel计算表生成器
- **规范标准扩展**：从32条扩展到120+条，覆盖六大专业全部国家规范
- **工程量精细化**：加入完整公式推导、系数表、扣减规则
- **项目结构**：模块从9个增长到14个，SKILL.md从60KB增长到186KB

### v1.0 (2026-07) — 初始版本
- 模块化框架搭建（modules/ + assemble.py）
- 三大核心能力：工程识图、工程量计算、CAD转BIM
- 六大专业支持：土建/市政/公路/幕墙/钢结构/隧道
- Docker容器化、MIT开源协议、GitHub仓库

## 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**GitHub**: [https://github.com/lizhixin066/engineering-bim](https://github.com/lizhixin066/engineering-bim)
