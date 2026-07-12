# Engineering BIM - 大型工程综合技能

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![Modules](https://img.shields.io/badge/Modules-16-green.svg)](#项目结构)
[![Functions](https://img.shields.io/badge/Functions-89-orange.svg)](#函数注册表)
[![Standards](https://img.shields.io/badge/规范-120%2B-blue.svg)](#规范参考)
[![SKILL.md](https://img.shields.io/badge/SKILL.md-292KB-green.svg)](SKILL.md)
[![Version](https://img.shields.io/badge/Version-3.1.0-red.svg)](#更新日志)

> 面向大型工程的企业级技能框架，覆盖工程全生命周期的识图、算量、BIM、计价、安全、碳排放、进度、Excel、**图纸智能分析**九大核心能力。
> 支持六大工程专业：土建 / 市政 / 公路 / 幕墙 / 钢结构 / 隧道。

---

## 目录

- [功能概览](#功能概览)
- [支持的专业](#支持的专业)
- [功能特性](#功能特性)
- [技术架构](#技术架构)
- [项目统计](#项目统计)
- [快速开始](#快速开始)
- [部署方式](#部署方式) ★
- [使用示例](#使用示例)
- [项目结构](#项目结构)
- [模块化框架](#模块化框架)
- [函数注册表](#函数注册表)
- [AI调用指南](#ai调用指南)
- [规范参考](#规范参考)
- [依赖库](#依赖库)
- [更新日志](#更新日志)
- [许可证](#许可证)

---

## 功能概览

```
┌──────────────────────────────────────────────────────────────────────┐
│                    Engineering BIM 技能框架 v3.1                       │
├──────────────┬──────────────┬──────────────┬─────────────────────────┤
│  工程识图     │  工程量计算   │  CAD转BIM    │  图纸智能分析 ★New       │
│  12种图元     │  公式推导     │  IFC4标准    │  端到端自动算量          │
│  图纸对比     │  GB清单编码   │  碰撞检测    │  构件识别→算量→校核      │
├──────────────┼──────────────┼──────────────┼─────────────────────────┤
│  工程造价计价 │  施工安全     │  碳排放计算   │  施工组织与进度           │
│  综合单价     │  脚手架/基坑  │  碳排放因子   │  CPM/横道图              │
│  报价书       │  塔吊/用电    │  绿建评价     │  挣值法EVM               │
├──────────────┴──────────────┴──────────────┴─────────────────────────┤
│                Excel计算表生成器（公式联动/4模板）                      │
└──────────────────────────────────────────────────────────────────────┘
       土建 │ 市政 │ 公路 │ 幕墙 │ 钢结构 │ 隧道
```

## 支持的专业

| 专业 | 识图 | 算量 | BIM | 计价 | 安全 | 碳排放 | 进度 | Excel | 图纸分析 |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 土建工程 | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 市政工程 | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| 公路工程 | Y | Y | Y | Y | Y | - | Y | Y | Y |
| 幕墙工程 | Y | Y | Y | Y | - | Y | Y | Y | Y |
| 钢结构工程 | Y | Y | - | Y | Y | Y | Y | Y | Y |
| 隧道工程 | Y | Y | Y | Y | Y | - | Y | Y | Y |

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

#### 4. 图纸智能分析与自动算量 ★ v3.1 新增
- **端到端管线**：CAD解析 → 图层分类 → 构件识别 → 尺寸提取 → 钢筋提取 → 自动算量 → 结果校核 → 报告导出
- 构件识别多策略：
  - 闭合矩形 → 柱
  - 平行线对 → 梁/墙
  - 闭合区域 → 板
  - 文字标注 → 截面尺寸
  - 图块参照 → 门窗
- 正则解析工程标注：
  - 柱编号：`KZ-1 600x600`
  - 梁编号：`KL1(1) 300x600`
  - 钢筋标注：`Φ10@200` / `C16@150` / `2C20` / `4C25+2C20`
  - 标高：`±0.000` / `H=3.600`
  - 板厚：`h=120`
  - 型钢：`H400x200x8x12`
- 自动算量：调用 `calculate_concrete_detail()` + 钢筋算量
- 结果校核：4项指标（混凝土用量指标/钢筋含量/模板系数/构件数量）
- 多层楼层组装与汇总
- 6专业路由：土建/市政/公路/幕墙/钢结构/隧道

### 扩展能力

#### 5. 工程造价计价
- 综合单价计算（人工费+材料费+机械费+管理费+利润+风险费）
- 人工工日单价表（14种工种，2024~2026市场参考价）
- 常用材料单价表（18种材料）+ 机械台班单价表（10种机械）
- 措施项目费计算（安全文明施工/夜间施工/二次搬运/冬雨季/脚手架/模板）
- 规费与税金计算（一般计税9% / 简易计税3%）
- 工程报价书生成（封面+清单+费用汇总，Excel格式）
- 材料价差调整（超±5%自动调差）

#### 6. 施工安全计算
- 脚手架：立杆稳定性验算(N/φA≤f)、连墙件抗风验算
- 模板支撑体系：立杆稳定性、荷载计算
- 深基坑支护：Rankine主动/被动土压力、嵌固深度、支护形式推荐
- 塔吊基础：地基承载力、偏心距、抗倾覆验算
- 高处作业：临边防护栏杆计算
- 临时用电：电缆截面选型、电压降验算、变压器容量

#### 7. 碳排放与绿色建筑
- 建材碳排放因子表（21种材料，依据GB/T 51366-2019）
- 运输碳排放因子（公路/铁路/水路4种方式）
- 施工能源碳排放因子（电力分区域/柴油/汽油/天然气）
- 全寿命期碳排放计算（建材生产+运输+施工+运行+拆除）
- 装配式建筑装配率计算与评级（AAA/AA/A/B级）
- 绿色建筑星级评价（GB/T 50378-2019，一星/二星/三星）
- 建筑运行能耗计算（采暖/空调/照明/设备）

#### 8. 施工组织与进度
- 双代号网络计划（CPM关键路径法：ES/EF/LS/LF/TF/FF）
- 横道图（甘特图）生成（matplotlib，关键路径红色标注）
- 资源动态曲线（日需求量/峰值/不均衡系数）
- 资源均衡优化（启发式搜索，最小方差法）
- 标准施工工序模板（房建20道/公路15道/隧道14道工序）
- 挣值法进度跟踪（PV/EV/AC/SV/CV/SPI/CPI）

#### 9. Excel计算表生成器
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
│ 16个模块  │         │ 292KB    │          │  89个函数  │
└─────────┘         └──────────┘          └───────────┘
    │
    ├── _header.md           元数据 + 技能概述
    ├── 01-drawing.md        工程识图（CAD解析/图块/比例/对比）
    ├── 02-quantity.md       工程量计算（公式/系数表/清单编码）
    ├── 03-bim.md            CAD转BIM（IFC4/LOD/碰撞检测）
    ├── 04-standards.md      规范标准（120+条国家规范）
    ├── 05-workflows.md      完整工作流（土建/公路/隧道）
    ├── 06-utilities.md      实用工具（坐标/单位/批量处理）
    ├── 07-deps.md           依赖库清单
    ├── 08-triggers.md       AI调用指南（10意图×关键字矩阵）
    ├── 09-pricing.md        造价计价（单价/措施费/税金/报价书）
    ├── 10-safety.md         安全计算（脚手架/基坑/塔吊/用电）
    ├── 11-carbon.md         碳排放（因子表/装配率/绿建/能耗）
    ├── 12-schedule.md       进度计划（CPM/横道图/资源/EVM）
    ├── 13-excel.md          Excel生成器（4模板/公式联动）
    ├── 14-api-registry.md   函数注册表（89函数标准化签名）
    └── 15-drawing-to-qty.md 图纸智能分析（端到端自动算量）★New
```

## 项目统计

| 指标 | 数值 |
|------|------|
| 模块文件数 | 16 个 |
| SKILL.md 大小 | 292 KB (240,814 字符) |
| 注册函数数 | 89 个 (FUNC-001~089) |
| AI意图分类 | 10 个 |
| 关键字映射 | 100+ 条 |
| 国家规范标准 | 120+ 条 |
| 碳排放因子 | 30+ 条 |
| 单价参考数据 | 40+ 条 |
| 清单编码 | ~80 条 |
| Python代码行 | 5,000+ 行 |

## 快速开始

### 30秒体验

```bash
git clone https://github.com/lizhixin066/engineering-bim.git
cd engineering-bim
pip install -r requirements.txt
python assemble.py
```

生成 `SKILL.md` 后即可作为技能文件被 AI 调用，或作为 Python 库直接使用。

### 验证安装

```bash
# 检查模块完整性
python assemble.py --check

# 装配并查看统计
python assemble.py --stats

# 监听模式（修改自动装配）
python assemble.py --watch
```

---

## 部署方式

本项目支持 **10 种部署方式**，覆盖本地开发、容器化、云端、集群、嵌入式等场景。

### 方式 1：本地源码部署（推荐开发使用）

```bash
# 克隆仓库
git clone https://github.com/lizhixin066/engineering-bim.git
cd engineering-bim

# 创建虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 装配技能
python assemble.py

# 运行示例
python -c "
from pathlib import Path
import sys; sys.path.insert(0, '.')
print('Engineering BIM v3.1.0 部署成功')
print('模块数: 16, 函数数: 89')
"
```

### 方式 2：Docker 容器部署

```bash
# 构建镜像
docker build -t engineering-bim:3.1 .

# 运行容器（挂载数据目录）
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  engineering-bim:3.1 python assemble.py --check

# 解析CAD图纸
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  engineering-bim:3.1 \
  python -c "from drawing_parser import parse_cad_drawing; print(parse_cad_drawing('/app/data/sample.dxf'))"
```

### 方式 3：Docker Compose 编排部署

```bash
# 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

`docker-compose.yml` 已配置：
- 数据卷挂载（`./data`、`./output`）
- 端口映射（8080 → 8080，可选 API 服务）
- 环境变量配置
- 重启策略（unless-stopped）

### 方式 4：Conda 环境部署（科学计算推荐）

```bash
# 创建 conda 环境
conda create -n eng-bim python=3.11 -y
conda activate eng-bim

# 安装 conda-forge 优先的依赖
conda install -c conda-forge numpy pandas shapely matplotlib openpyxl -y
conda install -c conda-forge ezdxf ifcopenshell laspy -y

# 安装项目
pip install -r requirements.txt

# 装配
python assemble.py
```

> **优势**：conda-forge 渠道的 ifcopenshell、ezdxf 在 Windows 上更稳定，无需编译。

### 方式 5：pip 可编辑安装（库模式）

```bash
# 安装为可编辑包（未来版本支持）
pip install -e .

# 之后可在任意位置导入
python -c "from engineering_bim import parse_cad_drawing"
```

### 方式 6：Kubernetes 集群部署

```bash
# 创建命名空间
kubectl create namespace engineering-bim

# 应用部署
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: engineering-bim
  namespace: engineering-bim
spec:
  replicas: 2
  selector:
    matchLabels:
      app: engineering-bim
  template:
    metadata:
      labels:
        app: engineering-bim
    spec:
      containers:
      - name: engineering-bim
        image: engineering-bim:3.1
        resources:
          requests: {memory: "512Mi", cpu: "250m"}
          limits: {memory: "2Gi", cpu: "1000m"}
        volumeMounts:
        - name: data
          mountPath: /app/data
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: eng-bim-pvc
EOF

# 创建持久卷
kubectl apply -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: eng-bim-pvc
  namespace: engineering-bim
spec:
  accessModes: [ReadWriteOnce]
  resources:
    requests:
      storage: 10Gi
EOF
```

### 方式 7：FastAPI 远程 API 服务

```bash
# 安装 FastAPI
pip install fastapi uvicorn

# 启动 API 服务（提供远程算量接口）
uvicorn api_server:app --host 0.0.0.0 --port 8080 --reload
```

`api_server.py` 示例骨架：

```python
from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import tempfile

app = FastAPI(title="Engineering BIM API", version="3.1.0")

@app.post("/api/parse-drawing")
async def parse_drawing(file: UploadFile = File(...)):
    """上传CAD图纸，返回解析结果"""
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
        f.write(await file.read())
        from drawing_parser import parse_cad_drawing
        return parse_cad_drawing(f.name)

@app.post("/api/auto-quantity")
async def auto_quantity(file: UploadFile = File(...)):
    """上传CAD图纸，返回自动算量结果"""
    with tempfile.NamedTemporaryFile(suffix=".dxf", delete=False) as f:
        f.write(await file.read())
        from drawing_to_quantity import auto_quantity_from_drawing
        return auto_quantity_from_drawing(f.name)

@app.get("/health")
def health():
    return {"status": "ok", "version": "3.1.0"}
```

调用示例：

```bash
# 解析图纸
curl -X POST http://localhost:8080/api/parse-drawing \
  -F "file=@floor_plan.dxf"

# 自动算量
curl -X POST http://localhost:8080/api/auto-quantity \
  -F "file=@floor_plan.dxf"
```

### 方式 8：Systemd 服务部署（Linux 生产环境）

```bash
# 创建服务文件
sudo tee /etc/systemd/system/engineering-bim.service > /dev/null <<EOF
[Unit]
Description=Engineering BIM API Service
After=network.target

[Service]
Type=simple
User=engbim
WorkingDirectory=/opt/engineering-bim
Environment="PATH=/opt/engineering-bim/venv/bin"
ExecStart=/opt/engineering-bim/venv/bin/uvicorn api_server:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 启用并启动
sudo systemctl daemon-reload
sudo systemctl enable engineering-bim
sudo systemctl start engineering-bim

# 查看状态
sudo systemctl status engineering-bim
journalctl -u engineering-bim -f
```

### 方式 9：Windows 服务部署

```powershell
# 安装 nssm（Non-Sucking Service Manager）
choco install nssm -y

# 安装为 Windows 服务
nssm install EngineeringBIM "C:\engineering-bim\venv\Scripts\uvicorn.exe" "api_server:app --host 0.0.0.0 --port 8080"
nssm set EngineeringBIM AppDirectory "C:\engineering-bim"
nssm set EngineeringBIM Start SERVICE_AUTO_START

# 启动服务
nssm start EngineeringBIM

# 查看状态
nssm status EngineeringBIM
```

### 方式 10：Serverless 云函数部署

#### 阿里云函数计算（FC）

```python
# index.py - 阿里云FC入口
import json
import tempfile
from drawing_to_quantity import auto_quantity_from_drawing

def handler(event, context):
    """FC事件处理函数"""
    event_obj = json.loads(event)
    oss_bucket = event_obj['bucket']
    oss_key = event_obj['key']

    # 下载OSS文件（需配置OSS触发器）
    import oss2
    auth = oss2.Auth(context.credentials.access_key_id, context.credentials.access_key_secret)
    bucket = oss2.Bucket(auth, 'oss-cn-hangzhou.aliyuncs.com', oss_bucket)

    with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as f:
        bucket.get_object_to_file(oss_key, f.name)
        result = auto_quantity_from_drawing(f.name)

    return {
        'statusCode': 200,
        'body': json.dumps(result, ensure_ascii=False)
    }
```

#### AWS Lambda（容器镜像）

```dockerfile
# Dockerfile.lambda
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . ${LAMBDA_TASK_ROOT}

# Lambda handler
CMD ["app.lambda_handler"]
```

```python
# app.py - AWS Lambda入口
import json
import tempfile
import boto3
from drawing_to_quantity import auto_quantity_from_drawing

s3 = boto3.client('s3')

def lambda_handler(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    with tempfile.NamedTemporaryFile(suffix='.dxf', delete=False) as f:
        s3.download_file(bucket, key, f.name)
        result = auto_quantity_from_drawing(f.name)

    return {
        'statusCode': 200,
        'body': json.dumps(result, ensure_ascii=False)
    }
```

### 部署方式对比

| 部署方式 | 适用场景 | 难度 | 扩展性 | 成本 |
|---------|---------|:---:|:---:|:---:|
| 本地源码 | 开发调试 | ★☆☆ | - | 免费 |
| Docker | 跨平台部署 | ★★☆ | ★★ | 低 |
| Docker Compose | 单机多服务 | ★★☆ | ★★ | 低 |
| Conda | 科学计算 | ★★☆ | - | 免费 |
| pip 库模式 | 集成到其他项目 | ★☆☆ | - | 免费 |
| Kubernetes | 大规模集群 | ★★★★ | ★★★★★ | 中高 |
| FastAPI | 远程API服务 | ★★☆ | ★★★ | 低 |
| Systemd | Linux生产服务 | ★★★ | ★★ | 低 |
| Windows 服务 | Windows生产服务 | ★★★ | ★★ | 低 |
| Serverless | 事件驱动/弹性伸缩 | ★★★ | ★★★★ | 按需 |

---

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
print(f"混凝土量: {result['concrete_volume_m3']:.2f} m³")
print(f"模板面积: {result['formwork_area_m2']:.2f} m²")
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

### 示例6：图纸智能分析自动算量 ★ New

```python
from drawing_to_quantity import (
    auto_quantity_from_drawing,
    generate_drawing_quantity_report,
    audit_quantity_result
)

# 一键端到端算量：CAD → 构件识别 → 算量
result = auto_quantity_from_drawing("floor_plan.dxf")
print(f"柱数量: {result['summary']['column_count']}")
print(f"混凝土总量: {result['summary']['concrete_volume_m3']:.2f} m³")
print(f"钢筋总量: {result['summary']['rebar_weight_kg']:.2f} kg")
print(f"模板总面积: {result['summary']['formwork_area_m2']:.2f} m²")

# 结果校核（4项指标合理性检查）
audit = audit_quantity_result(result)
print(f"校核通过: {audit['passed']}")
for item in audit['items']:
    print(f"  {item['name']}: {item['value']} ({item['status']})")

# 生成Excel报告（3 Sheet: 汇总/混凝土明细/校核）
generate_drawing_quantity_report(result, "图纸算量报告.xlsx")
```

### 示例7：多专业路由算量 ★ New

```python
from drawing_to_quantity import auto_quantity_by_discipline

# 按专业自动选择算量策略
# 支持: building/municipal/highway/curtain_wall/steel/tunnel
result = auto_quantity_by_discipline(
    drawing_path="road_plan.dxf",
    discipline="highway"
)
print(f"道路面积: {result['road_area_m2']:.2f} m²")
print(f"路缘石长度: {result['curb_length_m']:.2f} m")
```

## 项目结构

```
engineering-bim/
├── SKILL.md              # 装配后的技能文件 (292KB, 89函数)
├── assemble.py           # 模块装配脚本（支持 --check/--watch/--stats）
├── requirements.txt      # Python 依赖清单
├── Dockerfile            # Docker 容器配置
├── docker-compose.yml    # Docker Compose 配置
├── LICENSE               # MIT 许可证
├── README.md             # 项目说明文档
├── .gitignore            # Git 忽略规则
├── push_to_github.py     # GitHub 推送工具（纯Python标准库）
├── setup_github.bat      # GitHub 初始化脚本(Windows)
├── setup_github.sh       # GitHub 初始化脚本(Linux/Mac)
└── modules/              # 可独立编辑的模块 (16个)
    ├── _header.md        #   前置元数据 + 技能概述
    ├── 01-drawing.md     #   工程识图 (12.9KB)
    ├── 02-quantity.md    #   工程量计算 (48.5KB) ★核心
    ├── 03-bim.md         #   CAD转BIM (13.7KB)
    ├── 04-standards.md   #   全部国家规范 (14.7KB, 120+条)
    ├── 05-workflows.md   #   完整工作流 (4.1KB)
    ├── 06-utilities.md   #   实用工具 (4.3KB)
    ├── 07-deps.md        #   依赖库 (0.9KB)
    ├── 08-triggers.md    #   AI调用指南 (13.2KB, 10意图)
    ├── 09-pricing.md     #   工程造价计价 (12.7KB)
    ├── 10-safety.md      #   施工安全计算 (15.9KB)
    ├── 11-carbon.md      #   碳排放与绿色建筑 (15.3KB)
    ├── 12-schedule.md    #   施工组织与进度 (15.8KB)
    ├── 13-excel.md       #   Excel计算表生成器 (21.1KB)
    ├── 14-api-registry.md #  函数注册表 (36.0KB, 89函数)
    └── 15-drawing-to-quantity.md # 图纸智能分析 (52.2KB) ★New
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
1. 在 `modules/` 下创建 `.md` 文件（如 `16-qa.md`）
2. 在 `assemble.py` 的 `MODULES` 列表中按顺序加入文件名
3. 运行 `python assemble.py` 重新装配

## 函数注册表

本项目提供 **89 个标准化函数**（FUNC-001 ~ FUNC-089），每个函数注册条目包含：

- **函数签名**：参数类型、返回值类型
- **所属模块**：定位到具体 `.md` 文件
- **规范依据**：引用的国家规范/图集
- **调用示例**：可直接运行的代码片段

### 函数分布

| 模块 | 函数数 | 函数编号范围 |
|------|:---:|------------|
| 01-工程识图 | 6 | FUNC-001~006 |
| 02-工程量计算 | 20 | FUNC-007~026 |
| 03-CAD转BIM | 16 | FUNC-027~042 |
| 04-规范标准 | 5 | FUNC-043~047 |
| 05-完整工作流 | 3 | FUNC-048~050 |
| 06-实用工具 | 5 | FUNC-051~055 |
| 09-造价计价 | 5 | FUNC-056~060 |
| 10-施工安全 | 7 | FUNC-061~067 |
| 11-碳排放 | 4 | FUNC-068~071 |
| 12-进度计划 | 6 | FUNC-072~075* |
| 13-Excel生成器 | 6 | (扩展) |
| **15-图纸智能分析** ★ | **14** | **FUNC-076~089** |
| **合计** | **89** | — |

> 完整注册表详见 [modules/14-api-registry.md](modules/14-api-registry.md)

## AI调用指南

本项目为 AI 助手提供 **10 个意图分类** × **中英双语关键字矩阵**，实现智能路由。

### 意图分类

| 意图 | ID | 触发关键字示例 | 核心函数 |
|------|:--:|--------------|---------|
| 工程识图 | 01 | 识图/读图/parse cad | `parse_cad_drawing()` |
| 工程量计算 | 02 | 算量/工程量/quantity | `calculate_concrete_detail()` |
| CAD转BIM | 03 | BIM/IFC/碰撞检测 | `create_bim_model_from_cad()` |
| 规范查询 | 04 | 规范/标准/GB/JTG | `query_standard()` |
| 造价计价 | 05 | 计价/单价/报价 | `calculate_unit_price()` |
| 施工安全 | 06 | 安全/脚手架/基坑 | `check_scaffold_stability()` |
| 碳排放 | 07 | 碳排放/绿建/装配率 | `calculate_carbon_emission()` |
| 进度计划 | 08 | 进度/工期/横道图 | `build_cpm_network()` |
| Excel生成 | 09 | Excel/计算表/导出 | `generate_full_project_workbook()` |
| **图纸智能分析** ★ | **10** | **图纸分析/自动算量/drawing to quantity** | **`auto_quantity_from_drawing()`** |

### 路由流程

```
用户消息 → 关键字匹配 → 意图识别 → 专业路由 → 函数调用 → 结果返回
  ↓           ↓            ↓          ↓          ↓
 "根据图纸   "图纸分析"    意图-10    土建路由   auto_quantity
  算工程量"   "自动算量"              →         _from_drawing()
```

> 完整关键字矩阵详见 [modules/08-triggers.md](modules/08-triggers.md)

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

### v3.1.0 (2026-07-13) — 图纸智能分析 ★Latest

- **新增第16个模块**：`15-drawing-to-quantity.md`（52KB，14个新函数 FUNC-076~089）
- **端到端图纸算量管线**：CAD → 图层分类 → 构件识别 → 尺寸提取 → 钢筋提取 → 自动算量 → 结果校核 → 报告导出
- **构件识别多策略**：闭合矩形→柱、平行线对→梁/墙、闭合区域→板、文字标注→截面、块参照→门窗
- **正则解析工程标注**：柱(KZ-1 600x600)、梁(KL1(1) 300x600)、钢筋(Φ10@200/C16@150/2C20)、标高(±0.000)、板厚(h=120)、型钢(H400x200x8x12)
- **结果校核**：4项指标（混凝土用量/钢筋含量/模板系数/构件数量）
- **6专业路由**：土建/市政/公路/幕墙/钢结构/隧道
- **新增意图-10**：图纸智能分析与自动算量关键字矩阵（14行）
- **函数注册表扩展**：67→89个函数
- **SKILL.md**：230KB → 292KB
- **README**：新增10种部署方式

### v3.0.0 (2026-07-13) — 企业级 AI 调用规范

- **YAML 元数据**：capabilities(10项) + disciplines(6专业) 标准化声明
- **关键字矩阵**：9+1个意图分类 × 中英双语关键字映射
- **专业路由表**：6大专业智能路由
- **函数注册表**：67个函数标准化签名(FUNC-001~067)
- **新增模块**：`08-triggers.md`、`14-api-registry.md`
- **AI 调用规范化**：意图识别 → 关键字匹配 → 专业路由 → 函数注册 → 调用规范

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

**版本**: v3.1.0 | **模块**: 16 | **函数**: 89 | **规范**: 120+
