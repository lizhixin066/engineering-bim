---
name: "engineering-bim"
version: "3.0.0"
description: "企业级大型工程综合技能：工程识图、工程量计算、CAD转BIM、造价计价、施工安全、碳排放与绿色建筑、施工组织与进度、Excel计算表生成。覆盖土建/市政/公路/幕墙/钢结构/隧道六大专业。当用户需要识图、算量、BIM建模、计价、安全验算、碳排放、进度计划、Excel计算表或涉及上述工程专业时调用。"
capabilities:
  - id: "drawing"
    name: "工程识图"
    module: "01-drawing.md"
    keywords: ["识图","读图","解析CAD","解析图纸","看图","提取尺寸","图纸对比","图层","DWG","DXF","图块"]
  - id: "quantity"
    name: "工程量计算"
    module: "02-quantity.md"
    keywords: ["算量","工程量","混凝土量","钢筋量","土方量","模板","脚手架","砌体","防水","保温","清单编码"]
  - id: "bim"
    name: "CAD转BIM"
    module: "03-bim.md"
    keywords: ["BIM","IFC","三维模型","Revit","CAD转BIM","翻模","碰撞检测","4D","5D","LOD"]
  - id: "standards"
    name: "规范标准"
    module: "04-standards.md"
    keywords: ["规范","标准","GB","JGJ","JTG","CJJ","图集","22G101","验收"]
  - id: "pricing"
    name: "造价计价"
    module: "09-pricing.md"
    keywords: ["计价","造价","报价","单价","综合单价","措施费","规费","税金","报价书","价差"]
  - id: "safety"
    name: "施工安全计算"
    module: "10-safety.md"
    keywords: ["安全","脚手架验算","模板支撑","基坑支护","塔吊基础","临边防护","临时用电"]
  - id: "carbon"
    name: "碳排放与绿色建筑"
    module: "11-carbon.md"
    keywords: ["碳排放","碳足迹","装配率","绿色建筑","绿建","能耗","节能","碳中和"]
  - id: "schedule"
    name: "施工组织与进度"
    module: "12-schedule.md"
    keywords: ["进度","工期","网络计划","关键路径","CPM","横道图","甘特图","挣值","EVM","资源均衡"]
  - id: "excel"
    name: "Excel计算表生成"
    module: "13-excel.md"
    keywords: ["Excel","计算表","表格","导出","报表","工作簿","openpyxl"]
disciplines:
  - id: "civil"
    name: "土建工程"
    codes: ["0101","0102","0103","0104","0105","0106","0107","0108","0109","0110","0111"]
  - id: "municipal"
    name: "市政工程"
    codes: ["0401","0402","0403","0404","0405","0406","0407","0408","0409","0410","0411","0412","0413"]
  - id: "highway"
    name: "公路工程"
    codes: ["JTG"]
  - id: "curtain_wall"
    name: "幕墙工程"
    codes: ["0110"]
  - id: "steel"
    name: "钢结构工程"
    codes: ["0106"]
  - id: "tunnel"
    name: "隧道工程"
    codes: ["0114"]
standards_count: 120
function_count: 67
---

# 企业级大型工程综合技能 (Engineering & BIM)

> **版本**: v3.0.0 企业级 | **更新**: 2026-07-12
> **模块数**: 15 | **函数数**: 67 | **规范数**: 120+
> 编辑任意 `modules/*.md` 后运行 `python assemble.py` 重新生成 SKILL.md

本技能为企业级大型工程综合工具，覆盖工程全生命周期八大核心能力：

| # | 能力 | 模块 | 核心函数数 |
|---|------|------|:---:|
| 1 | 工程识图 | 01-drawing.md | 6 |
| 2 | 工程量计算 | 02-quantity.md | 20 |
| 3 | CAD转BIM | 03-bim.md | 15 |
| 4 | 规范标准 | 04-standards.md | - |
| 5 | 工程造价计价 | 09-pricing.md | 5 |
| 6 | 施工安全计算 | 10-safety.md | 6 |
| 7 | 碳排放与绿色建筑 | 11-carbon.md | 4 |
| 8 | 施工组织与进度 | 12-schedule.md | 5 |
| 9 | Excel计算表生成 | 13-excel.md | 6 |

支持六大专业：**土建 / 市政 / 公路 / 幕墙 / 钢结构 / 隧道**

---

## 一、工程识图 (Engineering Drawing Recognition)

### 1.1 支持的图纸格式
- **CAD 格式**: `.dwg` (R12~2024), `.dxf` (ASCII/Binary)
- **BIM 格式**: `.ifc` (IFC2x3/IFC4/IFC4.3), `.rvt` (Revit 2018+), `.skp` (SketchUp)
- **点云格式**: `.las`, `.laz`, `.ply`, `.pts`, `.xyz`, `.e57`
- **图像格式**: `.pdf` (矢量/栅格), `.tiff`, `.png`, `.jpg`
- **GIS 格式**: `.shp` (Shapefile), `.geojson`, `.kml`

### 1.2 识图流程

#### Step 1: 图纸加载与全图元解析

```python
import ezdxf
from ezdxf.math import Vec3
import math

def parse_cad_drawing(filepath: str) -> dict:
    """
    完整解析CAD图纸，支持所有常见图元类型
    """
    doc = ezdxf.readfile(filepath)
    msp = doc.modelspace()

    # 获取图纸基本信息
    header = doc.header
    drawing_info = {
        'units': header.get('$INSUNITS', 0),
        'min_extents': list(header.get('$EXTMIN', (0,0,0))),
        'max_extents': list(header.get('$EXTMAX', (0,0,0))),
        'layers': [layer.dxf.name for layer in doc.layers],
        'linetypes': [lt.dxf.name for lt in doc.linetypes],
        'text_styles': [ts.dxf.name for ts in doc.styles],
        'entities': {'lines': [], 'polylines': [], 'arcs': [], 'circles': [],
                     'texts': [], 'dimensions': [], 'blocks': [], 'hatches': [],
                     'splines': [], 'ellipses': [], 'points': [], 'inserts': []},
    }

    for entity in msp:
        etype = entity.dxftype()

        if etype == 'LINE':
            drawing_info['entities']['lines'].append({
                'start': (entity.dxf.start.x, entity.dxf.start.y, entity.dxf.start.z),
                'end': (entity.dxf.end.x, entity.dxf.end.y, entity.dxf.end.z),
                'length': (entity.dxf.end - entity.dxf.start).magnitude,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype in ('LWPOLYLINE', 'POLYLINE'):
            pts = []
            if etype == 'LWPOLYLINE':
                pts = [(p[0], p[1], entity.dxf.elevation if hasattr(entity.dxf, 'elevation') else 0)
                       for p in entity]
            else:
                pts = [(v.dxf.location.x, v.dxf.location.y, v.dxf.location.z)
                       for v in entity.vertices]
            closed = entity.closed if hasattr(entity, 'closed') else False
            drawing_info['entities']['polylines'].append({
                'points': pts,
                'closed': closed,
                'area': _polyline_area(pts) if closed else 0,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype == 'ARC':
            drawing_info['entities']['arcs'].append({
                'center': (entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z),
                'radius': entity.dxf.radius,
                'start_angle': entity.dxf.start_angle,
                'end_angle': entity.dxf.end_angle,
                'arc_length': entity.dxf.radius * abs(
                    (entity.dxf.end_angle - entity.dxf.start_angle) % 360 * math.pi / 180
                ),
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype == 'CIRCLE':
            drawing_info['entities']['circles'].append({
                'center': (entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z),
                'radius': entity.dxf.radius,
                'circumference': 2 * math.pi * entity.dxf.radius,
                'area': math.pi * entity.dxf.radius ** 2,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype in ('TEXT', 'MTEXT'):
            text_content = entity.dxf.text if etype == 'TEXT' else entity.text
            drawing_info['entities']['texts'].append({
                'content': text_content,
                'position': (entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z),
                'height': entity.dxf.height,
                'rotation': entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype in ('DIMENSION', 'DIMLINEAR', 'DIMALIGNED', 'DIMANGULAR',
                        'DIMRADIUS', 'DIMDIAMETER', 'DIMORDINATE'):
            dim_info = {
                'type': etype,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            }
            if hasattr(entity, 'get_measurement'):
                dim_info['measurement'] = entity.get_measurement()
            if hasattr(entity.dxf, 'text'):
                dim_info['text_override'] = entity.dxf.text
            drawing_info['entities']['dimensions'].append(dim_info)

        elif etype == 'INSERT':
            drawing_info['entities']['inserts'].append({
                'block_name': entity.dxf.name,
                'position': (entity.dxf.insert.x, entity.dxf.insert.y, entity.dxf.insert.z),
                'scale': (entity.dxf.xscale, entity.dxf.yscale, entity.dxf.zscale),
                'rotation': entity.dxf.rotation,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype == 'HATCH':
            drawing_info['entities']['hatches'].append({
                'pattern_name': entity.dxf.pattern_name if hasattr(entity.dxf, 'pattern_name') else 'SOLID',
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype == 'SPLINE':
            drawing_info['entities']['splines'].append({
                'control_points': [(p.x, p.y, p.z) for p in entity.control_points],
                'degree': entity.dxf.degree,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype == 'ELLIPSE':
            drawing_info['entities']['ellipses'].append({
                'center': (entity.dxf.center.x, entity.dxf.center.y, entity.dxf.center.z),
                'major_axis': (entity.dxf.major_axis.x, entity.dxf.major_axis.y, entity.dxf.major_axis.z),
                'ratio': entity.dxf.ratio,
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

        elif etype == 'POINT':
            drawing_info['entities']['points'].append({
                'position': (entity.dxf.location.x, entity.dxf.location.y, entity.dxf.location.z),
                'layer': entity.dxf.layer,
                'handle': entity.dxf.handle,
            })

    return drawing_info

def _polyline_area(points: list) -> float:
    """鞋带公式计算闭合多段线面积"""
    n = len(points)
    if n < 3:
        return 0.0
    area = 0.0
    for i in range(n):
        x1, y1 = points[i][0], points[i][1]
        x2, y2 = points[(i+1) % n][0], points[(i+1) % n][1]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2.0
```

#### Step 2: 图块（Block）与外部参照（Xref）处理

```python
def extract_block_definitions(doc) -> dict:
    """提取所有图块定义，包括嵌套块"""
    blocks = {}
    for block_record in doc.blocks:
        if block_record.name.startswith('*'):
            continue
        if block_record.is_xref:
            blocks[block_record.name] = {
                'type': 'xref',
                'xref_path': block_record.dxf.path,
                'entities': list(block_record),
            }
        else:
            blocks[block_record.name] = {
                'type': 'block',
                'base_point': block_record.block.base_point,
                'entities': [e for e in block_record],
            }
    return blocks

def explode_block_reference(block_ref, block_definitions, layer: str = None):
    """展开图块参照为原始图元，支持嵌套块递归展开"""
    block_name = block_ref['block_name']
    if block_name not in block_definitions:
        return []

    block_def = block_definitions[block_name]
    scale = block_ref['scale']
    insert_pos = block_ref['position']
    rotation = block_ref['rotation']
    exploded = []

    for entity in block_def.get('entities', []):
        if entity.dxftype() == 'INSERT':
            child_ref = {
                'block_name': entity.dxf.name,
                'position': entity.dxf.insert,
                'scale': (entity.dxf.xscale, entity.dxf.yscale, entity.dxf.zscale),
                'rotation': entity.dxf.rotation,
            }
            exploded.extend(explode_block_reference(child_ref, block_definitions, layer))
        else:
            transformed = _transform_entity(entity, scale, rotation, insert_pos)
            if layer:
                transformed['layer'] = layer
            exploded.append(transformed)

    return exploded

def _transform_entity(entity, scale, rotation, insert_pos):
    """对图元应用缩放、旋转和平移变换"""
    import math
    sx, sy, sz = scale
    cos_r = math.cos(math.radians(rotation))
    sin_r = math.sin(math.radians(rotation))

    def transform_point(x, y, z=0):
        nx, ny = x * sx, y * sy
        rx = nx * cos_r - ny * sin_r
        ry = nx * sin_r + ny * cos_r
        return (rx + insert_pos[0], ry + insert_pos[1], z + insert_pos[2])

    result = {'type': entity.dxftype(), 'layer': entity.dxf.layer}
    return result
```

#### Step 3: 图纸比例自动识别

```python
def detect_drawing_scale(msp, paper_size: str = 'A1') -> float:
    """自动识别图纸比例"""
    paper_sizes = {
        'A0': (1189, 841), 'A1': (841, 594), 'A2': (594, 420),
        'A3': (420, 297), 'A4': (297, 210),
    }
    dim_styles = get_dimension_styles(msp)
    dim_scale = dim_styles.get('DIMSCALE', 1.0)
    blocks = _get_block_entities(msp, 'INSERT')
    for b in blocks:
        name = b['block_name'].upper()
        if 'A1' in name or 'A2' in name or 'TK' in name:
            paper_w, paper_h = paper_sizes.get(paper_size, (841, 594))
            drawing_w = b['scale'][0]
            scale = paper_w / drawing_w if drawing_w > 0 else 1.0
            return round(scale)
    if dim_scale > 1:
        return dim_scale
    return 1.0
```

#### Step 4: 图层分类识别（扩展版）

| 图层关键字 | 构件类型 | 适用专业 |
|-----------|---------|---------|
| `WALL`, `墙`, `墙体`, `WA-`, `W-` | 墙体 | 土建/幕墙 |
| `COLUMN`, `柱`, `Z-`, `KZ-`, `GZ-` | 柱 | 土建/钢结构 |
| `BEAM`, `梁`, `L-`, `KL-`, `LL-`, `WKL-` | 梁 | 土建 |
| `SLAB`, `板`, `B-`, `LB-`, `WB-` | 楼板 | 土建 |
| `ROAD`, `道路`, `DL-`, `LM-`, `LJ-` | 道路 | 公路/市政 |
| `CURB`, `路缘石`, `LYS-`, `PYS-` | 路缘石 | 公路/市政 |
| `PIPE`, `管道`, `G-`, `PS-`, `GS-`, `YS-`, `WS-` | 管道 | 市政 |
| `CURTAIN`, `幕墙`, `MQ-`, `CW-` | 幕墙 | 幕墙 |
| `STEEL`, `钢筋`, `GJ-`, `REBAR` | 钢筋 | 土建/市政 |
| `FOUNDATION`, `基础`, `JC-`, `CT-`, `ZJ-` | 基础 | 土建 |
| `BRIDGE`, `桥梁`, `QL-`, `SX-`, `QD-`, `QT-` | 桥梁 | 公路/市政 |
| `DRAIN`, `排水`, `PS-`, `YS-`, `WS-` | 排水 | 市政/公路 |
| `STEEL_STRUCTURE`, `钢结构`, `GJG-`, `ST-`, `GL-` | 钢结构 | 钢结构/土建 |
| `TUNNEL`, `隧道`, `SD-`, `TUN-` | 隧道 | 公路/市政 |
| `DOOR`, `门`, `M-`, `D-`, `FM-` | 门 | 土建 |
| `WINDOW`, `窗`, `C-`, `TC-`, `FC-` | 窗 | 土建/幕墙 |
| `STAIR`, `楼梯`, `LT-`, `ST-` | 楼梯 | 土建 |
| `ELEVATION`, `标高`, `BG-`, `EL-` | 标高标注 | 通用 |
| `AXIS`, `轴线`, `ZX-`, `AX-` | 轴网 | 通用 |
| `SECTION`, `剖面`, `PM-`, `SEC-` | 剖面 | 通用 |

#### Step 5: 图纸对比功能

```python
def compare_drawings(doc1, doc2) -> dict:
    """对比两个版本的CAD图纸，找出差异"""
    differences = {
        'added_layers': [],
        'removed_layers': [],
        'modified_entities': [],
        'added_entities': [],
        'removed_entities': [],
    }
    msp1 = doc1.modelspace()
    msp2 = doc2.modelspace()
    layers1 = {e.dxf.layer for e in msp1}
    layers2 = {e.dxf.layer for e in msp2}
    differences['added_layers'] = list(layers2 - layers1)
    differences['removed_layers'] = list(layers1 - layers2)
    count1 = _count_by_layer(msp1)
    count2 = _count_by_layer(msp2)
    all_layers = set(count1.keys()) | set(count2.keys())
    for layer in all_layers:
        c1 = count1.get(layer, 0)
        c2 = count2.get(layer, 0)
        if c1 != c2:
            diff = c2 - c1
            differences['modified_entities'].append({
                'layer': layer,
                'change': diff,
                'type': 'added' if diff > 0 else 'removed',
                'count': abs(diff),
            })
    return differences

def _count_by_layer(msp) -> dict:
    counts = {}
    for entity in msp:
        layer = entity.dxf.layer
        counts[layer] = counts.get(layer, 0) + 1
    return counts
```

---

## 二、工程量计算 (Quantity Calculation)

> 依据: GB 50500-2013《建设工程工程量清单计价规范》、各专业施工及验收规范

---

### 2.0 通用计算公式与系数

#### 2.0.1 基本几何公式

```
矩形面积: A = a × b
三角形面积: A = 0.5 × b × h
圆形面积: A = π × r² = 0.25 × π × d²
梯形面积: A = (a + b) × h / 2
扇形面积: A = (θ/360) × π × r²

长方体体积: V = a × b × c
圆柱体体积: V = π × r² × h
棱台体积: V = h/3 × (A₁ + A₂ + √(A₁×A₂))
球缺体积: V = π × h² × (3R - h) / 3
```

#### 2.0.2 材料密度表

| 材料 | 密度 (kg/m³) | 材料 | 密度 (kg/m³) |
|------|------------|------|------------|
| 素混凝土 | 2200-2400 | 钢材 | 7850 |
| 钢筋混凝土 | 2500-2600 | 铝材 | 2700 |
| 水泥砂浆 | 2000 | 玻璃 | 2500 |
| 普通砖砌体 | 1800 | 沥青混凝土 | 2350-2450 |
| 加气混凝土 | 600-800 | 碎石 | 1500-1800 |

#### 2.0.3 土方松散系数

| 土质类别 | 最初松散系数 Ks | 最终松散系数 Ks' |
|---------|:---:|:---:|
| 一类土(松软) | 1.08-1.17 | 1.01-1.03 |
| 二类土(普通) | 1.14-1.28 | 1.02-1.05 |
| 三类土(坚土) | 1.24-1.30 | 1.04-1.07 |
| 四类土(砂砾) | 1.26-1.37 | 1.06-1.09 |
| 软质岩石 | 1.30-1.45 | 1.10-1.20 |
| 硬质岩石 | 1.45-1.50 | 1.20-1.30 |

---

### 2.1 土建工程量计算

#### 2.1.1 混凝土工程量（含模板、扣减规则）

**计算公式体系:**

```
柱: V = 截面面积 × 柱高
   模板 S = 柱周长 × 柱高 - 梁头/板头扣减

梁: V = 截面面积 × 梁长 (= 梁宽 × 梁高 × 净跨)
   模板 S = (梁宽 + 2×梁高) × 梁长 - 板厚扣减

板: V = 板面积 × 板厚
   模板 S = 板底面积 + 板侧面积

墙: V = 墙长 × 墙高 × 墙厚 - 门窗洞口 + 门窗过梁
   模板 S = 2 × 墙长 × 墙高 - 门窗洞口面积

基础: V = 基础底面积 × 基础高度
   模板 S = 基础侧面周长 × 基础高度
```

**梁柱节点扣减规则 (GB 50500):**
- 柱与梁相交: 柱算通，梁算至柱边
- 主梁与次梁相交: 主梁算通，次梁算至主梁边
- 板与梁相交: 板算至梁边，梁算通
- 板与墙相交: 板算至墙边，墙算通

```python
def calculate_concrete_detail(entities, element_type):
    """
    混凝土详细算量（含模板、扣减）
    依据: GB 50500-2013, GB 50204-2015
    """
    total_volume = 0.0
    total_formwork = 0.0

    for entity in entities:
        dims = get_element_dimensions(entity, element_type)

        if element_type == 'beam':
            w, h, L = dims['width'], dims['height'], dims['length']
            # 梁体积 = 截面宽 × 截面高 × 净跨
            volume = w * h * L
            # 梁模板 = 底模 + 两侧模（扣除板厚）
            slab_t = dims.get('slab_thickness', 0)
            formwork = (w + 2 * (h - slab_t)) * L

        elif element_type == 'column':
            w, d, h = dims['width'], dims['depth'], dims['height']
            # 柱体积 = 截面宽 × 截面深 × 柱高
            volume = w * d * h
            # 柱模板 = 四周面积（扣除梁头）
            beam_h = dims.get('beam_height', 0)
            formwork = 2 * (w + d) * (h - beam_h)

        elif element_type == 'slab':
            area = dims['area']
            t = dims['thickness']
            perimeter = dims.get('perimeter', 0)
            # 板体积 = 面积 × 厚度
            volume = area * t
            # 板模板 = 底面积 + 侧面积
            formwork = area + perimeter * t

        elif element_type == 'wall':
            L, H, t = dims['length'], dims['height'], dims['thickness']
            openings = dims.get('openings', [])  # 门窗洞口
            opening_area = sum(o['width'] * o['height'] for o in openings)
            # 墙体积 = 墙长 × 墙高 × 墙厚 - 洞口体积
            volume = L * H * t - opening_area * t
            # 墙模板 = 两面面积 - 洞口面积
            formwork = 2 * L * H - opening_area * 2

        elif element_type == 'foundation':
            L, W, H = dims['length'], dims['width'], dims['height']
            ftype = dims.get('type', 'independent')
            if ftype == 'independent':
                # 独立基础
                volume = L * W * H
                formwork = 2 * (L + W) * H
            elif ftype == 'strip':
                # 条形基础
                volume = L * W * H
                formwork = 2 * L * H + W * H
            elif ftype == 'raft':
                # 筏板基础
                volume = L * W * H
                formwork = 2 * (L + W) * H

        elif element_type == 'stair':
            run_w = dims['run_width']       # 踏步宽
            run_h = dims['run_height']       # 踏步高
            stair_w = dims['stair_width']     # 梯段宽
            steps = dims['steps']
            # 楼梯体积 = 梯段斜面积 × 梯板厚度
            slant = (run_w**2 + run_h**2)**0.5
            volume = slant * stair_w * dims['thickness'] * steps
            # 楼梯模板 = 梯段底面积 + 踏步侧面
            formwork = slant * stair_w * steps + run_h * stair_w * steps

        total_volume += volume
        total_formwork += formwork

    return {'concrete_volume_m3': round(total_volume, 3),
            'formwork_area_m2': round(total_formwork, 3)}
```

#### 2.1.2 构造柱、过梁、圈梁、压顶

```python
def calculate_secondary_elements(data: dict) -> dict:
    """
    二次结构算量: 构造柱、过梁、圈梁、压顶
    依据: GB 50011-2010《建筑抗震设计规范》, 12G614-1 图集
    """
    q = {}

    # ---- 构造柱 ----
    # 马牙槎体积 = 构造柱截面 × 高 × (1 + 马牙槎系数)
    # 马牙槎系数: 一字墙=0.06, 丁字墙=0.13, 十字墙=0.19, L形墙=0.10
    gc = data.get('construction_columns', [])
    q['gzz_volume'] = 0
    q['gzz_formwork'] = 0
    for col in gc:
        b, d, h = col['width'], col['depth'], col['height']
        shape = col.get('shape', '一字')
        horse_tooth = {'一字': 0.06, 'L形': 0.10, '丁字': 0.13, '十字': 0.19}
        factor = horse_tooth.get(shape, 0.06)
        q['gzz_volume'] += b * d * h * (1 + factor)
        q['gzz_formwork'] += 2 * (b + d) * h

    # ---- 过梁 ----
    # 体积 = 过梁宽 × 过梁高 × (洞口宽 + 2×每边搁置长度)
    # 搁置长度: 非抗震≥240mm, 抗震≥360mm
    gl = data.get('lintels', [])
    q['gl_volume'] = 0
    for lintel in gl:
        b, h = lintel['width'], lintel['height']
        opening = lintel['opening_width']
        bearing = lintel.get('bearing', 240)  # 每边搁置长度
        L = opening + 2 * bearing
        q['gl_volume'] += b * h * L

    # ---- 圈梁 ----
    # 体积 = 圈梁截面面积 × 中心线长度
    ql = data.get('ring_beams', [])
    q['ql_volume'] = 0
    for rb in ql:
        b, h = rb['width'], rb['height']
        L = rb['centerline_length']
        q['ql_volume'] += b * h * L

    # ---- 压顶 ----
    yd = data.get('coping', [])
    q['yd_volume'] = sum(c['width'] * c['height'] * c['length'] for c in yd)

    return q
```

#### 2.1.3 砌体工程量

```python
def calculate_masonry(wall_data: dict) -> dict:
    """
    砌体工程量计算
    依据: GB 50500-2013, GB 50203《砌体结构工程施工质量验收规范》

    标准砖: 240×115×53mm
    砌体净用量(块/m³):
      - 半砖墙: 552 块/m³ (墙厚 115mm)
      - 一砖墙: 529 块/m³ (墙厚 240mm)
      - 一砖半墙: 522 块/m³ (墙厚 365mm)
      - 二砖墙: 518 块/m³ (墙厚 490mm)

    砂浆净用量: 1m³砌体 - 砖体积
    """
    wall_type = wall_data.get('type', '240墙')
    brick_counts = {'115墙': 552, '240墙': 529, '365墙': 522, '490墙': 518}
    bricks_per_m3 = brick_counts.get(wall_type, 529)

    total_volume = 0
    for wall in wall_data.get('walls', []):
        L, H, t = wall['length'], wall['height'], wall['thickness']
        openings = wall.get('openings', [])
        opening_vol = sum(o['width'] * o['height'] * t for o in openings)
        total_volume += L * H * t - opening_vol

    return {
        'masonry_volume_m3': round(total_volume, 3),
        'brick_count': round(total_volume * bricks_per_m3),
        'mortar_volume_m3': round(total_volume * (1 - bricks_per_m3 * 0.24 * 0.115 * 0.053), 3),
    }
```

#### 2.1.4 钢筋详细算量（完整版）

**钢筋理论重量公式:**
```
W = 0.00617 × d² (kg/m)

其中 d = 钢筋直径 (mm)
推导: W = π × (d/2)² × 7850 × 10⁻⁶ = 0.006165 × d² ≈ 0.00617 × d²
```

**钢筋锚固长度公式 (GB 50010-2010):**
```
基本锚固长度: lab = α × (fy / ft) × d
  其中 α = 钢筋外形系数 (光圆=0.16, 带肋=0.14)
       fy = 钢筋抗拉强度设计值
       ft = 混凝土抗拉强度设计值
       d = 钢筋直径

抗震锚固长度: laE = ζaE × la
  抗震修正系数 ζaE:
    一、二级抗震: 1.15
    三级抗震: 1.05
    四级抗震: 1.00
```

**搭接长度:**
```
llE = ζl × laE
  搭接修正系数 ζl (按搭接接头面积百分率):
    ≤25%: 1.2
    50%: 1.4
    100%: 1.6
```

**不同混凝土强度等级下的锚固长度参考表 (HRB400, d≤25mm):**

| 抗震等级 | C20 | C25 | C30 | C35 | C40 | C45 | C50 |
|---------|-----|-----|-----|-----|-----|-----|-----|
| 一、二级 | 44d | 38d | 35d | 32d | 29d | 28d | 26d |
| 三级 | 41d | 35d | 32d | 29d | 27d | 25d | 24d |
| 四级 | 39d | 34d | 30d | 28d | 25d | 24d | 23d |

```python
# 完整钢筋理论重量表 (kg/m)
REBAR_WEIGHT = {
    4: 0.099, 5: 0.154, 6: 0.222, 6.5: 0.260, 8: 0.395, 10: 0.617,
    12: 0.888, 14: 1.210, 16: 1.580, 18: 2.000, 20: 2.470,
    22: 2.980, 25: 3.850, 28: 4.830, 32: 6.310, 36: 7.990, 40: 9.870,
    50: 15.42,
}

# 锚固长度表 (C30, HRB400, d≤25mm)
def anchorage_length(grade: int, concrete: str = 'C30', rebar_type: str = 'HRB400') -> int:
    """返回锚固长度倍数 (×d)"""
    table = {
        # 抗震等级: (C20, C25, C30, C35, C40, C45, C50)
        (1, 'HRB400'): (44, 38, 35, 32, 29, 28, 26),
        (2, 'HRB400'): (44, 38, 35, 32, 29, 28, 26),
        (3, 'HRB400'): (41, 35, 32, 29, 27, 25, 24),
        (4, 'HRB400'): (39, 34, 30, 28, 25, 24, 23),
    }
    concrete_idx = {'C20': 0, 'C25': 1, 'C30': 2, 'C35': 3, 'C40': 4, 'C45': 5, 'C50': 6}
    return table.get((grade, rebar_type), (35,))[concrete_idx.get(concrete, 2)]

def calculate_full_rebar(element_data: dict, element_type: str) -> dict:
    """
    完整钢筋算量：覆盖梁、柱、板、墙、基础
    依据: GB 50010-2010, 16G101-1/2/3 图集
    """
    result = {'items': [], 'total_kg': 0.0}

    if element_type == 'beam':
        result = _beam_rebar(element_data)
    elif element_type == 'column':
        result = _column_rebar(element_data)
    elif element_type == 'slab':
        result = _slab_rebar(element_data)
    elif element_type == 'wall':
        result = _wall_rebar(element_data)
    elif element_type == 'foundation':
        result = _foundation_rebar(element_data)

    return result

def _beam_rebar(data: dict) -> dict:
    """梁钢筋算量"""
    r = {'items': [], 'total_kg': 0.0}
    L, w, h = data['length'], data['width'], data['height']
    cover = data.get('cover', 25)
    grade = data.get('seismic_grade', 2)
    lae = anchorage_length(grade)  # 锚固长度倍数

    def add_item(name, d, count, single_len):
        wt = count * single_len / 1000 * REBAR_WEIGHT.get(d, 0.00617*d**2)
        r['items'].append({'name': name, 'd': d, 'count': count,
                           'length_mm': round(single_len), 'weight_kg': round(wt, 2)})
        r['total_kg'] += wt

    # 1. 上部通长筋
    for rb in data.get('top_rebars', []):
        add_item(f'上部通长筋 D{rb["d"]}', rb['d'], rb['count'], L + 2 * lae * rb['d'])

    # 2. 下部通长筋
    for rb in data.get('bottom_rebars', []):
        add_item(f'下部通长筋 D{rb["d"]}', rb['d'], rb['count'], L + 2 * lae * rb['d'])

    # 3. 支座负筋 (端支座 1/3净跨, 中间支座 1/3×两侧较大净跨)
    for rb in data.get('support_rebars', []):
        extend = L / 3  # 伸出长度 = 净跨/3
        add_item(f'支座负筋 D{rb["d"]}', rb['d'], rb['count'], extend + lae * rb['d'])

    # 4. 架立筋
    for rb in data.get('erection_rebars', []):
        add_item(f'架立筋 D{rb["d"]}', rb['d'], rb['count'], L + 2 * 150)

    # 5. 腰筋 (构造/抗扭)
    # 腹板高度 hw ≥ 450mm 时设置: 每侧间距 ≤ 200mm
    for rb in data.get('waist_rebars', []):
        add_item(f'腰筋 D{rb["d"]}', rb['d'], rb['count'], L + 2 * 15 * rb['d'])

    # 6. 箍筋
    st = data.get('stirrups', {})
    if st:
        d = st['d']
        spacing = st.get('spacing', 100)
        # 加密区和非加密区
        encrypt_len = st.get('encrypt_length', max(1.5 * h, 500))  # 加密区长度
        non_encrypt_len = L - 2 * encrypt_len
        encrypt_spacing = st.get('encrypt_spacing', min(spacing, 100))
        non_encrypt_spacing = st.get('non_encrypt_spacing', spacing)

        # 箍筋长度 = 2×(b+h) - 8×保护层 + 2×弯钩(11.9d)
        stirrup_len = 2 * (w + h) - 8 * cover + 2 * 11.9 * d
        encrypt_count = (encrypt_len // encrypt_spacing + 1) * 2  # 两端加密区
        non_encrypt_count = max(0, non_encrypt_len // non_encrypt_spacing - 1)
        total_count = encrypt_count + non_encrypt_count

        add_item(f'箍筋 D{d}@{encrypt_spacing}/{non_encrypt_spacing}',
                 d, total_count, stirrup_len)

    # 7. 拉筋
    tie = data.get('tie_rebars', {})
    if tie:
        d = tie['d']
        count = tie.get('count', 0)
        tie_len = w - 2 * cover + 2 * 11.9 * d  # 拉筋长度
        add_item(f'拉筋 D{d}', d, count, tie_len)

    r['total_kg'] = round(r['total_kg'], 2)
    return r

def _column_rebar(data: dict) -> dict:
    """柱钢筋算量 (16G101-1)"""
    r = {'items': [], 'total_kg': 0.0}
    w, d, h = data['width'], data['depth'], data['height']
    cover = data.get('cover', 20)
    grade = data.get('seismic_grade', 2)
    lae = anchorage_length(grade)

    def add_item(name, dia, count, single_len):
        wt = count * single_len / 1000 * REBAR_WEIGHT.get(dia, 0.00617*dia**2)
        r['items'].append({'name': name, 'd': dia, 'count': count,
                           'length_mm': round(single_len), 'weight_kg': round(wt, 2)})
        r['total_kg'] += wt

    # 1. 纵筋
    for rb in data.get('longitudinal_rebars', []):
        dia = rb['d']
        count = rb['count']
        # 纵筋长度 = 柱高 + 上层锚固 - 下层伸出
        single_len = h + lae * dia - (data.get('extend_below', 0))
        add_item(f'纵筋 D{dia}', dia, count, single_len)

    # 2. 箍筋 (加密区: 柱根≥Hn/3, 节点区, 上下端≥max(Hn/6,hc,500))
    st = data.get('stirrups', {})
    if st:
        dia = st['d']
        # 箍筋长度 = 2×(b+h) - 8×保护层 + 2×弯钩(11.9d)
        st_len = 2 * (w + d) - 8 * cover + 2 * 11.9 * dia
        spacing = st.get('spacing', 100)
        count = h // spacing + 1
        add_item(f'柱箍筋 D{dia}@{spacing}', dia, count, st_len)

    r['total_kg'] = round(r['total_kg'], 2)
    return r

def _slab_rebar(data: dict) -> dict:
    """板钢筋算量 (16G101-1, 04G101-4)"""
    r = {'items': [], 'total_kg': 0.0}
    Lx, Ly = data['length_x'], data['length_y']
    cover = data.get('cover', 15)

    def add_item(name, dia, count, single_len):
        wt = count * single_len / 1000 * REBAR_WEIGHT.get(dia, 0.00617*dia**2)
        r['items'].append({'name': name, 'd': dia, 'count': count,
                           'length_mm': round(single_len), 'weight_kg': round(wt, 2)})
        r['total_kg'] += wt

    # 1. 底筋 (双向)
    for rb in data.get('bottom_rebars', []):
        dia = rb['d']
        spacing = rb['spacing']
        direction = rb.get('direction', 'x')  # x 或 y
        length = Lx if direction == 'x' else Ly
        # 底筋长度 = 板净跨 + 两端伸入支座 (max(5d, 支座宽/2))
        bearing = data.get('bearing_width', 200)  # 支座宽度
        single_len = length + 2 * max(5 * dia, bearing / 2)
        count = (length // spacing) + 1
        add_item(f'板底筋{direction}向 D{dia}@{spacing}', dia, count, single_len)

    # 2. 面筋 (支座负筋)
    for rb in data.get('top_rebars', []):
        dia = rb['d']
        spacing = rb['spacing']
        extend = rb.get('extend', Lx / 4)  # 伸出长度 = 板跨/4
        # 负筋长度 = 平直段 + 两端弯折 (板厚 - 2×保护层)
        bend = data['thickness'] - 2 * cover
        single_len = extend + 2 * bend
        count = (Ly // spacing) + 1
        add_item(f'板面筋 D{dia}@{spacing}', dia, count, single_len)

    # 3. 分布筋
    for rb in data.get('distribution_rebars', []):
        dia = rb['d']
        spacing = rb['spacing']
        single_len = Lx  # 分布筋贯通
        count = (Ly // spacing) + 1
        add_item(f'分布筋 D{dia}@{spacing}', dia, count, single_len)

    r['total_kg'] = round(r['total_kg'], 2)
    return r

def _wall_rebar(data: dict) -> dict:
    """剪力墙钢筋算量 (16G101-1)"""
    r = {'items': [], 'total_kg': 0.0}
    L, H, t = data['length'], data['height'], data['thickness']
    cover = data.get('cover', 15)

    def add_item(name, dia, count, single_len):
        wt = count * single_len / 1000 * REBAR_WEIGHT.get(dia, 0.00617*dia**2)
        r['items'].append({'name': name, 'd': dia, 'count': count,
                           'length_mm': round(single_len), 'weight_kg': round(wt, 2)})
        r['total_kg'] += wt

    # 1. 竖向分布筋
    for rb in data.get('vertical_rebars', []):
        dia = rb['d']
        spacing = rb['spacing']
        single_len = H + data.get('lap_length', 1.2 * anchorage_length(2) * dia)
        count = (L // spacing) + 1
        add_item(f'墙竖筋 D{dia}@{spacing}', dia, count, single_len)

    # 2. 水平分布筋
    for rb in data.get('horizontal_rebars', []):
        dia = rb['d']
        spacing = rb['spacing']
        single_len = L + 2 * 15 * dia  # 两端弯锚15d
        count = (H // spacing) + 1
        add_item(f'墙水平筋 D{dia}@{spacing}', dia, count, single_len)

    # 3. 拉筋
    for rb in data.get('tie_rebars', []):
        dia = rb['d']
        spacing = rb.get('spacing', 600)
        tie_len = t - 2 * cover + 2 * 11.9 * dia  # 拉筋长度
        count_x = (L // spacing) + 1
        count_y = (H // spacing) + 1
        add_item(f'墙拉筋 D{dia}@{spacing}', dia, count_x * count_y, tie_len)

    r['total_kg'] = round(r['total_kg'], 2)
    return r

def _foundation_rebar(data: dict) -> dict:
    """基础钢筋算量"""
    r = {'items': [], 'total_kg': 0.0}
    L, W, H = data['length'], data['width'], data['height']
    cover = data.get('cover', 40)

    def add_item(name, dia, count, single_len):
        wt = count * single_len / 1000 * REBAR_WEIGHT.get(dia, 0.00617*dia**2)
        r['items'].append({'name': name, 'd': dia, 'count': count,
                           'length_mm': round(single_len), 'weight_kg': round(wt, 2)})
        r['total_kg'] += wt

    # 底筋双向
    for rb in data.get('bottom_rebars', []):
        dia = rb['d']
        spacing = rb['spacing']
        direction = rb.get('direction', 'x')
        base_len = L if direction == 'x' else W
        single_len = base_len - 2 * cover + 2 * 6.25 * dia  # 180°弯钩
        count = (W // spacing + 1) if direction == 'x' else (L // spacing + 1)
        add_item(f'基础底筋{direction}向 D{dia}@{spacing}', dia, count, single_len)

    r['total_kg'] = round(r['total_kg'], 2)
    return r
```

#### 2.1.5 土方工程量（完整版）

**三种计算方法 + 放坡系数 + 工作面**

```
放坡系数表 (GB 50500):
┌──────────┬──────────────┬──────────────┬──────────────┐
│ 土质类别  │ 放坡起点(m)  │ 人工挖土      │ 机械挖土      │
│          │              │ (坑内/坑上)   │ (坑内/坑上)   │
├──────────┼──────────────┼──────────────┼──────────────┤
│ 一、二类土 │    1.20      │ 1:0.50/0.75  │ 1:0.33/0.67  │
│ 三类土    │    1.50      │ 1:0.33/0.67  │ 1:0.25/0.50  │
│ 四类土    │    2.00      │ 1:0.25/0.33  │ 1:0.10/0.33  │
└──────────┴──────────────┴──────────────┴──────────────┘

工作面宽度:
  砖基础: 200mm (每边)
  混凝土基础垫层: 300mm
  混凝土基础支模: 300mm
  地下室防水: 800mm (有外防水层)
  垂直挡土板: 100mm

沟槽土方: V = (B + 2C + KH) × H × L
  其中 B=底宽, C=工作面, K=放坡系数, H=深度, L=长度

基坑土方: V = (A + 2C + KH) × (B + 2C + KH) × H + 1/3 × K² × H³
  (倒棱台公式, 含四角放坡)
```

```python
def calculate_earthwork_full(data: dict) -> dict:
    """
    土方完整算量
    包含: 平整场地、挖沟槽、挖基坑、挖一般土方、回填、余土外运
    依据: GB 50500-2013, GB 50202《建筑地基基础工程施工质量验收规范》
    """
    q = {}

    # ---- 放坡系数 ----
    slope_table = {
        ('一、二类', '人工'): 0.50, ('一、二类', '机械坑内'): 0.33, ('一、二类', '机械坑上'): 0.75,
        ('三类', '人工'): 0.33, ('三类', '机械坑内'): 0.25, ('三类', '机械坑上'): 0.67,
        ('四类', '人工'): 0.25, ('四类', '机械坑内'): 0.10, ('四类', '机械坑上'): 0.33,
    }
    soil_type = data.get('soil_type', '三类')
    dig_method = data.get('dig_method', '人工')
    K = slope_table.get((soil_type, dig_method), 0.33)
    C = data.get('working_space', 300)  # 工作面 mm

    # ---- 1. 平整场地 ----
    # 平整场地 = 外墙外边线外放2m面积
    length = data.get('building_length', 0)
    width = data.get('building_width', 0)
    q['leveling_area'] = (length + 4) * (width + 4)  # m²

    # ---- 2. 挖沟槽土方 ----
    # V = (B + 2C + KH) × H × L
    trench = data.get('trench', {})
    if trench:
        B = trench.get('width', 0)  # 底宽 mm
        H = trench.get('depth', 0)  # 深度 mm
        L = trench.get('length', 0)  # 长度 mm
        if H / 1000 >= data.get('slope_start', 1.5):  # 超过放坡起点
            K_used = K
        else:
            K_used = 0  # 不放坡
        Bm, Cm, Hm, K_used, Lm = B/1000, C/1000, H/1000, K_used, L/1000
        q['trench_excavation'] = (Bm + 2*Cm + K_used*Hm) * Hm * Lm  # m³

    # ---- 3. 挖基坑土方 ----
    # V = (A+2C+KH)(B+2C+KH)H + 1/3×K²×H³
    pit = data.get('pit', {})
    if pit:
        A = pit.get('length', 0) / 1000  # m
        B = pit.get('width', 0) / 1000
        H = pit.get('depth', 0) / 1000
        Cm = C / 1000
        if H >= data.get('slope_start', 1.5):
            K_used = K
        else:
            K_used = 0
        q['pit_excavation'] = (A + 2*Cm + K_used*H) * (B + 2*Cm + K_used*H) * H + K_used**2 * H**3 / 3

    # ---- 4. 挖一般土方 (场地大开挖) ----
    if 'general_excavation' in data:
        ge = data['general_excavation']
        L, W, H = ge['length']/1000, ge['width']/1000, ge['depth']/1000
        Cm = C / 1000
        K_used = K if H >= data.get('slope_start', 1.5) else 0
        q['general_excavation'] = (L + 2*Cm + K_used*H) * (W + 2*Cm + K_used*H) * H + K_used**2 * H**3 / 3

    # ---- 5. 回填土 ----
    # 基础回填 = 挖方 - 基础及垫层体积
    # 室内回填 = 主墙间净面积 × (室内外高差 - 地面面层及垫层厚)
    total_excavation = sum(v for k, v in q.items() if 'excavation' in k)
    foundation_vol = data.get('foundation_volume', 0)  # 基础构件体积 m³
    q['backfill'] = total_excavation - foundation_vol

    # ---- 6. 余土外运 ----
    # 余土 = 挖方 × 松散系数 - 回填 / 压实系数
    loose_factor = {'一、二类': 1.20, '三类': 1.25, '四类': 1.30}
    Ks = loose_factor.get(soil_type, 1.25)
    q['surplus_soil'] = total_excavation * Ks - q['backfill'] / 0.94  # 压实系数 0.94

    return {k: round(v, 3) for k, v in q.items()}
```

#### 2.1.6 方格网法土方（详细版）

```python
def earthwork_grid_method(points, design_elev, grid_size=10.0):
    """
    方格网法详细计算
    八个公式处理零线穿越情况

    公式:
    全挖/全填: V = a²/4 × (h1+h2+h3+h4)
    三挖一填: V填 = a²/6 × ht³/[(h1+h3)(h2+h3)]
    两挖两填: V填 = a²/4 × (h1+h2)²/(h1+h2+h3+h4)
    一挖三填: V挖 = a²/6 × hw³/[(h1+h3)(h2+h3)]
    其中 h1,h2,h3,h4 为四个角点的施工高度
    同号角点用"挖"或"填"统一
    """
    cut = 0.0; fill = 0.0
    rows, cols = len(points), len(points[0])
    a = grid_size

    for i in range(rows - 1):
        for j in range(cols - 1):
            h1 = points[i][j] - design_elev
            h2 = points[i][j+1] - design_elev
            h3 = points[i+1][j] - design_elev
            h4 = points[i+1][j+1] - design_elev

            heights = [h1, h2, h3, h4]
            pos = [h > 0 for h in heights]
            pos_count = sum(pos)
            neg_count = 4 - pos_count

            if pos_count == 4:
                fill += a**2 * sum(heights) / 4
            elif neg_count == 4:
                cut += a**2 * abs(sum(heights)) / 4
            elif pos_count == 1:
                # 一挖三填(一正三负) 或 一填三挖
                abs_h = [abs(h) for h in heights]
                idx = next(ii for ii, p in enumerate(pos) if p == (pos_count == 1))
                h_opposite = [abs_h[(idx+1)%4], abs_h[(idx+3)%4]]
                V_small = a**2 * abs_h[idx]**3 / (6 * (abs_h[idx] + h_opposite[0]) * (abs_h[idx] + h_opposite[1]))
                V_large = a**2 * (2 * sum(abs_h) - abs_h[idx]) / 6
                if pos_count == 1:
                    fill += V_small; cut += V_large
                else:
                    cut += V_small; fill += V_large
            elif pos_count == 2:
                # 两挖两填
                if pos[0] == pos[1]:  # 同侧
                    h_same = [abs(heights[0]), abs(heights[1])]
                    h_opp = [abs(heights[2]), abs(heights[3])]
                    V_pos = a**2 * sum(h_same**2) / (4 * sum(h_same))
                    V_neg = a**2 * sum(h_opp**2) / (4 * sum(h_opp))
                else:  # 对角
                    V_pos = a**2 * sum([abs_h[ii] for ii, p in enumerate(pos) if p]) / 4
                    V_neg = a**2 * sum([abs_h[ii] for ii, p in enumerate(pos) if not p]) / 4
                fill += V_pos; cut += V_neg

    return {'cut': round(cut, 3), 'fill': round(fill, 3)}
```

#### 2.1.7 防水工程量

```python
def calculate_waterproof(data: dict) -> dict:
    """
    防水工程量计算
    依据: GB 50108《地下工程防水技术规范》, GB 50345《屋面工程技术规范》

    屋面防水: 按设计图示尺寸以面积计算
      平屋面: 按水平投影面积 + 女儿墙弯起(250mm)
      坡屋面: 按斜面积计算
      不扣除: 房上烟囱、风帽底座、风道、屋面小气窗和斜沟面积≤0.3m²

    地下防水: 按设计图示尺寸以面积计算
      底板防水: 底板面积 + 底板侧面
      外墙防水: 外墙外边线 × 高度
      顶板防水: 顶板面积
    """
    q = {}

    # 屋面防水
    roof = data.get('roof', {})
    if roof:
        area = roof['area']
        roof_type = roof.get('type', 'flat')
        if roof_type == 'flat':
            # 平屋面: 水平面积 + 女儿墙弯起
            parapet = roof.get('parapet_length', 0)  # 女儿墙长度
            q['roof_waterproof'] = area + parapet * 0.25  # 弯起250mm
        elif roof_type == 'slope':
            # 坡屋面: 水平面积 / cos(坡度)
            slope = roof.get('slope_degree', 0)
            import math
            q['roof_waterproof'] = area / math.cos(math.radians(slope))
        q['roof_insulation'] = area  # 屋面保温 = 面积

    # 地下防水
    basement = data.get('basement', {})
    if basement:
        q['basement_bottom_wp'] = basement['length'] * basement['width']
        q['basement_wall_wp'] = 2 * (basement['length'] + basement['width']) * basement['height']
        q['basement_top_wp'] = basement['length'] * basement['width']

    # 卫生间/厨房防水
    wet_rooms = data.get('wet_rooms', [])
    q['room_waterproof'] = 0
    for room in wet_rooms:
        area = room['length'] * room['width']
        # 上翻: 墙面防水上翻 ≥ 300mm (淋浴区 ≥ 1800mm)
        upstand = room.get('upstand_height', 0.3)
        perimeter = 2 * (room['length'] + room['width'])
        q['room_waterproof'] += area + perimeter * upstand

    return {k: round(v, 3) for k, v in q.items()}
```

#### 2.1.8 保温工程量

```python
def calculate_insulation(data: dict) -> dict:
    """
    保温工程量计算
    依据: GB 50500-2013, JGJ 144《外墙外保温工程技术规程》

    外墙保温面积 = 外墙外边线 × 保温层高度 - 门窗洞口面积 + 门窗洞口侧壁
    屋面保温体积 = 屋面面积 × 保温层厚度
    """
    q = {}

    # 外墙保温
    wall = data.get('exterior_wall', {})
    if wall:
        perimeter = wall['perimeter']
        height = wall['height']
        openings = wall.get('openings', [])
        opening_area = sum(o['width'] * o['height'] for o in openings)
        # 洞口侧壁保温 = 洞口周长 × 保温厚度
        opening_side = sum(2 * (o['width'] + o['height']) * 0.08 for o in openings)
        q['wall_insulation'] = perimeter * height - opening_area + opening_side

    # 屋面保温
    roof = data.get('roof', {})
    if roof:
        q['roof_insulation'] = roof['area'] * roof.get('insulation_thickness', 0.05)

    # 楼地面保温
    floor = data.get('floor', {})
    if floor:
        q['floor_insulation'] = floor['area'] * floor.get('insulation_thickness', 0.03)

    return {k: round(v, 3) for k, v in q.items()}
```

#### 2.1.9 装饰装修工程量

```python
def calculate_decoration(data: dict) -> dict:
    """
    装饰装修工程量
    依据: GB 50500-2013, GB 50210

    楼地面: 按主墙间净面积
    墙面抹灰: 内墙净长 × 净高 - 门窗洞口
    天棚抹灰: 主墙间净面积(梁侧并入)
    外墙抹灰: 外边线 × 高度 - 门窗洞口
    踢脚线: 内墙净长 (扣除门洞, 不扣除门洞侧壁)
    """
    q = {}

    # 楼地面
    floor = data.get('floor', {})
    if floor:
        q['floor_area'] = floor['area']
        q['skirting_length'] = floor.get('internal_perimeter', 0)  # 踢脚线

    # 内墙抹灰
    for wall in data.get('interior_walls', []):
        L, H = wall['length'], wall['height']
        openings = wall.get('openings', [])
        opening_area = sum(o['width'] * o['height'] for o in openings)
        q.setdefault('wall_plaster', 0)
        q['wall_plaster'] += L * H - opening_area

    # 天棚抹灰
    q['ceiling_plaster'] = data.get('ceiling_area', 0)

    # 外墙抹灰
    ext = data.get('exterior_wall', {})
    if ext:
        perimeter = ext['perimeter']
        height = ext['height']
        openings = ext.get('openings', [])
        opening_area = sum(o['width'] * o['height'] for o in openings)
        q['exterior_plaster'] = perimeter * height - opening_area

    # 涂料/油漆
    q['paint_area'] = q.get('wall_plaster', 0) + q.get('ceiling_plaster', 0)

    return {k: round(v, 3) for k, v in q.items()}
```

#### 2.1.10 门窗工程量

```python
def calculate_doors_windows(data: dict) -> dict:
    """
    门窗工程量
    按设计图示洞口尺寸以面积计算 (樘/m²)
    """
    q = {'door_count': 0, 'door_area': 0, 'window_count': 0, 'window_area': 0}

    for door in data.get('doors', []):
        q['door_count'] += 1
        q['door_area'] += door['width'] * door['height']

    for window in data.get('windows', []):
        q['window_count'] += 1
        q['window_area'] += window['width'] * window['height']

    return q
```

#### 2.1.11 屋面工程量

```python
def calculate_roof(data: dict) -> dict:
    """
    屋面工程完整算量
    包括: 找平层、找坡层、保温层、防水层、保护层
    """
    q = {}
    area = data['area']
    slope = data.get('slope', 0.02)  # 找坡坡度

    # 找坡层平均厚度 = 最薄处 + 坡长 × 坡度 / 2
    min_thickness = data.get('min_thickness', 0.03)  # 最薄处 30mm
    slope_length = data.get('slope_length', (area**0.5))  # 坡长
    avg_thickness = min_thickness + slope_length * slope / 2

    q['leveling_area'] = area  # 找平层 = 面积
    q['slope_volume'] = area * avg_thickness  # 找坡层体积
    q['insulation_volume'] = area * data.get('insulation_thickness', 0.05)
    q['waterproof_area'] = area  # 防水层
    q['protection_area'] = area  # 保护层

    return {k: round(v, 3) for k, v in q.items()}
```

### 2.2 市政工程量计算

```python
def calculate_municipal_full(data: dict) -> dict:
    """
    市政工程量完整计算
    依据: GB 50500-2013, CJJ 1, CJJ 2, GB 50268, GB 50014
    """
    q = {}

    # ---- 道路工程 ----
    road = data.get('road', {})
    if road:
        q['road_area'] = road['length'] * road['width']
        q['curb_length'] = road['length'] * 2
        q['sidewalk_area'] = road['length'] * road.get('sidewalk_width', 2.0) * 2
        # 路基土方
        q['subgrade_volume'] = road['length'] * road['width'] * road.get('subgrade_thickness', 0.3)
        # 路面结构层
        for layer, thickness in road.get('pavement_layers', {}).items():
            q[f'pavement_{layer}'] = road['length'] * road['width'] * thickness

    # ---- 排水工程 ----
    drainage = data.get('drainage', {})
    if drainage:
        q['pipe_length'] = drainage['length']
        # 沟槽土方 = (底宽+放坡) × 深 × 长
        B = drainage.get('trench_width', 1.0)
        H = drainage.get('trench_depth', 2.0)
        slope = drainage.get('slope_coefficient', 0.33)
        q['pipe_trench'] = (B + slope * H) * H * drainage['length']
        q['pipe_bedding'] = B * drainage.get('bedding_thickness', 0.15) * drainage['length']
        q['pipe_backfill'] = q['pipe_trench'] - 3.1416 * (drainage.get('pipe_diameter', 0.3)/2)**2 * drainage['length']

    # ---- 检查井 ----
    manhole = data.get('manhole', {})
    if manhole:
        count = manhole.get('count', 0)
        D = manhole.get('diameter', 1.0)
        depth = manhole.get('depth', 2.0)
        t = manhole.get('wall_thickness', 0.24)
        q['manhole_count'] = count
        q['manhole_excavation'] = count * 3.1416 * ((D/2 + 0.3)**2) * depth  # 工作面0.3m
        q['manhole_concrete'] = count * 3.1416 * (D/2)**2 * 0.2  # 底板
        q['manhole_brickwork'] = count * 3.1416 * D * depth * t
        q['manhole_cover'] = count  # 井盖

    # ---- 给水工程 ----
    water = data.get('water_supply', {})
    if water:
        q['water_pipe_length'] = water['length']
        q['water_valve_count'] = water.get('valve_count', 0)
        q['water_hydrant_count'] = water.get('hydrant_count', 0)
        q['water_trench'] = (water.get('trench_width', 0.8) + 0.33 * water.get('trench_depth', 1.5)) * water.get('trench_depth', 1.5) * water['length']

    # ---- 桥梁工程 ----
    bridge = data.get('bridge', {})
    if bridge:
        q['bridge_deck_area'] = bridge['length'] * bridge['width']
        q['bridge_pier_concrete'] = sum(p['volume'] for p in bridge.get('piers', []))
        q['bridge_abutment_concrete'] = sum(a['volume'] for a in bridge.get('abutments', []))
        q['bridge_bearing_count'] = bridge.get('bearing_count', 0)
        q['bridge_expansion_joint'] = bridge.get('expansion_joint_length', 0)

    return {k: round(v, 3) if isinstance(v, float) else v for k, v in q.items()}
```

### 2.3 公路工程量计算

```python
def calculate_highway_full(alignment, cross_sections, params: dict) -> dict:
    """
    公路工程量完整计算 (JTG 3820-2018)
    """
    q = {}

    L = alignment['length']
    W = params.get('road_width', 7.5)

    # ---- 路基工程 ----
    q.update(_highway_subgrade(cross_sections))

    # ---- 路面工程 ----
    # 面层、基层、底基层、垫层
    for layer_name, thickness in params.get('pavement', {}).items():
        q[f'pavement_{layer_name}_area'] = L * W
        q[f'pavement_{layer_name}_volume'] = L * W * thickness

    # ---- 排水工程 ----
    q['side_ditch_length'] = L * 2 * params.get('ditch_rate', 0.8)
    q['culvert_count'] = params.get('culvert_count', 0)
    q['culvert_length'] = sum(c['length'] for c in params.get('culverts', []))

    # ---- 防护工程 ----
    q['slope_protection'] = L * params.get('slope_height', 3.0) * 2 * params.get('slope_rate', 0.5)
    q['retaining_wall_volume'] = sum(w['volume'] for w in params.get('retaining_walls', []))

    # ---- 交通安全设施 ----
    q['guardrail_length'] = L * 2 * params.get('guardrail_rate', 0.8)
    q['marking_area'] = L * params.get('marking_width', 0.15) * params.get('marking_lines', 2)
    q['sign_count'] = params.get('sign_count', 0)

    # ---- 绿化 ----
    q['greening_area'] = L * params.get('greening_width', 2.0) * 2

    return {k: round(v, 3) if isinstance(v, float) else v for k, v in q.items()}

def _highway_subgrade(cross_sections: list) -> dict:
    """路基土石方（断面法 + 棱台公式）"""
    cut = 0.0; fill = 0.0
    for i in range(len(cross_sections) - 1):
        s1, s2 = cross_sections[i], cross_sections[i+1]
        d = s2['station'] - s1['station']
        for key in ['cut', 'fill']:
            a1 = s1.get(f'{key}_area', 0)
            a2 = s2.get(f'{key}_area', 0)
            if a1 > 0 and a2 > 0:
                ratio = max(a1,a2)/min(a1,a2) if min(a1,a2)>0 else 999
                if 0.5 <= ratio <= 2.0:
                    v = d/3 * (a1 + a2 + (a1*a2)**0.5)
                else:
                    v = (a1 + a2)/2 * d
                if key == 'cut': cut += v
                else: fill += v
    return {'subgrade_cut': round(cut, 3), 'subgrade_fill': round(fill, 3)}
```

### 2.4 幕墙工程量计算

```python
def calculate_curtain_wall_full(data: dict) -> dict:
    """
    幕墙工程量完整计算 (JGJ 102, JGJ 133, GB/T 21086)
    """
    q = {
        'glass_area': 0, 'stone_area': 0, 'metal_area': 0,
        'aluminum_frame_kg': 0, 'steel_frame_kg': 0,
        'steel_connector_kg': 0, 'sealant_m': 0,
        'insulation_area': 0, 'fire_stop_m': 0,
        'anchor_count': 0, 'bolt_count': 0,
    }

    # 面板 (玻璃/石材/金属)
    for panel in data.get('panels', []):
        area = panel['width'] * panel['height']
        mat = panel.get('material', 'glass')
        if mat == 'glass':
            q['glass_area'] += area
        elif mat == 'stone':
            q['stone_area'] += area
        elif mat == 'metal':
            q['metal_area'] += area
        q['sealant_m'] += 2 * (panel['width'] + panel['height'])

    # 框架
    for frame in data.get('frames', []):
        L = frame['length']
        mat = frame.get('material', 'aluminum')
        density = 2700 if mat == 'aluminum' else 7850
        area = frame['width'] * frame['height'] - frame.get('inner_width', 0) * frame.get('inner_height', 0)
        weight = area / 1e6 * density * L / 1000  # kg
        if mat == 'aluminum':
            q['aluminum_frame_kg'] += weight
        else:
            q['steel_frame_kg'] += weight

    # 连接件
    q['steel_connector_kg'] = data.get('connector_weight', 0)
    q['anchor_count'] = data.get('anchor_count', 0)
    q['bolt_count'] = data.get('bolt_count', 0)

    # 防火封堵
    q['fire_stop_m'] = data.get('fire_stop_length', 0)

    # 保温
    q['insulation_area'] = q['glass_area'] * data.get('insulation_ratio', 0.3)

    return {k: round(v, 3) if isinstance(v, float) else v for k, v in q.items()}
```

### 2.5 钢结构工程量

```python
def calculate_steel_full(components: list) -> dict:
    """
    钢结构完整算量 (GB 50500, GB 50205, GB 50017)
    支持: H型钢、箱型、圆管、角钢、槽钢、工字钢、T型钢
    """
    q = {'steel_kg': 0, 'surface_m2': 0, 'fireproof_m2': 0,
         'bolt_count': 0, 'weld_m': 0, 'detail': []}
    density = 7850

    for comp in components:
        comp_type = comp['type']
        L = comp['length']  # mm

        if comp_type == 'h_beam':
            h, b, tw, tf = comp['height'], comp['width'], comp['web_thickness'], comp['flange_thickness']
            area = (h - 2*tf) * tw + 2 * b * tf  # mm²
            weight = area / 1e6 * density * L / 1000  # kg
            surface = (2*b + 4*(h - 2*tf) + 2*tw) * L / 1e6  # m²

        elif comp_type == 'box_column':
            h, b, t = comp['height'], comp['width'], comp['thickness']
            area = 2 * (h + b - 2*t) * t
            weight = area / 1e6 * density * L / 1000
            surface = 2 * (h + b) * L / 1e6

        elif comp_type == 'pipe':
            D, t = comp['diameter'], comp['thickness']
            area = 3.1416 * (D - t) * t
            weight = area / 1e6 * density * L / 1000
            surface = 3.1416 * D * L / 1e6

        elif comp_type == 'angle':
            # 角钢 Lb×b×t
            b, t = comp['width'], comp['thickness']
            area = (2*b - t) * t
            weight = area / 1e6 * density * L / 1000
            surface = 4 * b * L / 1e6

        elif comp_type == 'channel':
            # 槽钢 [h×b×tw×tf
            h, b, tw, tf = comp['height'], comp['width'], comp['web_thickness'], comp['flange_thickness']
            area = (h - 2*tf) * tw + 2 * b * tf
            weight = area / 1e6 * density * L / 1000
            surface = (2*b + 2*(h - 2*tf) + h) * L / 1e6

        elif comp_type == 'i_beam':
            # 工字钢
            h, b, tw, tf = comp['height'], comp['width'], comp['web_thickness'], comp['flange_thickness']
            area = (h - 2*tf) * tw + 2 * b * tf
            weight = area / 1e6 * density * L / 1000
            surface = (2*b + 4*(h - 2*tf) + 2*tw) * L / 1e6

        else:
            continue

        q['steel_kg'] += weight
        q['surface_m2'] += surface
        q['fireproof_m2'] += surface
        q['bolt_count'] += comp.get('bolt_count', 0)
        q['weld_m'] += comp.get('weld_length_mm', 0) / 1000
        q['detail'].append({'type': comp_type, 'weight_kg': round(weight, 2)})

    for k in ['steel_kg', 'surface_m2', 'fireproof_m2', 'weld_m']:
        q[k] = round(q[k], 3)
    return q
```

### 2.6 隧道工程量

```python
def calculate_tunnel_full(data: dict) -> dict:
    """
    隧道工程量完整计算 (JTG 3660, JTG D70)
    """
    q = {'excavation': 0, 'shotcrete': 0, 'lining': 0,
         'bolt_count': 0, 'bolt_length': 0, 'arch_kg': 0,
         'waterproof': 0, 'invert': 0, 'pavement': 0}

    for section in data.get('sections', []):
        L = section['end_station'] - section['start_station']
        # 开挖量 (含超挖)
        overbreak = section.get('overbreak', 0.15)  # 超挖 15cm
        q['excavation'] += section['area'] * (1 + overbreak) * L
        # 喷射混凝土
        q['shotcrete'] += section['perimeter'] * section['shotcrete_t'] * L
        # 二衬
        q['lining'] += section['perimeter'] * section['lining_t'] * L
        # 锚杆
        q['bolt_count'] += section.get('bolts_per_m', 5) * L
        q['bolt_length'] += section.get('bolts_per_m', 5) * section.get('bolt_l', 3.0) * L
        # 钢拱架
        q['arch_kg'] += section.get('arch_kg_per_m', 50) * L
        # 防水
        q['waterproof'] += section['perimeter'] * L
        # 仰拱
        if section.get('invert_area', 0) > 0:
            q['invert'] += section['invert_area'] * L
        # 路面
        q['pavement'] += section.get('road_width', 7.0) * section.get('pavement_t', 0.26) * L

    return {k: round(v, 3) for k, v in q.items()}
```

### 2.7 工程量清单编码（完整版 GB 50500-2013）

#### 附录A - 土石方工程 (0101)

| 编码 | 项目名称 | 单位 | 计算规则 |
|------|---------|:--:|------|
| 010101001 | 平整场地 | m² | 外墙外边线外放2m面积 |
| 010101002 | 挖一般土方 | m³ | 设计图示尺寸 |
| 010101003 | 挖沟槽土方 | m³ | 垫层底宽×深×长 |
| 010101004 | 挖基坑土方 | m³ | 垫层底面积×深 |
| 010103001 | 回填方 | m³ | 挖方-基础体积 |
| 010103002 | 余方弃置 | m³ | 挖方-回填/压实系数 |

#### 附录A - 地基处理 (0102)

| 编码 | 项目名称 | 单位 |
|------|---------|:--:|
| 010201001 | 预制钢筋混凝土方桩 | m/m³ |
| 010201003 | 混凝土灌注桩 | m/m³ |
| 010202001 | 强夯地基 | m² |
| 010202008 | 高压喷射注浆 | m |

#### 附录A - 砌筑工程 (0104)

| 编码 | 项目名称 | 单位 |
|------|---------|:--:|
| 010401001 | 砖基础 | m³ |
| 010401003 | 实心砖墙 | m³ |
| 010401004 | 多孔砖墙 | m³ |
| 010401005 | 空心砖墙 | m³ |
| 010402001 | 砌块墙 | m³ |

#### 附录A - 混凝土及钢筋混凝土工程 (0105)

| 编码 | 项目名称 | 单位 | 编码 | 项目名称 | 单位 |
|------|---------|:--:|------|---------|:--:|
| 010501001 | 垫层 | m³ | 010502001 | 矩形柱 | m³ |
| 010502002 | 构造柱 | m³ | 010502003 | 异形柱 | m³ |
| 010503001 | 基础梁 | m³ | 010503002 | 矩形梁 | m³ |
| 010503003 | 异形梁 | m³ | 010503004 | 圈梁 | m³ |
| 010503005 | 过梁 | m³ | 010504001 | 直形墙 | m³ |
| 010505001 | 有梁板 | m³ | 010505002 | 无梁板 | m³ |
| 010505003 | 平板 | m³ | 010506001 | 直形楼梯 | m²/m³ |
| 010507001 | 散水、坡道 | m² | 010507002 | 台阶 | m²/m³ |
| 010515001 | 现浇构件钢筋 | t | 010515002 | 预制构件钢筋 | t |
| 010515003 | 钢筋网片 | t | 010515004 | 钢筋笼 | t |
| 010516001 | 预埋螺栓 | t | 010516002 | 预埋铁件 | t |

#### 附录A - 门窗工程 (0108)

| 编码 | 项目名称 | 单位 | 编码 | 项目名称 | 单位 |
|------|---------|:--:|------|---------|:--:|
| 010801001 | 木质门 | 樘/m² | 010802001 | 金属门 | 樘/m² |
| 010807001 | 金属窗 | 樘/m² | 010807005 | 塑钢窗 | 樘/m² |

#### 附录A - 屋面及防水工程 (0109)

| 编码 | 项目名称 | 单位 | 编码 | 项目名称 | 单位 |
|------|---------|:--:|------|---------|:--:|
| 010901001 | 屋面卷材防水 | m² | 010902001 | 墙面卷材防水 | m² |
| 010902002 | 墙面涂膜防水 | m² | 010903001 | 楼地面卷材防水 | m² |

#### 附录A - 保温隔热工程 (0110)

| 编码 | 项目名称 | 单位 | 编码 | 项目名称 | 单位 |
|------|---------|:--:|------|---------|:--:|
| 011001001 | 保温隔热屋面 | m² | 011001003 | 保温隔热墙面 | m² |
| 011001005 | 保温隔热楼地面 | m² | 011001006 | 保温隔热天棚 | m² |

#### 附录A - 装饰工程 (0111-0114)

| 编码 | 项目名称 | 单位 | 编码 | 项目名称 | 单位 |
|------|---------|:--:|------|---------|:--:|
| 011101001 | 水泥砂浆楼地面 | m² | 011201001 | 墙面一般抹灰 | m² |
| 011301001 | 天棚抹灰 | m² | 011406001 | 抹灰面油漆 | m² |

#### 附录B - 市政工程 (04)

| 编码 | 项目名称 | 单位 | 编码 | 项目名称 | 单位 |
|------|---------|:--:|------|---------|:--:|
| 040101001 | 挖一般土方 | m³ | 040103001 | 回填方 | m³ |
| 040201001 | 路床整形 | m² | 040202001 | 石灰稳定土 | m² |
| 040203001 | 水泥稳定土 | m² | 040203005 | 沥青混凝土路面 | m² |
| 040204001 | 人行道块料铺设 | m² | 040205001 | 安砌路缘石 | m |
| 040303001 | 预制混凝土梁 | m³ | 040501001 | 混凝土管道 | m |
| 040504001 | 砌筑检查井 | 座 | 040505001 | 雨水口 | 座 |

#### 附录C - 公路工程 (JTG 3820)

| 编码 | 项目名称 | 单位 | 编码 | 项目名称 | 单位 |
|------|---------|:--:|------|---------|:--:|
| 202-1 | 清理现场 | m² | 203-1 | 挖土方 | m³ |
| 204-1 | 利用土方填筑 | m³ | 205-1 | 软土地基处理 | m |
| 302-1 | 水泥稳定土底基层 | m² | 304-1 | 水泥稳定土基层 | m² |
| 308-1 | 透层 | m² | 309-1 | 黏层 | m² |
| 310-1 | 沥青混凝土面层 | m² | 403-1 | 基础钢筋 | kg |
| 504-1 | 圆管涵 | m | 602-1 | 护栏 | m |

---

## 三、CAD 转 BIM 模型 (CAD to BIM)

### 3.1 模型转换流程

```
CAD图纸 (DWG/DXF)
    ↓ 解析提取
几何数据 + 图层信息 + 属性
    ↓ 构件映射
IFC构件类型匹配
    ↓ 属性赋值 + LOD分级
带属性、带LOD的BIM模型
    ↓ 碰撞检测
优化后的BIM模型
    ↓ 导出
IFC 文件 (.ifc)
```

### 3.2 LOD (Level of Development) 定义

| LOD | 等级 | 内容 | 适用阶段 |
|-----|------|------|---------|
| LOD 100 | 概念设计 | 基本体量、位置、大致尺寸 | 方案设计 |
| LOD 200 | 初步设计 | 粗略几何、大致数量、类型 | 初步设计 |
| LOD 300 | 施工图设计 | 精确几何、尺寸、材质、属性 | 施工图设计 |
| LOD 350 | 深化设计 | 构件连接、预留预埋、加工信息 | 深化设计 |
| LOD 400 | 加工制造 | 加工级精度、安装信息、序列号 | 加工制造 |
| LOD 500 | 竣工运维 | 实际建造信息、运维参数 | 竣工交付 |

```python
def set_lod_level(model, element, lod_level: int):
    """设置构件的LOD等级"""
    lod_properties = {
        100: {'Precision': 'Conceptual', 'GeometryType': 'BoundingBox'},
        200: {'Precision': 'Schematic', 'GeometryType': 'Approximate'},
        300: {'Precision': 'Detailed', 'GeometryType': 'Precise'},
        350: {'Precision': 'Fabrication', 'GeometryType': 'PreciseWithConnections'},
        400: {'Precision': 'Manufacturing', 'GeometryType': 'ShopDrawing'},
        500: {'Precision': 'AsBuilt', 'GeometryType': 'Actual'},
    }
    props = lod_properties.get(lod_level, lod_properties[300])
    pset = run("pset.add_pset", model, product=element, name="LOD_Specification")
    if pset:
        run("pset.edit_pset", model, pset=pset, properties=props)
```

### 3.3 使用 IfcOpenShell 创建 BIM 模型（基础框架）

```python
import ifcopenshell
import ifcopenshell.api
from ifcopenshell.api import run

def create_bim_model_from_cad(cad_data, project_info):
    """从CAD数据创建BIM模型"""
    model = ifcopenshell.file(schema="IFC4")
    project = run("root.create_entity", model,
        ifc_class="IfcProject", name=project_info['name'])
    run("unit.assign_unit", model,
        length={"is_metric": True, "raw": "METERS"})
    site = run("root.create_entity", model,
        ifc_class="IfcSite", name="Site")
    building = run("root.create_entity", model,
        ifc_class="IfcBuilding", name=project_info['name'])
    run("aggregate.assign_object", model,
        relating_object=project, products=[site])
    run("aggregate.assign_object", model,
        relating_object=site, products=[building])
    return model
```

### 3.4 核心构件生成函数

```python
def add_wall_to_bim(model, storey, wall_data):
    """添加墙体到BIM模型"""
    wall = run("root.create_entity", model, ifc_class="IfcWall",
        name=wall_data.get('name', 'Wall'))
    psets = {
        "Pset_WallCommon": {
            "LoadBearing": wall_data.get('load_bearing', True),
            "ExtendToStructure": wall_data.get('extend_to_structure', False),
            "IsExternal": wall_data.get('is_external', True),
        },
        "Dimensions": {
            "Length": wall_data['length'], "Height": wall_data['height'],
            "Thickness": wall_data['thickness'],
        }
    }
    _apply_psets(model, wall, psets)
    if wall_data.get('lod'):
        set_lod_level(model, wall, wall_data['lod'])
    return wall

def add_beam_to_bim(model, storey, beam_data):
    """添加梁到BIM模型"""
    beam = run("root.create_entity", model, ifc_class="IfcBeam",
        name=beam_data.get('name', 'Beam'))
    psets = {
        "Pset_BeamCommon": {
            "LoadBearing": True, "IsExternal": False,
            "Span": beam_data['length'], "Slope": beam_data.get('slope', 0),
        },
        "Dimensions": {
            "Length": beam_data['length'], "Width": beam_data['width'],
            "Height": beam_data['height'],
        }
    }
    _apply_psets(model, beam, psets)
    return beam

def add_column_to_bim(model, storey, column_data):
    """添加柱到BIM模型"""
    column = run("root.create_entity", model, ifc_class="IfcColumn",
        name=column_data.get('name', 'Column'))
    psets = {
        "Pset_ColumnCommon": {
            "LoadBearing": True,
            "IsExternal": column_data.get('is_external', False),
            "Slope": 0,
        },
        "Dimensions": {
            "Width": column_data['width'], "Depth": column_data['depth'],
            "Height": column_data['height'],
        }
    }
    _apply_psets(model, column, psets)
    return column

def add_slab_to_bim(model, storey, slab_data):
    """添加楼板到BIM模型"""
    slab = run("root.create_entity", model, ifc_class="IfcSlab",
        name=slab_data.get('name', 'Slab'))
    psets = {
        "Pset_SlabCommon": {"IsExternal": False, "LoadBearing": True},
        "Dimensions": {"Area": slab_data['area'], "Thickness": slab_data['thickness']},
    }
    _apply_psets(model, slab, psets)
    return slab

def add_foundation_to_bim(model, site, foundation_data):
    """添加基础到BIM模型"""
    f_type = foundation_data.get('type', 'footing')
    ifc_class = {
        'footing': 'IfcFooting', 'pile': 'IfcPile', 'raft': 'IfcSlab',
    }.get(f_type, 'IfcFooting')
    foundation = run("root.create_entity", model, ifc_class=ifc_class,
        name=foundation_data.get('name', 'Foundation'))
    psets = {
        "Pset_FootingCommon": {
            "LoadBearing": True,
            "Punching": foundation_data.get('punching', False),
        },
        "Dimensions": {
            "Length": foundation_data['length'], "Width": foundation_data['width'],
            "Height": foundation_data['height'],
        }
    }
    _apply_psets(model, foundation, psets)
    return foundation

def _apply_psets(model, element, psets: dict):
    """批量添加属性集"""
    for pset_name, properties in psets.items():
        pset = run("pset.add_pset", model, product=element, name=pset_name)
        if pset:
            run("pset.edit_pset", model, pset=pset, properties=properties)

def export_bim_model(model, output_path):
    """导出BIM模型为IFC文件"""
    model.write(output_path)
    return output_path
```

### 3.5 碰撞检测

```python
def clash_detection(model, tolerance: float = 0.01) -> list:
    """BIM模型碰撞检测（基于包围盒）"""
    clashes = []
    elements = list(model.by_type('IfcBuildingElement'))
    for i in range(len(elements)):
        for j in range(i + 1, len(elements)):
            e1, e2 = elements[i], elements[j]
            if _is_normal_connection(e1, e2):
                continue
            bbox1 = _get_bounding_box(e1)
            bbox2 = _get_bounding_box(e2)
            if bbox1 and bbox2 and _bbox_overlap(bbox1, bbox2, tolerance):
                clashes.append({
                    'element1': {'id': e1.GlobalId, 'name': e1.Name, 'type': e1.is_a()},
                    'element2': {'id': e2.GlobalId, 'name': e2.Name, 'type': e2.is_a()},
                    'overlap_volume': _calc_overlap_volume(bbox1, bbox2),
                })
    return clashes

def _bbox_overlap(bbox1, bbox2, tolerance):
    """检查两个包围盒是否重叠"""
    return (bbox1[0][0] - tolerance < bbox2[1][0] and
            bbox1[1][0] + tolerance > bbox2[0][0] and
            bbox1[0][1] - tolerance < bbox2[1][1] and
            bbox1[1][1] + tolerance > bbox2[0][1] and
            bbox1[0][2] - tolerance < bbox2[1][2] and
            bbox1[1][2] + tolerance > bbox2[0][2])

def _get_bounding_box(element):
    """获取构件包围盒"""
    try:
        if hasattr(element, 'ObjectPlacement'):
            return ((0, 0, 0), (1, 1, 1))
    except:
        pass
    return None

def _is_normal_connection(e1, e2) -> bool:
    """判断是否为正常连接"""
    e1_type = e1.is_a()
    e2_type = e2.is_a()
    normal_pairs = [
        ('IfcBeam', 'IfcSlab'), ('IfcColumn', 'IfcBeam'),
        ('IfcWall', 'IfcSlab'), ('IfcFooting', 'IfcColumn'),
    ]
    return (e1_type, e2_type) in normal_pairs or (e2_type, e1_type) in normal_pairs
```

### 3.6 4D/5D BIM（进度与成本）

```python
def add_4d_schedule(model, element, start_date: str, end_date: str):
    """添加4D进度信息"""
    schedule_pset = {
        "Pset_ConstructionSchedule": {
            "StartDate": start_date,
            "EndDate": end_date,
            "Duration": f"{(end_date - start_date).days} days",
        }
    }
    _apply_psets(model, element, schedule_pset)

def add_5d_cost(model, element, cost_data: dict):
    """添加5D成本信息"""
    cost_pset = {
        "Pset_ConstructionCost": {
            "MaterialCost": cost_data.get('material_cost', 0),
            "LaborCost": cost_data.get('labor_cost', 0),
            "EquipmentCost": cost_data.get('equipment_cost', 0),
            "TotalUnitCost": cost_data.get('total_unit_cost', 0),
            "Currency": cost_data.get('currency', 'CNY'),
        }
    }
    _apply_psets(model, element, cost_pset)
```

### 3.7 BIM 模型质量检查

```python
def validate_bim_model(model) -> dict:
    """BIM模型质量检查"""
    report = {'errors': [], 'warnings': [], 'stats': {}}
    projects = model.by_type('IfcProject')
    if not projects:
        report['errors'].append('缺少 IfcProject')
    else:
        sites = model.by_type('IfcSite')
        if not sites:
            report['errors'].append('缺少 IfcSite')
    walls = model.by_type('IfcWall')
    columns = model.by_type('IfcColumn')
    beams = model.by_type('IfcBeam')
    slabs = model.by_type('IfcSlab')
    report['stats'] = {
        'walls': len(walls), 'columns': len(columns),
        'beams': len(beams), 'slabs': len(slabs),
    }
    unnamed = [e for e in model.by_type('IfcBuildingElement') if not e.Name]
    if unnamed:
        report['warnings'].append(f'有 {len(unnamed)} 个构件未命名')
    guids = [e.GlobalId for e in model]
    if len(guids) != len(set(guids)):
        report['errors'].append('存在重复的 GlobalId')
    return report
```

### 3.8 专业差异化 BIM 构件

#### 市政工程 BIM 构件
```python
def add_pipe_to_bim(model, alignment, pipe_data):
    """添加管道到市政BIM模型"""
    pipe = run("root.create_entity", model, ifc_class="IfcPipeSegment",
        name=pipe_data.get('name', 'Pipe'))
    psets = {
        "Pset_PipeSegmentCommon": {
            "Diameter": pipe_data['diameter'],
            "Material": pipe_data.get('material', 'HDPE'),
            "PressureRating": pipe_data.get('pressure_rating', 'PN10'),
        },
        "Dimensions": {
            "Length": pipe_data['length'],
            "InnerDiameter": pipe_data['inner_diameter'],
            "OuterDiameter": pipe_data['outer_diameter'],
        }
    }
    _apply_psets(model, pipe, psets)
    return pipe

def add_manhole_to_bim(model, location, manhole_data):
    """添加检查井到市政BIM模型"""
    manhole = run("root.create_entity", model,
        ifc_class="IfcDistributionChamberElement",
        name=manhole_data.get('name', 'Manhole'))
    return manhole
```

#### 公路工程 BIM 构件
```python
def add_road_alignment_to_bim(model, alignment_data):
    """添加道路线形到公路BIM模型"""
    alignment = run("root.create_entity", model, ifc_class="IfcAlignment",
        name=alignment_data.get('name', 'Road Alignment'))
    for segment in alignment_data.get('segments', []):
        if segment['type'] == 'straight': pass
        elif segment['type'] == 'curve': pass
        elif segment['type'] == 'spiral': pass
    return alignment

def add_bridge_to_bim(model, bridge_data):
    """添加桥梁到公路BIM模型"""
    bridge = run("root.create_entity", model, ifc_class="IfcBridge",
        name=bridge_data.get('name', 'Bridge'))
    for pier in bridge_data.get('piers', []):
        run("root.create_entity", model, ifc_class="IfcPier", name=pier['name'])
    for abutment in bridge_data.get('abutments', []):
        run("root.create_entity", model, ifc_class="IfcAbutment", name=abutment['name'])
    return bridge

def add_tunnel_to_bim(model, tunnel_data):
    """添加隧道到公路BIM模型"""
    tunnel = run("root.create_entity", model, ifc_class="IfcTunnel",
        name=tunnel_data.get('name', 'Tunnel'))
    psets = {
        "Pset_TunnelCommon": {
            "TunnelType": tunnel_data.get('type', 'Mountain'),
            "ExcavationMethod": tunnel_data.get('method', 'NATM'),
            "DesignSpeed": tunnel_data.get('design_speed', 80),
        }
    }
    _apply_psets(model, tunnel, psets)
    return tunnel
```

#### 幕墙工程 BIM 构件
```python
def add_curtain_wall_to_bim(model, building_storey, cw_data):
    """添加幕墙到BIM模型"""
    curtain_wall = run("root.create_entity", model,
        ifc_class="IfcCurtainWall", name=cw_data.get('name', 'CurtainWall'))
    psets = {
        "Pset_CurtainWallCommon": {
            "FireRating": cw_data.get('fire_rating', '60min'),
            "AcousticRating": cw_data.get('acoustic_rating', '35dB'),
            "ThermalTransmittance": cw_data.get('u_value', 1.8),
        },
        "Dimensions": {"Width": cw_data['width'], "Height": cw_data['height']},
    }
    _apply_psets(model, curtain_wall, psets)
    for panel in cw_data.get('panels', []):
        cp = run("root.create_entity", model, ifc_class="IfcPlate",
            name=panel.get('name', 'Panel'))
        _apply_psets(model, cp, {
            "Pset_PlateCommon": {
                "Material": panel.get('material', 'Glass'),
                "Thickness": panel.get('thickness', 12),
            }
        })
    return curtain_wall
```

---

## 四、全部国家规范与标准参考

> 涵盖六大专业方向（土建/市政/公路/幕墙/钢结构/隧道）及通用基础规范，共计 120+ 条。
> 优先级：国家标准(GB/GB/T) > 行业标准(JGJ/CJJ/JTG/TB) > 协会标准(CECS) > 标准图集(G/xxG)

### 4.0 通用基础规范

| 编号 | 规范名称 | 适用范围 |
|------|----------|----------|
| GB 50500-2013 | 建设工程工程量清单计价规范 | 全部工程量清单编制与计价 |
| GB 50854-2013 | 房屋建筑与装饰工程工程量计算规范 | 土建工程量计算规则 |
| GB/T 50353-2013 | 建筑工程建筑面积计算规范 | 建筑面积计算 |
| GB/T 50502-2009 | 建筑施工组织设计规范 | 施工组织设计 |
| GB 50300-2013 | 建筑工程施工质量验收统一标准 | 质量验收统一框架 |
| GB 50164-2011 | 混凝土质量控制标准 | 混凝土配制与质量控制 |
| GB/T 50107-2010 | 混凝土强度检验评定标准 | 混凝土强度统计评定 |
| GB/T 50080-2016 | 普通混凝土拌合物性能试验方法标准 | 混凝土拌合物试验 |
| GB/T 50081-2019 | 混凝土物理力学性能试验方法标准 | 混凝土力学性能试验 |
| GB/T 50082-2009 | 普通混凝土长期性能和耐久性能试验方法标准 | 混凝土耐久性试验 |
| GB/T 50476-2019 | 混凝土结构耐久性设计标准 | 混凝土耐久性设计 |
| GB 50119-2013 | 混凝土外加剂应用技术规范 | 外加剂选用与施工 |
| GB 175-2007 | 通用硅酸盐水泥 | 水泥产品标准 |
| GB/T 14684-2011 | 建设用砂 | 砂料质量标准 |
| GB/T 14685-2011 | 建设用卵石、碎石 | 石料质量标准 |
| GB 1499.1-2017 | 钢筋混凝土用钢 第1部分:热轧光圆钢筋 | HPB300钢筋 |
| GB 1499.2-2018 | 钢筋混凝土用钢 第2部分:热轧带肋钢筋 | HRB400/500钢筋 |
| GB/T 13788-2017 | 冷轧带肋钢筋 | CRB550/600H钢筋 |
| GB/T 5223-2014 | 预应力混凝土用钢丝 | 预应力钢丝 |
| GB/T 5224-2014 | 预应力混凝土用钢绞线 | 预应力钢绞线 |
| GB/T 1591-2018 | 低合金高强度结构钢 | Q355/Q390/Q420等 |
| JGJ/T 27-2014 | 钢筋焊接接头试验方法标准 | 焊接接头试验 |
| JGJ 18-2012 | 钢筋焊接及验收规程 | 钢筋焊接施工 |
| JGJ 107-2016 | 钢筋机械连接技术规程 | 直螺纹等机械连接 |
| GB/T 50218-2014 | 工程岩体分级标准 | 岩体质量分级 |
| GB 6722-2014 | 爆破安全规程 | 爆破设计与安全 |

---

### 4.1 土建工程规范

#### 4.1.1 结构设计

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| GB 50003-2011 | 砌体结构设计规范 | 砌体抗压/抗剪/高厚比 |
| GB 50007-2011 | 建筑地基基础设计规范 | 地基承载力/沉降/基础设计 |
| GB 50009-2012 | 建筑结构荷载规范 | 恒/活/风/雪/地震荷载 |
| GB 50010-2010(2015版) | 混凝土结构设计规范 | 正截面/斜截面/裂缝/挠度 |
| GB 50011-2010(2016版) | 建筑抗震设计规范 | 抗震等级/延性设计 |
| GB 50016-2014(2018版) | 建筑设计防火规范 | 耐火等级/防火分区 |
| GB 50017-2017 | 钢结构设计标准 | 钢结构强度/稳定/连接 |
| GB 50068-2018 | 建筑结构可靠性设计统一标准 | 可靠度/分项系数 |
| GB 50108-2008 | 地下工程防水技术规范 | 防水等级/设防要求 |
| GB 50345-2012 | 屋面工程技术规范 | 屋面防水/保温/排水 |

#### 4.1.2 施工与验收

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| GB 50202-2018 | 建筑地基基础工程施工质量验收标准 | 地基/桩基/基坑验收 |
| GB 50203-2011 | 砌体结构工程施工质量验收规范 | 砌筑质量/拉结筋 |
| GB 50204-2015 | 混凝土结构工程施工质量验收规范 | 模板/钢筋/混凝土验收 |
| GB 50207-2012 | 屋面工程质量验收规范 | 找平/防水/保温层验收 |
| GB 50208-2011 | 地下防水工程质量验收规范 | 防水混凝土/卷材验收 |
| GB 50209-2010 | 建筑地面工程施工质量验收规范 | 基层/面层/踢脚线验收 |
| GB 50210-2018 | 建筑装饰装修工程质量验收标准 | 抹灰/吊顶/饰面验收 |
| GB 50212-2014 | 建筑防腐蚀工程施工规范 | 防腐面层/隔离层 |
| GB 50327-2001 | 住宅装饰装修工程施工规范 | 住宅装修施工工艺 |
| GB 50411-2019 | 建筑节能工程施工质量验收标准 | 保温/门窗/幕墙节能 |

#### 4.1.3 标准图集（构造详图）

| 编号 | 图集名称 | 核心内容 |
|------|----------|----------|
| 22G101-1 | 现浇混凝土框架/剪力墙/梁/板 | 平面整体表示方法制图规则 |
| 22G101-2 | 现浇混凝土板式楼梯 | 梯板配筋/构造详图 |
| 22G101-3 | 独立基础/条形基础/筏形基础/桩基础 | 基础配筋/构造详图 |
| 18G901-1 | 混凝土结构施工钢筋排布规则与构造详图 | 钢筋排布/间距控制 |
| 18G901-2 | 现浇混凝土板式楼梯钢筋排布 | 楼梯钢筋排布 |
| 18G901-3 | 独立基础/条形基础/筏形基础钢筋排布 | 基础钢筋排布 |

---

### 4.2 市政工程规范

#### 4.2.1 给排水

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| GB 50013-2018 | 室外给水设计标准 | 给水管网/水厂设计 |
| GB 50014-2021 | 室外排水设计标准 | 雨污水管网/泵站设计 |
| GB 50015-2019 | 建筑给水排水设计标准 | 建筑内部给排水 |
| GB 50141-2008 | 给水排水构筑物工程施工及验收规范 | 水池/泵房施工验收 |
| GB 50268-2008 | 给水排水管道工程施工及验收规范 | 管道开槽/顶管/闭水试验 |
| GB 50289-2016 | 城市工程管线综合规划规范 | 管线综合/间距控制 |
| GB 50318-2017 | 城市排水工程规划规范 | 排水系统规划 |

#### 4.2.2 道路桥梁

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| CJJ 1-2008 | 城镇道路工程施工与质量验收规范 | 路基/基层/面层施工验收 |
| CJJ 2-2008 | 城市桥梁工程施工与质量验收规范 | 桥梁上下部结构施工验收 |
| CJJ 37-2012(2016版) | 城市道路工程设计规范 | 道路线形/横断面/交叉口 |
| CJJ 139-2010 | 城市桥梁桥面防水工程技术规程 | 桥面防水层设计施工 |
| CJJ 169-2012 | 城镇道路路面设计规范 | 沥青/水泥路面结构设计 |
| CJJ 194-2013 | 城市道路路基设计规范 | 路基填料/压实/边坡 |
| CJJ/T 135-2009 | 透水水泥混凝土路面技术规程 | 透水混凝土配合比与施工 |

#### 4.2.3 其他市政

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| CJJ 82-2012 | 园林绿化工程施工及验收规范 | 绿化种植/养护验收 |
| CJJ 89-2012 | 城市道路照明工程施工及验收规范 | 路灯/线缆施工验收 |
| CJJ 90-2009 | 生活垃圾焚烧处理工程技术规范 | 焚烧厂设计施工 |
| 18GL205 | 现浇混凝土综合管廊 (国家标准图集) | 管廊配筋/构造 |

---

### 4.3 公路工程规范

#### 4.3.1 总体与路线

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| JTG 3820-2018 | 公路工程工程量清单计量规则 | 公路清单编码与计量单位 |
| JTG B01-2014 | 公路工程技术标准 | 公路等级/设计速度/车道宽度 |
| JTG D20-2017 | 公路路线设计规范 | 平纵横设计/视距/超高 |

#### 4.3.2 路基路面

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| JTG D30-2015 | 公路路基设计规范 | 路基填料/边坡/支挡结构 |
| JTG D40-2011 | 公路水泥混凝土路面设计规范 | 水泥路面结构/接缝设计 |
| JTG D50-2017 | 公路沥青路面设计规范 | 沥青路面结构/材料设计 |
| JTG F10-2006 | 公路路基施工技术规范 | 路基填筑/碾压/检测 |
| JTG F40-2004 | 公路沥青路面施工技术规范 | 沥青混合料/摊铺/压实 |

#### 4.3.3 桥涵

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| JTG D60-2015 | 公路桥涵设计通用规范 | 荷载组合/冲击系数 |
| JTG D61-2005 | 公路圬工桥涵设计规范 | 石砌/混凝土圬工 |
| JTG 3362-2018 | 公路钢筋混凝土及预应力混凝土桥涵设计规范 | 正截面/斜截面/预应力 |
| JTG 3363-2019 | 公路桥涵地基与基础设计规范 | 桩基/沉井/扩大基础 |
| JTG D64-2015 | 公路钢结构桥梁设计规范 | 钢桥面板/稳定/疲劳 |
| JTG/T 3650-2020 | 公路桥涵施工技术规范 | 支架/挂篮/顶推施工 |

#### 4.3.4 试验检测

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| JTG E20-2011 | 公路工程沥青及沥青混合料试验规程 | 针入度/软化点/马歇尔 |
| JTG E30-2005 | 公路工程水泥及水泥混凝土试验规程 | 凝结时间/抗压抗折 |
| JTG E40-2007 | 公路工程土工试验规程 | 含水率/击实/CBR/界限含水率 |
| JTG E41-2005 | 公路工程岩石试验规程 | 单轴抗压/吸水率 |
| JTG E42-2005 | 公路工程集料试验规程 | 筛分/压碎值/磨耗 |
| JTG E50-2006 | 公路工程土工合成材料试验规程 | 拉伸/撕裂/顶破 |
| JTG E51-2009 | 公路工程无机结合料稳定材料试验规程 | 无侧限抗压/延迟时间 |
| JTG E60-2008 | 公路工程路基路面现场测试规程 | 弯沉/压实度/平整度 |
| JTG F80/1-2017 | 公路工程质量检验评定标准 第一册 土建工程 | 分项/分部/单位工程评定 |

---

### 4.4 幕墙工程规范

#### 4.4.1 设计与施工

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| JGJ 102-2003 | 玻璃幕墙工程技术规范 | 玻璃面板/横梁立柱/连接件 |
| JGJ 133-2001 | 金属与石材幕墙工程技术规范 | 铝板/钢板/石材幕墙 |
| JGJ 145-2013 | 混凝土结构后锚固技术规程 | 化学锚栓/扩底锚栓 |
| JGJ 113-2015 | 建筑玻璃应用技术规程 | 玻璃选型/安全玻璃 |
| GB/T 21086-2007 | 建筑幕墙 | 幕墙产品标准/性能分级 |
| GB 50009-2012 | 建筑结构荷载规范 | 风荷载/自重荷载计算 |

#### 4.4.2 检测与验收

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| JGJ/T 139-2020 | 玻璃幕墙工程质量检验标准 | 安装质量/观感质量 |
| GB/T 15227-2019 | 建筑幕墙气密/水密/抗风压性能检测方法 | 三性试验 |
| GB/T 18250-2015 | 建筑幕墙层间变形性能分级及检测方法 | 层间位移角 |
| GB/T 18575-2017 | 建筑幕墙抗震性能振动台试验方法 | 抗震试验 |
| GB/T 38264-2019 | 建筑幕墙耐撞击性能分级及检测方法 | 软体/硬体撞击 |

#### 4.4.3 材料

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| GB 15763.2-2005 | 建筑用安全玻璃 第2部分:钢化玻璃 | 钢化玻璃性能 |
| GB 15763.3-2009 | 建筑用安全玻璃 第3部分:夹层玻璃 | 夹层玻璃性能 |
| JC/T 882-2001 | 幕墙玻璃接缝用密封胶 | 硅酮密封胶 |

---

### 4.5 钢结构工程规范

#### 4.5.1 设计与施工

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| GB 50017-2017 | 钢结构设计标准 | 强度/稳定/疲劳/连接 |
| GB 50205-2020 | 钢结构工程施工质量验收标准 | 制作/安装/涂装验收 |
| GB 50661-2011 | 钢结构焊接规范 | 焊接工艺评定/焊缝质量 |
| GB 50755-2012 | 钢结构工程施工规范 | 制作/安装/卸载施工 |
| GB 51022-2015 | 门式刚架轻型房屋钢结构技术规范 | 门刚/檩条/墙梁 |
| JGJ 82-2011 | 钢结构高强度螺栓连接技术规程 | 扭剪型/大六角螺栓 |
| JGJ 99-2015 | 高层民用建筑钢结构技术规程 | 框架-支撑/伸臂桁架 |
| JGJ 7-2010 | 空间网格结构技术规程 | 网架/网壳/弦支穹顶 |
| JGJ 257-2012 | 索结构技术规程 | 索网/索桁架/张弦结构 |
| CECS 102-2002 | 门式刚架轻型房屋钢结构技术规程 | 门刚补充规定 |

#### 4.5.2 材料

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| GB/T 1591-2018 | 低合金高强度结构钢 | Q355/Q390/Q420/Q460 |
| GB/T 3632-2008 | 钢结构用扭剪型高强度螺栓连接副 | 螺栓/螺母/垫圈 |
| GB/T 5313-2010 | 厚度方向性能钢板 | Z向性能钢板 |
| GB/T 19879-2015 | 建筑结构用钢板 | 建筑用钢技术要求 |

---

### 4.6 隧道工程规范

#### 4.6.1 公路隧道

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| JTG D70-2004 | 公路隧道设计规范 | 围岩分级/衬砌/防排水 |
| JTG 3370.1-2018 | 公路隧道设计规范 第一册 土建工程 | 隧道结构/支护/洞门 |
| JTG 3660-2020 | 公路隧道施工技术规范 | 钻爆/掘进/衬砌/通风 |
| JTG/T 3660-2020 | 公路隧道施工技术规范(推荐性) | 施工补充技术 |
| JTG F80/1-2017 | 公路工程质量检验评定标准 | 隧道分项工程评定 |

#### 4.6.2 铁路隧道

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| TB 10003-2016 | 铁路隧道设计规范 | 铁路隧道/明洞/辅助坑道 |
| TB 10753-2018 | 高速铁路隧道工程施工质量验收标准 | 高铁隧道验收 |
| TB 10121-2015 | 铁路隧道施工机械化技术规范 | 机械化配套施工 |

#### 4.6.3 通用

| 编号 | 规范名称 | 核心内容 |
|------|----------|----------|
| GB 50086-2015 | 岩土锚杆与喷射混凝土支护工程技术规范 | 锚杆/钢架/喷射混凝土 |
| GB 50108-2008 | 地下工程防水技术规范 | 防水等级/防水措施 |
| GB 50208-2011 | 地下防水工程质量验收规范 | 防水层验收 |
| GB/T 50218-2014 | 工程岩体分级标准 | 围岩BQ分级法 |
| GB 6722-2014 | 爆破安全规程 | 钻爆法/控制爆破 |

---

### 4.7 规范使用优先级

在工程量计算和BIM建模中，当多条规范对同一问题有规定时，按以下优先级执行：

1. **强制性条文**（GB/GB 5xxxx 中黑体字部分） — 必须执行
2. **国家标准**（GB 5xxxx） — 优先执行
3. **国家标准（推荐性）**（GB/T 5xxxx） — 可选用
4. **行业标准**（JGJ/CJJ/JTG/TB） — 补充执行
5. **协会标准**（CECS） — 参考执行
6. **标准图集**（xxG101/xxG901） — 构造详图依据

### 4.8 规范版本检查清单

工程量计算时需确认以下规范版本是否为最新有效版本：

- 22G101 系列 > 16G101 系列 > 11G101 系列（图集迭代）
- GB 50010-2010(2015版) 局部修订
- GB 50011-2010(2016版) 局部修订
- GB 50016-2014(2018版) 局部修订
- JTG 3362-2018 替代 JTG D62-2004
- JTG 3363-2019 替代 JTG D63-2007
- JTG 3370.1-2018 替代 JTG D70-2004 隧道部分
- GB 50202-2018 替代 GB 50202-2002
- GB 50205-2020 替代 GB 50205-2001
- GB 50411-2019 替代 GB 50411-2007
- GB/T 50081-2019 替代 GB/T 50081-2002

---

## 五、完整工作流程示例

### 5.1 土建工程：CAD→算量→BIM→碰撞检查→导出

```python
def full_workflow_building(cad_path, output_ifc_path, output_excel_path):
    """土建工程完整工作流"""
    import ezdxf
    import ifcopenshell
    from ifcopenshell.api import run
    from openpyxl import Workbook
    import json

    # ===== Step 1: 加载CAD图纸 =====
    doc = ezdxf.readfile(cad_path)
    msp = doc.modelspace()
    drawing_info = parse_cad_drawing(cad_path)

    # ===== Step 2: 按图层提取构件 =====
    walls = extract_elements_by_layer(msp, ['WALL', '墙', 'WA-'])
    columns = extract_elements_by_layer(msp, ['COLUMN', '柱', 'KZ-'])
    beams = extract_elements_by_layer(msp, ['BEAM', '梁', 'KL-'])
    slabs = extract_elements_by_layer(msp, ['SLAB', '板', 'LB-'])
    foundations = extract_elements_by_layer(msp, ['FOUNDATION', '基础', 'JC-'])

    # ===== Step 3: 工程量计算 =====
    quantities = {}
    quantities['wall_concrete'] = calculate_concrete_and_formwork(walls, 'wall')
    quantities['column_concrete'] = calculate_concrete_and_formwork(columns, 'column')
    quantities['beam_concrete'] = calculate_concrete_and_formwork(beams, 'beam')
    quantities['slab_concrete'] = calculate_concrete_and_formwork(slabs, 'slab')
    quantities['foundation_concrete'] = calculate_concrete_and_formwork(foundations, 'foundation')

    # ===== Step 4: 导出工程量清单到Excel =====
    export_quantity_to_excel(quantities, output_excel_path)

    # ===== Step 5: 创建BIM模型 =====
    model = create_bim_model_from_cad(None, {'name': 'Building Project'})
    storey = run("root.create_entity", model,
        ifc_class="IfcBuildingStorey", name="Level 1")

    for w in walls: add_wall_to_bim(model, storey, w)
    for c in columns: add_column_to_bim(model, storey, c)
    for b in beams: add_beam_to_bim(model, storey, b)
    for s in slabs: add_slab_to_bim(model, storey, s)
    for f in foundations: add_foundation_to_bim(model, None, f)

    # ===== Step 6: 碰撞检测 =====
    clashes = clash_detection(model)
    if clashes:
        print(f"发现 {len(clashes)} 处碰撞:")
        for clash in clashes:
            print(f"  {clash['element1']['name']} <-> {clash['element2']['name']}")

    # ===== Step 7: 模型质量检查 =====
    validation = validate_bim_model(model)
    print(f"模型统计: {validation['stats']}")

    # ===== Step 8: 导出IFC =====
    export_bim_model(model, output_ifc_path)

    return {
        'quantities': quantities,
        'bim_model': output_ifc_path,
        'excel_report': output_excel_path,
        'clashes': len(clashes),
        'validation': validation,
    }
```

### 5.2 公路工程：路线→算量→BIM

```python
def full_workflow_highway(alignment_data, cross_sections, output_ifc_path):
    """公路工程完整工作流"""
    import ifcopenshell
    from ifcopenshell.api import run

    alignment = parse_alignment(alignment_data)
    quantities = calculate_highway_quantities(alignment, cross_sections, {})

    model = ifcopenshell.file(schema="IFC4")
    project = run("root.create_entity", model,
        ifc_class="IfcProject", name="Highway Project")
    add_road_alignment_to_bim(model, alignment)
    for section in cross_sections:
        add_cross_section_to_bim(model, section)

    export_bim_model(model, output_ifc_path)
    return quantities
```

### 5.3 隧道工程：地质剖面→算量→BIM

```python
def full_workflow_tunnel(geological_data, tunnel_design, output_ifc_path):
    """隧道工程完整工作流"""
    import ifcopenshell
    from ifcopenshell.api import run

    geology = parse_geological_profile(geological_data)
    tunnel_qty = calculate_tunnel_quantities(tunnel_design)

    model = ifcopenshell.file(schema="IFC4")
    project = run("root.create_entity", model,
        ifc_class="IfcProject", name="Tunnel Project")
    tunnel = add_tunnel_to_bim(model, tunnel_design)
    add_geological_model_to_bim(model, geology)

    export_bim_model(model, output_ifc_path)
    return tunnel_qty
```

---

## 六、实用工具集

### 6.1 坐标转换

```python
import math

def coordinate_transform(x, y, z, from_system: str, to_system: str) -> tuple:
    """
    常用工程坐标转换
    支持: WGS84, CGCS2000, 北京54, 西安80
    """
    if from_system == 'WGS84' and to_system == 'CGCS2000':
        return (x, y, z)
    if from_system == 'BJ54' and to_system == 'WGS84':
        dx, dy, dz = -22.0, 118.0, 30.5
        return (x + dx, y + dy, z + dz)
    return (x, y, z)

def gauss_kruger_to_lonlat(X, Y, central_meridian=114.0):
    """
    高斯-克吕格投影 → 经纬度
    """
    e2 = 0.006693421622966
    a = 6378137.0
    Bf = _compute_bottom_latitude(X, a, e2)
    return (0, 0)  # 简化
```

### 6.2 单位换算

```python
# 常用工程单位换算
UNIT_CONVERSIONS = {
    'length': {
        'mm_to_m': 0.001, 'cm_to_m': 0.01, 'm_to_km': 0.001,
        'inch_to_mm': 25.4, 'ft_to_m': 0.3048,
    },
    'area': {
        'mm2_to_m2': 1e-6, 'cm2_to_m2': 1e-4, 'm2_to_ha': 1e-4,
        'm2_to_km2': 1e-6, 'm2_to_mu': 0.0015,
    },
    'volume': {
        'mm3_to_m3': 1e-9, 'cm3_to_m3': 1e-6, 'L_to_m3': 0.001,
    },
    'mass': {
        'kg_to_t': 0.001, 'g_to_kg': 0.001,
    },
    'pressure': {
        'MPa_to_kPa': 1000, 'kPa_to_Pa': 1000, 'MPa_to_psi': 145.038,
    },
}

def convert_unit(value: float, from_unit: str, to_unit: str) -> float:
    """通用单位换算"""
    key = f"{from_unit}_to_{to_unit}"
    return value * UNIT_CONVERSIONS.get(key, 1.0)
```

### 6.3 Excel工程量清单导出

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

def export_quantity_to_excel(quantities: dict, output_path: str):
    """
    导出工程量清单到Excel
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "工程量清单"

    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font_white = Font(name='宋体', bold=True, size=12, color='FFFFFF')
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin'),
    )

    headers = ['序号', '清单编码', '项目名称', '单位', '工程量', '备注']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border

    row = 2
    for idx, (name, qty) in enumerate(quantities.items(), 1):
        ws.cell(row=row, column=1, value=idx).border = thin_border
        ws.cell(row=row, column=2, value=qty.get('code', '')).border = thin_border
        ws.cell(row=row, column=3, value=name).border = thin_border
        ws.cell(row=row, column=4, value=qty.get('unit', 'm³')).border = thin_border
        ws.cell(row=row, column=5, value=qty.get('value', 0)).border = thin_border
        ws.cell(row=row, column=6, value=qty.get('remark', '')).border = thin_border
        row += 1

    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 16
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 20

    wb.save(output_path)
    return output_path
```

### 6.4 图纸批量处理

```python
import os
import glob

def batch_process_cad(input_dir: str, output_dir: str):
    """
    批量处理CAD图纸
    支持: 批量转换、批量算量、批量导出
    """
    results = []
    dxf_files = glob.glob(os.path.join(input_dir, '*.dxf'))
    dwg_files = glob.glob(os.path.join(input_dir, '*.dwg'))

    for filepath in dxf_files + dwg_files:
        try:
            drawing_info = parse_cad_drawing(filepath)
            results.append({
                'file': os.path.basename(filepath),
                'status': 'success',
                'layers': len(drawing_info['layers']),
                'entities': sum(len(v) for v in drawing_info['entities'].values()),
            })
        except Exception as e:
            results.append({
                'file': os.path.basename(filepath),
                'status': 'error',
                'error': str(e),
            })

    return results
```

---

## 七、依赖库清单

```bash
# CAD 图纸解析
pip install ezdxf>=1.1.0           # DXF文件读写
pip install opencv-python>=4.8     # 图像处理与OCR

# BIM 建模
pip install ifcopenshell>=0.7.0    # IFC文件创建与编辑

# 工程量计算
pip install numpy>=1.24            # 数值计算
pip install shapely>=2.0           # 几何计算
pip install pandas>=2.0            # 数据处理

# 点云处理
pip install open3d>=0.17           # 点云处理与可视化
pip install laspy>=2.5             # LAS点云格式

# 报告生成
pip install openpyxl>=3.1          # Excel工程量清单
pip install matplotlib>=3.7        # 图表可视化
pip install xlsxwriter>=3.1        # 高级Excel导出

# GIS 支持
pip install geopandas>=0.13        # 地理数据处理
pip install fiona>=1.9             # 矢量数据读写
```

---

## 八、AI 调用指南 (AI Invocation Guide)

> 本章节为 AI 助手提供完整的关键字匹配、意图识别、函数路由和调用规范。

---

### 8.1 意图识别关键字矩阵

AI 收到用户消息后，按以下矩阵匹配意图。匹配优先级：**精确匹配 > 模糊匹配 > 专业领域匹配**。

#### 意图-01: 工程识图 (`drawing`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 识图、读图、看图 | parse drawing, read cad | `parse_cad_drawing()` |
| 解析CAD、解析DWG、解析DXF | parse dwg, parse dxf | `parse_cad_drawing()` |
| 提取尺寸、提取图元 | extract entities | `parse_cad_drawing()` |
| 图纸对比、版本对比 | compare drawings | `compare_drawings()` |
| 图层、图层分类 | layer, layer classification | `parse_cad_drawing()` |
| 图块、块定义、外部参照 | block, xref | `extract_block_definitions()` |
| 炸开块、展开块 | explode block | `explode_block_reference()` |
| 比例识别、图幅 | scale, paper size | `detect_drawing_scale()` |

#### 意图-02: 工程量计算 (`quantity`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 算量、工程量、计算工程量 | quantity, calculate quantity | 按构件类型路由 |
| 混凝土量、混凝土算量 | concrete quantity | `calculate_concrete_detail()` |
| 钢筋量、钢筋算量、钢筋重量 | rebar quantity, steel weight | `calculate_full_rebar()` |
| 锚固长度、搭接长度 | anchorage length, lap length | `anchorage_length()` |
| 土方量、土方算量、挖土 | earthwork, excavation | `calculate_earthwork_full()` |
| 方格网法、方格网土方 | grid method | `earthwork_grid_method()` |
| 砌体量、砖用量、砌筑量 | masonry, brick quantity | `calculate_masonry()` |
| 构造柱、过梁、圈梁、压顶 | tie column, lintel, ring beam | `calculate_secondary_elements()` |
| 防水面积、防水算量 | waterproof area | `calculate_waterproof()` |
| 保温层、保温算量 | insulation | `calculate_insulation()` |
| 装饰装修、抹灰、涂料 | decoration, plastering | `calculate_decoration()` |
| 门窗算量、门窗面积 | doors windows | `calculate_doors_windows()` |
| 屋面算量、屋面防水 | roof quantity | `calculate_roof()` |
| 市政算量、管道算量、道路算量 | municipal quantity | `calculate_municipal_full()` |
| 公路算量、路基算量、路面算量 | highway quantity | `calculate_highway_full()` |
| 幕墙算量、玻璃幕墙、石材幕墙 | curtain wall quantity | `calculate_curtain_wall_full()` |
| 钢结构算量、钢构件重量 | steel structure quantity | `calculate_steel_full()` |
| 隧道算量、衬砌算量 | tunnel quantity | `calculate_tunnel_full()` |
| 清单编码、GB50500、清单项 | bill code, BOQ code | 查阅02-quantity.md §2.7 |

#### 意图-03: CAD转BIM (`bim`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| BIM建模、转BIM、翻模 | bim model, convert to bim | `create_bim_model_from_cad()` |
| IFC模型、导出IFC | ifc model, export ifc | `export_bim_model()` |
| 添加墙、添加柱、添加梁 | add wall, add column | `add_wall_to_bim()` 等 |
| 碰撞检测、碰撞检查 | clash detection | `clash_detection()` |
| 模型检查、模型验证 | model validation | `validate_bim_model()` |
| 4D BIM、进度关联 | 4d bim | `add_4d_schedule()` |
| 5D BIM、造价关联 | 5d bim | `add_5d_cost()` |
| LOD等级、LOD分级 | lod level | `set_lod_level()` |
| 添加管道、添加井 | add pipe, add manhole | `add_pipe_to_bim()` 等 |
| 添加道路、添加桥梁 | add road, add bridge | `add_road_alignment_to_bim()` 等 |
| 添加隧道、添加幕墙 | add tunnel, add curtain wall | `add_tunnel_to_bim()` 等 |

#### 意图-04: 工程造价计价 (`pricing`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 计价、造价、报价 | pricing, cost, quote | `calculate_composite_unit_price()` |
| 综合单价 | composite unit price | `calculate_composite_unit_price()` |
| 措施费、措施项目费 | measure cost | `calculate_measure_cost()` |
| 规费、税金 | regulation, tax | `calculate_regulation_and_tax()` |
| 报价书、工程报价 | bid document | `generate_bid_document()` |
| 价差、材料价差 | price adjustment | `calculate_material_price_adjustment()` |

#### 意图-05: 施工安全计算 (`safety`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 脚手架验算、脚手架安全 | scaffold check | `check_scaffold_stability()` |
| 连墙件验算 | wall connector | `check_wall_connector()` |
| 模板支撑、模板验算 | formwork support | `check_formwork_support()` |
| 基坑支护、深基坑、土压力 | excavation support | `check_deep_excavation()` |
| 塔吊基础、塔吊验算 | tower crane foundation | `check_tower_crane_foundation()` |
| 临边防护、防护栏杆 | edge protection | `check_edge_protection()` |
| 临时用电、电缆选择 | temporary power | `check_temporary_power()` |

#### 意图-06: 碳排放与绿色建筑 (`carbon`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 碳排放、碳足迹、碳排量 | carbon emission | `calculate_building_carbon_emission()` |
| 装配率、装配式建筑 | assembly rate | `calculate_assembly_rate()` |
| 绿色建筑、绿建评价、绿建评分 | green building | `evaluate_green_building()` |
| 建筑能耗、能耗计算 | energy consumption | `calculate_building_energy()` |

#### 意图-07: 施工组织与进度 (`schedule`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 进度计划、施工进度 | schedule, construction plan | `build_cpm_network()` |
| 关键路径、CPM、网络计划 | critical path, cpm | `build_cpm_network()` |
| 横道图、甘特图 | gantt chart | `generate_gantt_chart()` |
| 资源曲线、资源计划 | resource curve | `calculate_resource_curve()` |
| 资源均衡、资源优化 | resource leveling | `optimize_resource_leveling()` |
| 标准工序、工序模板 | standard sequence | `get_standard_sequence()` |
| 进度跟踪、挣值法、EVM | progress tracking, evm | `track_schedule_progress()` |

#### 意图-08: Excel计算表生成 (`excel`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| Excel计算表、生成表格 | excel sheet, generate table | `generate_full_project_workbook()` |
| 混凝土计算表 | concrete sheet | `generate_concrete_quantity_sheet()` |
| 钢筋计算表 | rebar sheet | `generate_rebar_quantity_sheet()` |
| 清单汇总表 | quantity summary | `generate_quantity_summary_sheet()` |
| 造价汇总表 | cost summary | `generate_cost_summary_sheet()` |

#### 意图-09: 实用工具 (`utilities`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 坐标转换、WGS84、CGCS2000 | coordinate transform | `coordinate_transform()` |
| 高斯投影、经纬度转换 | gauss kruger | `gauss_kruger_to_lonlat()` |
| 单位换算、单位转换 | unit conversion | `convert_unit()` |
| 导出Excel、导出清单 | export excel | `export_quantity_to_excel()` |
| 批量处理、批量算量 | batch process | `batch_process_cad()` |

---

### 8.2 专业领域路由表

当用户提到特定专业时，路由到对应算量函数：

| 专业关键字 | 专业ID | 主函数 | 清单编码前缀 |
|-----------|--------|--------|:---:|
| 土建、建筑、房建、住宅、办公楼 | `civil` | `calculate_concrete_detail()` | 0101-0111 |
| 市政、管网、给排水、道路、路灯 | `municipal` | `calculate_municipal_full()` | 0401-0413 |
| 公路、高速、路基、路面、桥梁 | `highway` | `calculate_highway_full()` | JTG |
| 幕墙、玻璃幕墙、石材幕墙、铝板 | `curtain_wall` | `calculate_curtain_wall_full()` | 0110 |
| 钢结构、钢框架、钢桁架、网架 | `steel` | `calculate_steel_full()` | 0106 |
| 隧道、地下工程、衬砌、掘进 | `tunnel` | `calculate_tunnel_full()` | 0114 |

---

### 8.3 AI 调用规范

#### 规范-1: 调用流程

```
用户输入 → 关键字匹配(§8.1) → 专业路由(§8.2) → 函数选择(§14 API注册表) → 执行 → 格式化输出
```

#### 规范-2: 参数收集优先级

1. 用户消息中直接提供的参数值
2. 从图纸/CAD文件中解析的参数
3. 使用规范默认值（查04-standards.md）
4. 询问用户补充

#### 规范-3: 输出格式标准

| 输出类型 | 格式要求 |
|---------|---------|
| 工程量结果 | 表格（序号/编码/名称/单位/工程量/备注） |
| 安全验算结果 | 表格（验算项/计算值/限值/应力比/结论） |
| 造价计算结果 | 表格（费用项/计算基础/费率/金额） |
| BIM模型信息 | 列表（构件类型/数量/属性） |
| 进度计划结果 | 列表（工序/工期/ES/EF/LS/LF/TF/关键路径标注） |
| 碳排放结果 | 表格（阶段/排放量/占比） |

#### 规范-4: 错误处理

```python
# AI 调用函数时的标准错误处理模式
try:
    result = target_function(**params)
    if result.get('是否安全', '').startswith('✗'):
        # 验算不通过 → 提供改进建议
        suggestion = result.get('建议', '请检查输入参数')
    else:
        # 正常输出结果
        format_output(result)
except KeyError as e:
    # 缺少必要参数 → 询问用户
    ask_user(f"请提供参数: {e}")
except ValueError as e:
    # 参数值无效 → 提示正确范围
    ask_user(f"参数无效: {e}，请检查输入")
except Exception as e:
    # 其他错误 → 降级处理
    fallback_to_manual_calculation()
```

#### 规范-5: 组合调用模式

| 场景 | 调用链 |
|------|--------|
| CAD→算量→Excel | `parse_cad_drawing()` → `calculate_concrete_detail()` → `export_quantity_to_excel()` |
| CAD→算量→BIM→碰撞 | `parse_cad_drawing()` → `calculate_*()` → `create_bim_model_from_cad()` → `clash_detection()` |
| 算量→计价→报价书 | `calculate_*()` → `calculate_composite_unit_price()` → `generate_bid_document()` |
| 进度→资源→横道图 | `get_standard_sequence()` → `build_cpm_network()` → `calculate_resource_curve()` → `generate_gantt_chart()` |
| 算量→碳排放→绿建 | `calculate_*()` → `calculate_building_carbon_emission()` → `evaluate_green_building()` |
| 安全验算全套 | `check_scaffold_stability()` + `check_formwork_support()` + `check_deep_excavation()` + `check_tower_crane_foundation()` |

---

### 8.4 处理原则

1. **识图优先**: 先读取并解析图纸，确认图层、图块和构件信息
2. **算量准确**: 严格按照国家规范公式计算，标注计算依据（规范条目号）
3. **BIM规范**: 使用IFC4标准，确保模型可导入Revit、Tekla等主流软件
4. **专业区分**: 不同专业使用不同的算量规则和BIM构件类型
5. **碰撞必检**: BIM模型生成后务必进行碰撞检测
6. **输出清晰**: 工程量清单使用表格形式，BIM模型标注构件属性
7. **安全验算**: 所有施工安全计算必须给出明确结论（满足/不满足）和改进建议
8. **造价闭环**: 计价结果必须包含量→价→费→税完整链条
9. **规范引用**: 所有计算结果必须标注依据的规范编号和条文
10. **可追溯性**: 保留中间计算过程，方便审计复核

---

## 九、工程造价计价 (Pricing & Cost Estimation)

> 依据: GB 50500-2013《建设工程工程量清单计价规范》、建办标〔2020〕38号
> 体系: 量价分离 — 工程量由算量模块计算，本模块负责计价

---

### 9.1 费用组成体系

```
工程造价 = 分部分项工程费 + 措施项目费 + 其他项目费 + 规费 + 税金
         └─ 人工费 + 材料费 + 机械费 + 管理费 + 利润
```

| 费用类别 | 编码前缀 | 说明 |
|---------|---------|------|
| 分部分项工程费 | 0101~0117 | 按清单编码对应实体项目 |
| 措施项目费 | 01S | 安全文明施工、夜间施工、二次搬运等 |
| 其他项目费 | 01Q | 暂列金额、暂估价、计日工、总承包服务费 |
| 规费 | 01G | 社保、公积金、工程排污费 |
| 税金 | 01T | 增值税（一般计税9% / 简易计税3%） |

### 9.2 综合单价计算

```
综合单价 = 人工费 + 材料费 + 机械费 + 管理费 + 利润
         + 一般风险费（不含规费和税金）

人工费 = ∑(工日消耗量 × 人工单价)
材料费 = ∑(材料消耗量 × 材料单价)
机械费 = ∑(机械台班消耗量 × 台班单价)
管理费 = (人工费 + 机械费) × 管理费费率
利  润 = (人工费 + 机械费) × 利润率
```

```python
def calculate_composite_unit_price(
    labor_days: float, labor_rate: float,
    materials: list,  # [(name, consumption, unit_price), ...]
    machinery: list,  # [(name, shifts, shift_price), ...]
    mgmt_rate: float = 0.15,
    profit_rate: float = 0.08,
    risk_rate: float = 0.02,
) -> dict:
    """
    计算综合单价
    依据: GB 50500-2013 第3.0.5条
    """
    labor_cost = labor_days * labor_rate

    material_cost = sum(consumption * price for _, consumption, price in materials)

    machinery_cost = sum(shifts * price for _, shifts, price in machinery)

    base = labor_cost + machinery_cost
    management_cost = base * mgmt_rate
    profit = base * profit_rate
    risk = base * risk_rate

    unit_price = (labor_cost + material_cost + machinery_cost
                  + management_cost + profit + risk)

    return {
        'labor_cost': round(labor_cost, 2),
        'material_cost': round(material_cost, 2),
        'machinery_cost': round(machinery_cost, 2),
        'management_cost': round(management_cost, 2),
        'profit': round(profit, 2),
        'risk_cost': round(risk, 2),
        'composite_unit_price': round(unit_price, 2),
        'analysis': {
            '人工费占比': f'{labor_cost/unit_price*100:.1f}%',
            '材料费占比': f'{material_cost/unit_price*100:.1f}%',
            '机械费占比': f'{machinery_cost/unit_price*100:.1f}%',
        }
    }
```

### 9.3 人工工日单价参考表

| 工种 | 工日单价(元) | 工种 | 工日单价(元) |
|------|:---:|------|:---:|
| 综合工日 | 120~150 | 木工 | 150~200 |
| 钢筋工 | 150~220 | 混凝土工 | 130~180 |
| 砌筑工 | 140~190 | 抹灰工 | 130~180 |
| 架子工 | 160~230 | 电焊工 | 180~280 |
| 起重工 | 160~240 | 电工 | 160~250 |
| 管工 | 150~220 | 油漆工 | 130~180 |
| 防水工 | 140~200 | 信号工 | 130~170 |

> 注: 以上为2024~2026年市场参考价，实际以当地造价信息为准

### 9.4 常用材料单价参考表

| 材料名称 | 规格 | 单位 | 单价(元) |
|---------|------|------|:---:|
| 商品混凝土 | C30 | m³ | 420~480 |
| 商品混凝土 | C35 | m³ | 460~520 |
| 商品混凝土 | C40 | m³ | 500~560 |
| 商品混凝土 | C50 | m³ | 560~640 |
| 水泥 | P.O 42.5 | t | 380~450 |
| 砂 | 中砂 | m³ | 120~180 |
| 碎石 | 5-31.5mm | m³ | 130~190 |
| 热轧带肋钢筋 | HRB400 Φ12-25 | t | 3800~4200 |
| 热轧光圆钢筋 | HPB300 Φ6-10 | t | 4000~4400 |
| 钢绞线 | Φ15.2 | t | 5500~6500 |
| 木模板 | 周转 | m² | 35~50 |
| 钢模板 | 周转 | kg | 4.5~6.0 |
| 脚手架钢管 | Φ48×3.5 | t | 3800~4500 |
| 标准砖 | 240×115×53 | 千块 | 400~550 |
| 加气混凝土砌块 | B06 A5.0 | m³ | 220~300 |
| 防水卷材 | SBS 3mm | m² | 25~38 |
| 沥青混凝土 | AC-13C | t | 550~700 |
| 水泥稳定碎石 | 5% | m³ | 180~240 |

### 9.5 机械台班单价参考表

| 机械名称 | 规格 | 台班单价(元) |
|---------|------|:---:|
| 履带式挖掘机 | 1.0m³ | 1800~2200 |
| 履带式挖掘机 | 0.6m³ | 1200~1600 |
| 轮式装载机 | 3.0m³ | 1000~1400 |
| 自卸汽车 | 15t | 600~900 |
| 混凝土泵车 | 56m | 2500~3500 |
| 混凝土搅拌车 | 12m³ | 800~1200 |
| 塔式起重机 | TC6010 | 1200~1800 |
| 施工电梯 | SC200/200 | 600~900 |
| 履带式起重机 | 50t | 2000~3000 |
| 振动压路机 | 18t | 800~1200 |

### 9.6 措施项目费计算

```python
def calculate_measure_cost(
    project_cost: float,
    project_type: str = 'building',
    area: float = 0,
) -> dict:
    """
    计算措施项目费
    依据: GB 50500-2013 第3.0.6条
    """
    # 安全文明施工费费率（按总造价百分比）
    safety_rates = {
        'building': 0.030,      # 房建 3.0%
        'municipal': 0.025,     # 市政 2.5%
        'highway': 0.020,       # 公路 2.0%
    }
    safety_rate = safety_rates.get(project_type, 0.025)

    safety_cost = project_cost * safety_rate  # 安全文明施工费

    # 夜间施工增加费
    night_cost = project_cost * 0.005 if project_type == 'building' else 0

    # 二次搬运费
    transport_cost = project_cost * 0.008

    # 冬雨季施工增加费
    seasonal_cost = project_cost * 0.010

    # 大型机械设备进出场及安拆费（按实际计列）
    equipment_mobilization = 0  # 按实际报价

    # 脚手架费（按建筑面积估算）
    scaffold_cost = area * 35 if area > 0 else project_cost * 0.015

    # 模板费（按混凝土量估算，一般在混凝土造价的15-25%）
    formwork_cost = project_cost * 0.020

    total = (safety_cost + night_cost + transport_cost +
             seasonal_cost + equipment_mobilization +
             scaffold_cost + formwork_cost)

    return {
        '安全文明施工费': round(safety_cost, 2),
        '夜间施工增加费': round(night_cost, 2),
        '二次搬运费': round(transport_cost, 2),
        '冬雨季施工增加费': round(seasonal_cost, 2),
        '大型机械进出场费': round(equipment_mobilization, 2),
        '脚手架费': round(scaffold_cost, 2),
        '模板费': round(formwork_cost, 2),
        '措施费合计': round(total, 2),
    }
```

### 9.7 规费与税金计算

```python
def calculate_regulation_and_tax(
    sub_project_cost: float,  # 分部分项工程费
    measure_cost: float,      # 措施项目费
    other_cost: float = 0,    # 其他项目费
    tax_method: str = 'general',  # 'general'(一般计税9%) / 'simple'(简易计税3%)
) -> dict:
    """
    计算规费和税金
    依据: GB 50500-2013 第3.0.7条、财税〔2018〕32号
    """
    base = sub_project_cost + measure_cost + other_cost

    # 规费费率
    regulation_rates = {
        '社保费': 0.032,       # 养老+医疗+失业+工伤+生育
        '住房公积金': 0.010,
        '工程排污费': 0.001,
    }

    regulation_cost = sum(base * rate for rate in regulation_rates.values())

    # 税前造价
    pre_tax = base + regulation_cost

    # 增值税率
    tax_rate = 0.09 if tax_method == 'general' else 0.03
    tax = pre_tax * tax_rate

    # 总造价
    total = pre_tax + tax

    return {
        '规费': {
            '社保费': round(base * regulation_rates['社保费'], 2),
            '住房公积金': round(base * regulation_rates['住房公积金'], 2),
            '工程排污费': round(base * regulation_rates['工程排污费'], 2),
            '规费合计': round(regulation_cost, 2),
        },
        '税金': {
            '计税方法': '一般计税' if tax_method == 'general' else '简易计税',
            '税率': f'{tax_rate*100:.0f}%',
            '税前造价': round(pre_tax, 2),
            '税金': round(tax, 2),
        },
        '工程总造价': round(total, 2),
    }
```

### 9.8 工程报价书生成

```python
def generate_bid_document(
    quantities: list,  # [(code, name, unit, qty, unit_price), ...]
    project_info: dict,
    output_path: str,
) -> str:
    """
    生成完整工程报价书（Excel）
    包含: 封面、分部分项清单、措施项目清单、规费税金汇总
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

    wb = Workbook()

    # === 封面 ===
    ws_cover = wb.active
    ws_cover.title = "封面"
    ws_cover['A1'] = "工程报价书"
    ws_cover['A1'].font = Font(name='宋体', size=24, bold=True)
    ws_cover.merge_cells('A1:F1')
    ws_cover['A3'] = f"工程名称: {project_info.get('name', '')}"
    ws_cover['A4'] = f"建设单位: {project_info.get('client', '')}"
    ws_cover['A5'] = f"施工单位: {project_info.get('contractor', '')}"
    ws_cover['A6'] = f"报价日期: {project_info.get('date', '')}"

    # === 分部分项工程量清单 ===
    ws_bq = wb.create_sheet("分部分项工程量清单")
    headers = ['序号', '清单编码', '项目名称', '项目特征', '计量单位',
               '工程量', '综合单价(元)', '合价(元)', '其中人工费', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws_bq.cell(row=1, column=col, value=h)
        cell.font = Font(name='宋体', bold=True, size=10)
        cell.fill = PatternFill('solid', start_color='4472C4')
        cell.font = Font(name='宋体', bold=True, size=10, color='FFFFFF')
        cell.alignment = Alignment(horizontal='center')

    total_cost = 0
    for idx, (code, name, unit, qty, price) in enumerate(quantities, 1):
        subtotal = qty * price
        total_cost += subtotal
        row = idx + 1
        ws_bq.cell(row=row, column=1, value=idx)
        ws_bq.cell(row=row, column=2, value=code)
        ws_bq.cell(row=row, column=3, value=name)
        ws_bq.cell(row=row, column=6, value=unit)
        ws_bq.cell(row=row, column=7, value=qty)
        ws_bq.cell(row=row, column=8, value=price)
        ws_bq.cell(row=row, column=9, value=round(subtotal, 2))

    # 合计行
    sum_row = len(quantities) + 2
    ws_bq.cell(row=sum_row, column=3, value="合计").font = Font(bold=True)
    ws_bq.cell(row=sum_row, column=9, value=round(total_cost, 2)).font = Font(bold=True)

    # === 费用汇总表 ===
    ws_summary = wb.create_sheet("费用汇总表")
    measures = calculate_measure_cost(total_cost, project_info.get('type', 'building'),
                                       project_info.get('area', 0))
    reg_tax = calculate_regulation_and_tax(total_cost, measures['措施费合计'])

    summary_data = [
        ['1', '分部分项工程费', round(total_cost, 2)],
        ['2', '措施项目费', measures['措施费合计']],
        ['3', '其他项目费', 0],
        ['4', '规费', reg_tax['规费']['规费合计']],
        ['5', '税金', reg_tax['税金']['税金']],
        ['', '工程总造价', reg_tax['工程总造价']],
    ]
    for row_idx, (no, name, amount) in enumerate(summary_data, 1):
        ws_summary.cell(row=row_idx, column=1, value=no)
        ws_summary.cell(row=row_idx, column=2, value=name)
        ws_summary.cell(row=row_idx, column=3, value=amount)

    wb.save(output_path)
    return output_path
```

### 9.9 材料价差调整

```python
def calculate_material_price_adjustment(
    contract_prices: dict,  # {材料名: 合同单价}
    current_prices: dict,   # {材料名: 当前市场单价}
    quantities: dict,       # {材料名: 消耗量}
    adjustment_threshold: float = 0.05,  # ±5%以内不调整
) -> dict:
    """
    材料价差调整
    依据: 施工合同约定及工程造价信息
    """
    adjustments = []
    total_diff = 0

    for material, contract_price in contract_prices.items():
        current_price = current_prices.get(material, contract_price)
        qty = quantities.get(material, 0)
        diff_pct = (current_price - contract_price) / contract_price

        if abs(diff_pct) > adjustment_threshold:
            diff_amount = (current_price - contract_price) * qty
            adjustments.append({
                '材料名称': material,
                '合同单价': contract_price,
                '现行单价': current_price,
                '价差率': f'{diff_pct*100:.1f}%',
                '消耗量': qty,
                '价差金额': round(diff_amount, 2),
            })
            total_diff += diff_amount

    return {
        '调整明细': adjustments,
        '价差合计': round(total_diff, 2),
        '调整材料数': len(adjustments),
    }
```

---

## 十、施工安全计算 (Construction Safety Calculation)

> 依据: JGJ 130-2011《建筑施工扣件式钢管脚手架安全技术规范》、JGJ 162-2014《建筑施工模板安全技术规范》、JGJ 120-2012《建筑基坑支护技术规程》、JGJ 215-2010《建筑施工升降机安装、使用、拆卸安全技术规程》

---

### 10.1 脚手架计算

#### 10.1.1 落地式钢管脚手架承载力

```
立杆稳定性验算: N/φA ≤ f

式中:
  N  — 立杆轴向力设计值 (kN)
  φ  — 轴心受压构件稳定系数（查长细比λ）
  A  — 立杆截面面积 (cm²), Φ48×3.5钢管 A=4.89cm²
  f  — 钢材抗压强度设计值, Q235 f=205 N/mm²

立杆轴向力:
  N = 1.2×(NG1k + NG2k) + 1.4×ΣNQk

  NG1k — 脚手架结构自重 (kN)
  NG2k — 构配件自重 (kN)
  NQk  — 施工荷载 (kN)

长细比: λ = l₀/i
  l₀ = k×μ×h  (计算长度)
  i  = 15.78mm (截面回转半径, Φ48×3.5)
  k  = 1.155 (长度附加系数)
  μ  = 1.50~1.80 (立杆计算长度系数, 按连墙件布置查表)
```

```python
def check_scaffold_stability(
    height: float,         # 脚手架高度(m)
    step: float = 1.8,     # 步距(m)
    span: float = 1.5,     # 立杆纵距(m)
    layers: int = 2,       # 同时施工层数
    load_per_layer: float = 3.0,  # 每层施工荷载(kN/m²)
    wall_type: str = 'two',  # 'two'=两步三跨, 'three'=三步三跨
) -> dict:
    """
    落地式扣件钢管脚手架立杆稳定性验算
    依据: JGJ 130-2011 第5.1.5~5.1.9条
    """
    # 钢管参数 Φ48×3.5
    A = 489.0        # 截面面积 mm²
    i = 15.78        # 回转半径 mm
    f = 205.0        # Q235强度设计值 N/mm²
    E = 2.06e5       # 弹性模量 N/mm²

    # 计算长度系数
    mu = 1.50 if wall_type == 'two' else 1.70
    k = 1.155
    l0 = k * mu * step * 1000  # mm

    # 长细比及稳定系数
    lamda = l0 / i
    # φ值查表近似公式 (JGJ 130 附录C)
    if lamda <= 135:
        phi = (1 + 0.001 * lamda**2) ** -1 * (1 - 0.001 * lamda**2) / (
            (1 + 0.001 * lamda**2) ** 2 + 0.0001 * lamda**2)
        # 简化: 使用查表近似
        phi_table = {60: 0.842, 70: 0.809, 80: 0.771, 90: 0.730,
                     100: 0.688, 110: 0.645, 120: 0.604, 130: 0.565, 135: 0.546}
        # 线性插值
        keys = sorted(phi_table.keys())
        for j in range(len(keys)-1):
            if keys[j] <= lamda <= keys[j+1]:
                t = (lamda - keys[j]) / (keys[j+1] - keys[j])
                phi = phi_table[keys[j]] * (1-t) + phi_table[keys[j+1]] * t
                break
        else:
            phi = 0.546
    else:
        phi = 7240 / lamda**2  # b类截面

    # 荷载计算
    # 1. 结构自重: 钢管+扣件, 约0.1337 kN/m(纵距1.5m, 步距1.8m)
    gk1 = 0.1337 * height / step  # 每根立杆结构自重 kN
    # 2. 构配件自重: 脚手板+挡脚板+安全网
    gk2 = (0.35 * span * step * (height / step / 2)  # 脚手板(隔步铺设)
           + 0.14 * span * (height / step)            # 挡脚板
           + 0.01 * span * height)                    # 安全网
    # 3. 施工荷载
    nqk = load_per_layer * span * step * layers  # kN

    # 立杆轴向力设计值
    NGk = gk1 + gk2
    N = 1.2 * NGk + 1.4 * nqk  # kN

    # 稳定性验算
    sigma = N * 1000 / (phi * A)  # N/mm²
    safe = sigma <= f
    ratio = sigma / f

    return {
        '长细比λ': round(lamda, 1),
        '稳定系数φ': round(phi, 4),
        '计算长度l0': f'{l0:.0f} mm',
        '结构自重NG1k': f'{gk1:.2f} kN',
        '构配件自重NG2k': f'{gk2:.2f} kN',
        '施工荷载NQk': f'{nqk:.2f} kN',
        '立杆轴向力N': f'{N:.2f} kN',
        '截面应力σ': f'{sigma:.1f} N/mm²',
        '强度设计值f': f'{f} N/mm²',
        '应力比σ/f': f'{ratio:.3f}',
        '是否安全': '✓ 满足' if safe else '✗ 不满足，需调整',
        '建议': '' if safe else '减小步距/纵距/施工层数，或增设抛撑',
    }
```

#### 10.1.2 脚手架连墙件计算

```python
def check_wall_connector(
    wind_pressure: float,   # 风压标准值 kN/m²
    span: float = 1.5,      # 立杆纵距 m
    vertical_step: float = 3.6,  # 连墙件竖向间距 m(两步)
    horizontal_step: float = 4.5,  # 连墙件水平间距 m(三跨)
) -> dict:
    """
    连墙件抗风验算
    依据: JGJ 130-2011 第5.1.12条
    """
    # 连墙件轴向力设计值
    Nl = 1.4 * wind_pressure * vertical_step * horizontal_step + 3.0  # kN, +3.0为自重

    # 扣件抗滑承载力
    Rc = 8.0  # 单扣件 8kN, 双扣件 12kN

    safe = Nl <= Rc
    return {
        '风荷载标准值': f'{wind_pressure} kN/m²',
        '连墙件轴向力Nl': f'{Nl:.2f} kN',
        '扣件抗滑力Rc': f'{Rc} kN',
        '是否安全': '✓ 满足' if safe else '✗ 不满足，需用双扣件',
        '建议': '' if safe else '采用双扣件连接(Rc=12kN)',
    }
```

### 10.2 模板支撑体系计算

```python
def check_formwork_support(
    slab_thickness: float,    # 板厚 mm
    concrete_unit_weight: float = 25.0,  # 钢筋混凝土容重 kN/m³
    span: float = 1.2,        # 立杆纵距 m
    step: float = 1.2,        # 步距 m
    construction_load: float = 2.5,  # 施工荷载 kN/m²
    wall_type: str = 'two',   # 连墙件类型
) -> dict:
    """
    模板支撑架立杆稳定性验算
    依据: JGJ 162-2014 第6.2.4条、JGJ 130-2011
    """
    # 钢管参数
    A = 489.0  # mm²
    i = 15.78  # mm
    f = 205.0  # N/mm²

    # 荷载计算
    # 1. 模板及支撑架自重: 约0.75 kN/m²
    g1 = 0.75
    # 2. 新浇混凝土自重
    g2 = slab_thickness / 1000 * concrete_unit_weight  # kN/m²
    # 3. 钢筋自重: 约1.1 kN/m³ × 板厚
    g3 = 1.1 * slab_thickness / 1000
    # 4. 施工人员及设备荷载
    q1 = construction_load

    # 立杆轴向力
    N_k = (g1 + g2 + g3 + q1) * span * span  # 标准值 kN
    N = 1.2 * (g1 + g2 + g3) * span * span + 1.4 * q1 * span * span  # 设计值 kN

    # 稳定系数
    mu = 1.50 if wall_type == 'two' else 1.70
    k = 1.155
    l0 = k * mu * step * 1000  # mm
    lamda = l0 / i

    # φ值近似
    if lamda <= 120:
        phi_approx = max(0.6 - (lamda - 100) * 0.004, 0.45)
    else:
        phi_approx = max(0.45 - (lamda - 120) * 0.003, 0.30)

    sigma = N * 1000 / (phi_approx * A)
    safe = sigma <= f

    return {
        '板厚': f'{slab_thickness} mm',
        '混凝土自重': f'{g2:.2f} kN/m²',
        '总恒载': f'{g1+g2+g3:.2f} kN/m²',
        '施工荷载': f'{q1} kN/m²',
        '立杆轴向力(标准值)': f'{N_k:.2f} kN',
        '立杆轴向力(设计值)': f'{N:.2f} kN',
        '长细比λ': round(lamda, 1),
        '稳定系数φ': round(phi_approx, 4),
        '截面应力σ': f'{sigma:.1f} N/mm²',
        '应力比σ/f': f'{sigma/f:.3f}',
        '是否安全': '✓ 满足' if safe else '✗ 不满足',
        '建议': '' if safe else '减小立杆间距或步距，增加剪刀撑',
    }
```

### 10.3 深基坑支护计算

```python
def check_deep_excavation(
    excavation_depth: float,  # 开挖深度 m
    soil_gamma: float = 18.0,  # 土体重度 kN/m³
    soil_phi: float = 20.0,    # 内摩擦角 °
    soil_c: float = 15.0,      # 内聚力 kPa
    surcharge: float = 20.0,   # 地面超载 kPa
    water_table: float = None,  # 地下水位深度 m
) -> dict:
    """
    深基坑支护初步计算
    依据: JGJ 120-2012《建筑基坑支护技术规程》
    包含: 主动土压力、被动土压力、嵌固深度验算
    """
    import math

    # 主动土压力系数 (Rankine)
    Ka = math.tan(math.radians(45 - soil_phi/2))**2
    # 被动土压力系数
    Kp = math.tan(math.radians(45 + soil_phi/2))**2

    # 主动土压力 (坑底处)
    pa_bottom = soil_gamma * excavation_depth * Ka - 2 * soil_c * math.sqrt(Ka)
    pa_bottom = max(pa_bottom, 0)  # 不出现负值

    # 考虑地面超载
    pa_surcharge = surcharge * Ka

    # 总主动土压力(三角形分布)
    Pa = 0.5 * soil_gamma * excavation_depth**2 * Ka \
         - 2 * soil_c * math.sqrt(Ka) * excavation_depth \
         + surcharge * Ka * excavation_depth
    Pa = max(Pa, 0)

    # 嵌固深度计算（悬臂式支护）
    # 经验值: 嵌固深度 = 0.3~1.2 × 开挖深度
    # 简化计算: 力矩平衡法
    embed_ratio = 0.8  # 初始估计
    for _ in range(20):
        d = excavation_depth * embed_ratio
        # 被动土压力
        Pp = 0.5 * soil_gamma * d**2 * Kp + 2 * soil_c * math.sqrt(Kp) * d
        # 力矩平衡(简化): Pa×(H/3) ≤ Pp×(d/3)
        moment_active = Pa * (excavation_depth / 3)
        moment_passive = Pp * (d / 3)
        if moment_passive >= 1.2 * moment_active:  # 安全系数1.2
            break
        embed_ratio += 0.05

    embed_depth = excavation_depth * embed_ratio
    total_length = excavation_depth + embed_depth

    # 判定基坑等级
    if excavation_depth >= 12:
        grade = '一级'
    elif excavation_depth >= 7:
        grade = '二级'
    else:
        grade = '三级'

    return {
        '基坑等级': grade,
        '开挖深度': f'{excavation_depth} m',
        '主动土压力系数Ka': round(Ka, 4),
        '被动土压力系数Kp': round(Kp, 4),
        '坑底主动土压力': f'{pa_bottom:.1f} kPa',
        '超载侧压力': f'{pa_surcharge:.1f} kPa',
        '总主动土压力Pa': f'{Pa:.1f} kN/m',
        '最小嵌固深度': f'{embed_depth:.1f} m',
        '桩/墙总长度': f'{total_length:.1f} m',
        '嵌固比d/H': f'{embed_ratio:.2f}',
        '安全系数': '1.2 (力矩平衡)',
        '建议支护形式': _recommend_support(excavation_depth, grade),
    }

def _recommend_support(depth: float, grade: str) -> str:
    """根据深度和等级推荐支护形式"""
    if depth <= 3:
        return '放坡开挖 / 土钉墙'
    elif depth <= 6:
        return '土钉墙 / 水泥土桩'
    elif depth <= 10:
        return '排桩+内支撑 / 地下连续墙'
    elif depth <= 15:
        return '地下连续墙+混凝土内支撑 / 排桩+锚索'
    else:
        return '地下连续墙+多道混凝土内支撑 / SMW工法'
```

### 10.4 塔吊基础计算

```python
def check_tower_crane_foundation(
    crane_model: str,           # 塔吊型号
    tipping_moment: float,      # 倾覆力矩 kN·m
    vertical_load: float,       # 垂直力 kN
    base_size: float = 5.0,     # 基础边长 m
    base_height: float = 1.2,   # 基础高度 m
    soil_bearing: float = 180,  # 地基承载力特征值 kPa
) -> dict:
    """
    塔吊板式基础验算
    依据: JGJ/T 30122-2014《塔式起重机混凝土基础工程技术规程》
    """
    import math

    # 基础自重
    concrete_gamma = 25.0  # kN/m³
    base_weight = base_size * base_size * base_height * concrete_gamma

    # 总垂直力
    N = vertical_load + base_weight

    # 偏心距
    e = tipping_moment / N

    # 基础底面抵抗矩
    W = base_size * base_size**2 / 6

    # 基底应力（梯形或三角形分布）
    p_max = N / (base_size * base_size) + tipping_moment / W
    p_min = N / (base_size * base_size) - tipping_moment / W

    # 地基承载力验算
    # 修正后地基承载力 (深宽修正)
    f_a = soil_bearing + 1.0 * 18 * (base_height - 0.5)  # 简化修正

    safe_bearing = p_max <= 1.2 * f_a
    safe_eccentricity = e <= base_size / 6  # 不脱离

    # 抗倾覆验算
    overturn_resist = base_weight * base_size / 2
    overturn_factor = overturn_resist / tipping_moment
    safe_overturn = overturn_factor >= 1.5

    return {
        '塔吊型号': crane_model,
        '倾覆力矩': f'{tipping_moment} kN·m',
        '垂直力': f'{vertical_load} kN',
        '基础尺寸': f'{base_size}×{base_size}×{base_height} m',
        '基础自重': f'{base_weight:.1f} kN',
        '总垂直力': f'{N:.1f} kN',
        '偏心距e': f'{e:.3f} m',
        '基底最大应力pmax': f'{p_max:.1f} kPa',
        '基底最小应力pmin': f'{p_min:.1f} kPa',
        '修正地基承载力fa': f'{f_a:.0f} kPa',
        '抗倾覆安全系数': f'{overturn_factor:.2f}',
        '地基承载力验算': '✓ 满足' if safe_bearing else '✗ 不满足',
        '偏心距验算': '✓ 满足' if safe_eccentricity else '✗ 不满足(有拉应力)',
        '抗倾覆验算': '✓ 满足' if safe_overturn else '✗ 不满足',
        '综合判断': '✓ 安全' if all([safe_bearing, safe_eccentricity, safe_overturn]) else '✗ 需修改',
    }
```

### 10.5 高处作业临边洞口防护计算

```python
def check_edge_protection(
    floor_height: float,        # 楼层高度 m
    slab_thickness: float,      # 板厚 mm
    wind_pressure: float = 0.5, # 基本风压 kN/m²
) -> dict:
    """
    临边防护栏杆计算
    依据: JGJ 80-2016《建筑施工高处作业安全技术规范》
    """
    # 防护栏杆荷载
    # 水平荷载: 1kN/m (防护栏杆顶部)
    horizontal_load = 1.0  # kN/m

    # 钢管参数 Φ48×3.5
    A = 489.0  # mm²
    W = 5.08e3  # 截面抵抗矩 mm³
    f = 205.0  # N/mm²

    # 立杆间距2m，栏杆高1.2m
    post_spacing = 2.0  # m
    rail_height = 1.2   # m

    # 立杆弯矩
    M = horizontal_load * post_spacing * rail_height * 1000  # N·m

    # 立杆应力
    sigma = M * 1000 / W  # N/mm²

    # 风荷载影响
    wind_force = wind_pressure * post_spacing * rail_height  # kN
    wind_moment = wind_force * rail_height / 2 * 1000  # N·m
    sigma_wind = wind_moment * 1000 / W

    total_sigma = sigma + sigma_wind
    safe = total_sigma <= f

    return {
        '楼层高度': f'{floor_height} m',
        '栏杆高度': f'{rail_height} m',
        '立杆间距': f'{post_spacing} m',
        '水平荷载': f'{horizontal_load} kN/m',
        '风荷载': f'{wind_force:.2f} kN',
        '立杆弯矩': f'{M:.1f} N·m',
        '截面应力σ': f'{total_sigma:.1f} N/mm²',
        '应力比': f'{total_sigma/f:.3f}',
        '是否安全': '✓ 满足' if safe else '✗ 不满足，减小立杆间距',
    }
```

### 10.6 临时用电安全计算

```python
def check_temporary_power(
    total_power: float,       # 总用电功率 kW
    voltage: int = 380,       # 电压 V
    power_factor: float = 0.8, # 功率因数
    cable_length: float = 100, # 电缆长度 m
    conductor: str = 'copper', # 'copper'/'aluminum'
) -> dict:
    """
    施工现场临时用电计算
    依据: JGJ 46-2024《施工现场临时用电安全技术规范》
    """
    # 计算电流
    import math
    I = total_power * 1000 / (math.sqrt(3) * voltage * power_factor)

    # 铜电缆经济电流密度 (A/mm²)
    j_economical = 4.0 if conductor == 'copper' else 2.5

    # 计算截面
    cross_section = I / j_economical

    # 标准截面选型
    standard_sections = [2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
    selected_section = next((s for s in standard_sections if s >= cross_section), 240)

    # 电压降验算 (ΔU% ≤ 5%)
    # ΔU% = (P×L) / (C×S)
    C = 77 if conductor == 'copper' else 46.3  # 铜C=77, 铝C=46.3
    delta_u = (total_power * cable_length) / (C * selected_section)
    safe_voltage = delta_u <= 5.0

    # 需要系数法计算变压器容量
    Kx = 0.7  # 需要系数
    S_transformer = Kx * total_power / power_factor

    return {
        '总功率': f'{total_power} kW',
        '计算电流': f'{I:.1f} A',
        '经济截面': f'{cross_section:.1f} mm²',
        '选择截面': f'{selected_section} mm²',
        '电压降': f'{delta_u:.2f}%',
        '电压降限值': '5%',
        '变压器容量': f'{S_transformer:.1f} kVA',
        '建议变压器': f'{math.ceil(S_transformer/50)*50} kVA',
        '电压降验算': '✓ 满足' if safe_voltage else '✗ 不满足，增大截面',
    }
```

---

## 十一、碳排放与绿色建筑 (Carbon Emission & Green Building)

> 依据: GB/T 51366-2019《建筑碳排放计算标准》、GB/T 50378-2019《绿色建筑评价标准》、GB/T 51231-2016《装配式混凝土建筑技术标准》

---

### 11.1 建筑碳排放计算

#### 11.1.1 碳排放阶段划分

```
建筑全寿命期碳排放 = 建材生产碳排放 + 运输碳排放 + 建造碳排放
                    + 运行碳排放 + 拆除碳排放

CE = CE_prod + CE_trans + CE_cons + CE_oper + CE_demo
```

| 阶段 | 计算边界 | 占比(典型) |
|------|---------|:---:|
| 建材生产 | 原料开采→产品出厂 | 50~70% |
| 运输 | 工厂→施工现场 | 2~5% |
| 建造施工 | 施工过程能源消耗 | 3~8% |
| 运行使用 | 采暖/空调/照明/电梯/给排水 | 15~35% |
| 拆除处置 | 拆除+废弃物处理 | 1~3% |

#### 11.1.2 建材碳排放因子表

| 材料名称 | 单位 | 碳排放因子(kgCO₂e) | 数据来源 |
|---------|------|:---:|---------|
| 硅酸盐水泥(P.O 42.5) | t | 735 | GB/T 51366 附录A |
| 矿渣水泥(P.S 32.5) | t | 590 | GB/T 51366 附录A |
| 商品混凝土 C30 | m³ | 295 | 地方碳排放因子 |
| 商品混凝土 C40 | m³ | 340 | 地方碳排放因子 |
| 商品混凝土 C50 | m³ | 380 | 地方碳排放因子 |
| 热轧带肋钢筋 | t | 2120 | GB/T 51366 附录A |
| 热轧型钢 | t | 1980 | GB/T 51366 附录A |
| 钢板 | t | 2350 | GB/T 51366 附录A |
| 铝合金型材 | t | 11200 | GB/T 51366 附录A |
| 平板玻璃(5mm) | m² | 14.6 | GB/T 51366 附录A |
| 中空玻璃 | m² | 25.5 | 行业数据 |
| 烧结普通砖 | 千块 | 198 | GB/T 51366 附录A |
| 加气混凝土砌块 | m³ | 79 | GB/T 51366 附录A |
| SBS防水卷材 | m² | 4.2 | 行业数据 |
| 聚苯板(EPS) | m³ | 165 | 行业数据 |
| 挤塑板(XPS) | m³ | 195 | 行业数据 |
| 木材(原木) | m³ | 12.2 | GB/T 51366 附录A |
| 碎石 | t | 3.5 | 行业数据 |
| 中砂 | t | 2.8 | 行业数据 |
| 沥青混凝土 | t | 65 | 行业数据 |
| 陶瓷墙地砖 | m² | 7.8 | GB/T 51366 附录A |

#### 11.1.3 运输碳排放因子

| 运输方式 | 碳排放因子(kgCO₂e/t·km) | 适用场景 |
|---------|:---:|---------|
| 公路运输(柴油重卡) | 0.052 | 短途(<200km) |
| 公路运输(天然气) | 0.045 | 短途(<200km) |
| 铁路运输 | 0.010 | 中长途 |
| 水路运输 | 0.006 | 长途沿江沿海 |

#### 11.1.4 施工能源碳排放因子

| 能源类型 | 单位 | 碳排放因子(kgCO₂e) |
|---------|------|:---:|
| 电力(华东电网) | kWh | 0.7035 |
| 电力(华北电网) | kWh | 0.8843 |
| 电力(全国平均) | kWh | 0.5810 |
| 柴油 | kg | 3.0959 |
| 汽油 | kg | 2.9251 |
| 天然气 | m³ | 2.1622 |
| 液化石油气 | kg | 3.1013 |

```python
def calculate_building_carbon_emission(
    materials: dict,      # {材料名: 消耗量}
    transport_distance: float = 50,  # 平均运输距离 km
    transport_mode: str = 'truck_diesel',
    electricity_kwh: float = 0,  # 施工用电 kWh
    diesel_kg: float = 0,        # 施工柴油 kg
    project_type: str = 'building',
    grid_region: str = 'national',
) -> dict:
    """
    建筑施工阶段碳排放计算
    依据: GB/T 51366-2019《建筑碳排放计算标准》
    """
    # 建材碳排放因子数据库
    material_factors = {
        '水泥_P.O42.5': 735, '水泥_P.S32.5': 590,
        '混凝土_C25': 265, '混凝土_C30': 295, '混凝土_C35': 320,
        '混凝土_C40': 340, '混凝土_C45': 360, '混凝土_C50': 380,
        '钢筋_HRB400': 2120, '钢筋_HPB300': 2120,
        '型钢': 1980, '钢板': 2350, '铝合金': 11200,
        '平板玻璃': 14.6, '中空玻璃': 25.5,
        '普通砖': 0.198, '加气块': 79,
        'SBS卷材': 4.2, 'EPS板': 165, 'XPS板': 195,
        '木材': 12.2, '碎石': 3.5, '砂': 2.8,
        '沥青混凝土': 65, '瓷砖': 7.8,
    }

    # 运输因子
    transport_factors = {
        'truck_diesel': 0.052, 'truck_gas': 0.045,
        'railway': 0.010, 'waterway': 0.006,
    }
    tf = transport_factors.get(transport_mode, 0.052)

    # 电力因子
    grid_factors = {
        'national': 0.5810, 'east': 0.7035, 'north': 0.8843,
        'south': 0.5271, 'central': 0.5737, 'northeast': 0.6214,
        'northwest': 0.6016,
    }
    ef = grid_factors.get(grid_region, 0.5810)

    # 1. 建材生产碳排放
    ce_prod = 0
    material_detail = []
    for mat, qty in materials.items():
        factor = material_factors.get(mat, 0)
        carbon = qty * factor
        ce_prod += carbon
        material_detail.append({
            '材料': mat,
            '消耗量': qty,
            '因子': factor,
            '碳排放(kgCO₂e)': round(carbon, 1),
        })

    # 2. 运输碳排放
    total_weight = sum(materials.get(k, 0) for k in materials)
    # 估算材料总重量(简化: 按主要材料重量)
    weight_estimate = 0
    weight_map = {'水泥_P.O42.5': 1, '水泥_P.S32.5': 1, '混凝土_C30': 2.4,
                  '钢筋_HRB400': 7.85, '普通砖': 1.7, '加气块': 0.6}
    for mat, qty in materials.items():
        density = weight_map.get(mat, 1.0)
        weight_estimate += qty * density

    ce_trans = weight_estimate * transport_distance * tf

    # 3. 施工碳排放
    ce_cons_elec = electricity_kwh * ef
    ce_cons_diesel = diesel_kg * 3.0959
    ce_cons = ce_cons_elec + ce_cons_diesel

    # 合计
    ce_total = ce_prod + ce_trans + ce_cons

    return {
        '建材生产碳排放': {
            '碳排放(kgCO₂e)': round(ce_prod, 1),
            '碳排放(tCO₂e)': round(ce_prod / 1000, 2),
            '占比': f'{ce_prod/ce_total*100:.1f}%',
            '明细': material_detail[:10],  # 前十项
        },
        '运输碳排放': {
            '碳排放(kgCO₂e)': round(ce_trans, 1),
            '碳排放(tCO₂e)': round(ce_trans / 1000, 2),
            '占比': f'{ce_trans/ce_total*100:.1f}%',
            '运输距离': f'{transport_distance} km',
        },
        '施工碳排放': {
            '碳排放(kgCO₂e)': round(ce_cons, 1),
            '碳排放(tCO₂e)': round(ce_cons / 1000, 2),
            '占比': f'{ce_cons/ce_total*100:.1f}%',
            '用电碳排放': round(ce_cons_elec, 1),
            '柴油碳排放': round(ce_cons_diesel, 1),
        },
        '施工阶段碳排放合计': {
            'kgCO₂e': round(ce_total, 1),
            'tCO₂e': round(ce_total / 1000, 2),
        },
    }
```

### 11.2 装配式建筑装配率计算

```python
def calculate_assembly_rate(
    prefabricated_elements: dict,  # 预制构件信息
    total_elements: dict,          # 全部构件信息
    project_area: float = 0,       # 建筑面积 m²
) -> dict:
    """
    装配率计算
    依据: GB/T 51231-2016、各省装配式建筑评价标准
    装配率 = 预制构件体积 / 全部构件体积 × 100% (承重构件)
    或: 装配率 = Q/(100-Qw) × 100% (综合评价法)
    """
    # 承重构件装配率
    pre_columns = prefabricated_elements.get('columns', 0)
    total_columns = total_elements.get('columns', 1)
    pre_beams = prefabricated_elements.get('beams', 0)
    total_beams = total_elements.get('beams', 1)
    pre_walls = prefabricated_elements.get('walls', 0)
    total_walls = total_elements.get('walls', 1)
    pre_slabs = prefabricated_elements.get('slabs', 0)
    total_slabs = total_elements.get('slabs', 1)

    # 各构件装配率
    rate_columns = pre_columns / total_columns if total_columns > 0 else 0
    rate_beams = pre_beams / total_beams if total_beams > 0 else 0
    rate_walls = pre_walls / total_walls if total_walls > 0 else 0
    rate_slabs = pre_slabs / total_slabs if total_slabs > 0 else 0

    # 综合装配率 (权重法)
    # 柱20% + 梁20% + 墙30% + 板20% + 非承重墙10%
    weights = {'columns': 0.20, 'beams': 0.20, 'walls': 0.30, 'slabs': 0.20}
    assembly_rate = (rate_columns * weights['columns'] +
                     rate_beams * weights['beams'] +
                     rate_walls * weights['walls'] +
                     rate_slabs * weights['slabs']) * 100

    # 装配率分级
    if assembly_rate >= 76:
        grade = 'AAA级 (装配率≥76%)'
    elif assembly_rate >= 66:
        grade = 'AA级 (装配率≥66%)'
    elif assembly_rate >= 50:
        grade = 'A级 (装配率≥50%)'
    elif assembly_rate >= 30:
        grade = 'B级 (装配率≥30%)'
    else:
        grade = '不达标 (装配率<30%)'

    return {
        '柱装配率': f'{rate_columns*100:.1f}%',
        '梁装配率': f'{rate_beams*100:.1f}%',
        '墙装配率': f'{rate_walls*100:.1f}%',
        '板装配率': f'{rate_slabs*100:.1f}%',
        '综合装配率': f'{assembly_rate:.1f}%',
        '装配等级': grade,
        '评价建筑面积': f'{project_area} m²' if project_area else '未提供',
    }
```

### 11.3 绿色建筑评价

```python
def evaluate_green_building(
    project_info: dict,
    scores: dict,  # 各评价项得分
) -> dict:
    """
    绿色建筑评价
    依据: GB/T 50378-2019《绿色建筑评价标准》
    评价指标: 安全耐久+健康舒适+生活便利+资源节约+环境宜居
    """
    # 五大指标满分均为100分
    categories = {
        '安全耐久': {'max': 100, 'min_pass': 60},
        '健康舒适': {'max': 100, 'min_pass': 60},
        '生活便利': {'max': 100, 'min_pass': 60},
        '资源节约': {'max': 100, 'min_pass': 60},
        '环境宜居': {'max': 100, 'min_pass': 60},
    }

    # 加分项(提高与创新)满分100分
    bonus_max = 100

    # 计算总得分
    total = 0
    detail = {}
    all_pass = True

    for cat, info in categories.items():
        score = scores.get(cat, 0)
        passed = score >= info['min_pass']
        if not passed:
            all_pass = False
        detail[cat] = {
            '得分': score,
            '满分': info['max'],
            '得分率': f'{score/info["max"]*100:.0f}%',
            '是否达标': '✓' if passed else '✗',
        }
        total += score

    bonus = scores.get('提高与创新', 0)
    total_with_bonus = total + bonus

    # 星级判定
    # 一星级: 总分≥60且各指标≥60
    # 二星级: 总分≥70且各指标≥60
    # 三星级: 总分≥85且各指标≥60
    if all_pass and total_with_bonus >= 85:
        star_level = '三星级'
    elif all_pass and total_with_bonus >= 70:
        star_level = '二星级'
    elif all_pass and total_with_bonus >= 60:
        star_level = '一星级'
    else:
        star_level = '不达标'

    return {
        '项目名称': project_info.get('name', ''),
        '评价指标': detail,
        '加分项得分': bonus,
        '总得分': round(total_with_bonus, 1),
        '绿色建筑等级': star_level,
        '是否全部达标': '✓ 是' if all_pass else '✗ 否，有指标不达标',
        '评价依据': 'GB/T 50378-2019',
    }
```

### 11.4 建筑能耗计算

```python
def calculate_building_energy(
    area: float,               # 建筑面积 m²
    climate_zone: str = 'hot_summer_cold_winter',  # 气候区
    building_type: str = 'residential',  # 'residential'/'office'/'commercial'
    heating_days: int = 90,    # 采暖天数
    cooling_days: int = 120,   # 空调天数
    u_walls: float = 0.6,      # 外墙传热系数 W/(m²·K)
    u_roof: float = 0.5,       # 屋面传热系数 W/(m²·K)
    u_windows: float = 2.5,    # 外窗传热系数 W/(m²·K)
    window_wall_ratio: float = 0.3,  # 窗墙比
    ac_cop: float = 3.5,       # 空调能效比
) -> dict:
    """
    建筑运行能耗计算
    依据: GB 50189-2015《公共建筑节能设计标准》、JGJ 26-2018《严寒和寒冷地区居住建筑节能设计标准》
    """
    # 采暖度日数和空调度日数
    hdd_map = {
        'severe_cold': 5000, 'cold': 3000,
        'hot_summer_cold_winter': 1500,
        'hot_summer_warm_winter': 300,
    }
    cdd_map = {
        'severe_cold': 50, 'cold': 150,
        'hot_summer_cold_winter': 300,
        'hot_summer_warm_winter': 600,
    }

    hdd = hdd_map.get(climate_zone, 1500)
    cdd = cdd_map.get(climate_zone, 300)

    # 体形系数估算
    form_factor = 0.3  # 简化

    # 采暖能耗 (简化计算)
    # Q_heat = 24×HDD×(U_wall×A_wall + U_roof×A_roof + U_win×A_win) / η / AC_COP
    wall_area = area * 0.4 * 4  # 估算外墙面积 (层高3m, 4面)
    roof_area = area * 0.1
    window_area = wall_area * window_wall_ratio
    wall_net = wall_area * (1 - window_wall_ratio)

    # 采暖热负荷
    heat_load = (u_walls * wall_net + u_roof * roof_area + u_windows * window_area) * 24 * hdd / 1000
    # 采暖能耗(kWh)
    heating_efficiency = 0.90  # 采暖系统效率
    energy_heating = heat_load / heating_efficiency

    # 空调能耗
    cool_load = (u_walls * wall_net + u_roof * roof_area + u_windows * window_area) * 24 * cdd / 1000
    energy_cooling = cool_load / ac_cop

    # 照明能耗 (按面积和天数估算)
    lighting_power_density = 5.0 if building_type == 'residential' else 9.0  # W/m²
    lighting_hours = 4 * 365
    energy_lighting = lighting_power_density * area * lighting_hours / 1000

    # 设备/插座能耗
    equipment_power = 3.0 if building_type == 'residential' else 15.0  # W/m²
    equipment_hours = 6 * 365
    energy_equipment = equipment_power * area * equipment_hours / 1000

    # 总能耗
    total_energy = energy_heating + energy_cooling + energy_lighting + energy_equipment
    energy_per_area = total_energy / area if area > 0 else 0

    # 碳排放 (运行阶段年碳排放)
    electricity_factor = 0.581  # kgCO₂e/kWh
    annual_carbon = total_energy * electricity_factor

    return {
        '气候区': climate_zone,
        '建筑面积': f'{area} m²',
        '采暖度日数HDD': hdd,
        '空调度日数CDD': cdd,
        '外墙传热系数': f'{u_walls} W/(m²·K)',
        '屋面传热系数': f'{u_roof} W/(m²·K)',
        '外窗传热系数': f'{u_windows} W/(m²·K)',
        '窗墙比': f'{window_wall_ratio}',
        '采暖能耗': f'{energy_heating:.0f} kWh/年',
        '空调能耗': f'{energy_cooling:.0f} kWh/年',
        '照明能耗': f'{energy_lighting:.0f} kWh/年',
        '设备能耗': f'{energy_equipment:.0f} kWh/年',
        '总能耗': f'{total_energy:.0f} kWh/年',
        '单位面积能耗': f'{energy_per_area:.1f} kWh/(m²·年)',
        '年运行碳排放': f'{annual_carbon:.0f} kgCO₂e ({annual_carbon/1000:.1f} tCO₂e)',
        '节能评价': _evaluate_energy_saving(energy_per_area, building_type),
    }

def _evaluate_energy_saving(energy_per_area: float, building_type: str) -> str:
    """节能评价"""
    thresholds = {
        'residential': [20, 30, 40],     # 优/良/一般/差
        'office': [40, 60, 80],
        'commercial': [50, 75, 100],
    }
    t = thresholds.get(building_type, [30, 50, 70])
    if energy_per_area <= t[0]:
        return '优 (超低能耗建筑水平)'
    elif energy_per_area <= t[1]:
        return '良 (节能建筑)'
    elif energy_per_area <= t[2]:
        return '一般 (满足节能标准)'
    else:
        return '差 (不满足节能要求)'
```

---

## 十二、施工组织与进度计划 (Construction Schedule & CPM)

> 依据: GB/T 50502-2009《建筑施工组织设计规范》、JGJ/T 132-2009《居住建筑节能检测标准》
> 方法: 网络计划技术(CPM/PERT)、横道图、资源动态曲线

---

### 12.1 双代号网络计划

```python
def build_cpm_network(tasks: list) -> dict:
    """
    双代号网络计划计算（关键路径法 CPM）
    tasks: [(task_id, name, duration_days, predecessors: list), ...]
    返回: 各任务最早开始/最早完成/最迟开始/最迟完成/总时差/自由时差 + 关键路径
    """
    # 构建任务字典
    task_map = {}
    for tid, name, duration, preds in tasks:
        task_map[tid] = {
            'id': tid, 'name': name, 'duration': duration,
            'predecessors': preds, 'successors': [],
        }
    # 构建后继关系
    for tid, task in task_map.items():
        for pred in task['predecessors']:
            if pred in task_map:
                task_map[pred]['successors'].append(tid)

    # 正向计算: 最早开始(ES)和最早完成(EF)
    calculated = set()
    max_iterations = len(task_map) * 2 + 10
    for _ in range(max_iterations):
        progress = False
        for tid, task in task_map.items():
            if tid in calculated:
                continue
            if all(p in calculated for p in task['predecessors']):
                if not task['predecessors']:
                    task['ES'] = 0
                else:
                    task['ES'] = max(task_map[p]['EF'] for p in task['predecessors'])
                task['EF'] = task['ES'] + task['duration']
                calculated.add(tid)
                progress = True
        if not progress:
            break
        if len(calculated) == len(task_map):
            break

    # 项目总工期
    project_duration = max((t.get('EF', 0) for t in task_map.values()), default=0)

    # 逆向计算: 最迟开始(LS)和最迟完成(LF)
    late_calculated = set()
    for tid, task in task_map.items():
        if not task['successors']:
            task['LF'] = project_duration
            task['LS'] = task['LF'] - task['duration']
            late_calculated.add(tid)

    for _ in range(max_iterations):
        progress = False
        for tid, task in task_map.items():
            if tid in late_calculated:
                continue
            if all(s in late_calculated for s in task['successors']):
                if task['successors']:
                    task['LF'] = min(task_map[s]['LS'] for s in task['successors'])
                else:
                    task['LF'] = project_duration
                task['LS'] = task['LF'] - task['duration']
                late_calculated.add(tid)
                progress = True
        if not progress:
            break
        if len(late_calculated) == len(task_map):
            break

    # 计算时差
    for tid, task in task_map.items():
        task['TF'] = task.get('LF', 0) - task.get('EF', 0)  # 总时差
        # 自由时差 FF = min(ES_successors) - EF
        if task['successors']:
            min_es_succ = min(task_map[s]['ES'] for s in task['successors'])
            task['FF'] = min_es_succ - task['EF']
        else:
            task['FF'] = project_duration - task['EF']

    # 关键路径: TF=0 的任务
    critical_path = [tid for tid, task in task_map.items() if task.get('TF', 0) == 0]

    return {
        'tasks': {tid: {
            'name': t['name'],
            'duration': t['duration'],
            'ES': t.get('ES', 0), 'EF': t.get('EF', 0),
            'LS': t.get('LS', 0), 'LF': t.get('LF', 0),
            'TF': t.get('TF', 0), 'FF': t.get('FF', 0),
            'is_critical': t.get('TF', 0) == 0,
        } for tid, t in task_map.items()},
        'project_duration': project_duration,
        'critical_path': critical_path,
    }
```

### 12.2 横道图（甘特图）生成

```python
def generate_gantt_chart(
    cpm_result: dict,
    output_path: str = None,
    start_date: str = '2026-01-01',
) -> str:
    """
    生成横道图(甘特图) — 使用matplotlib
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, '%Y-%m-%d')
    tasks = cpm_result['tasks']

    # 按最早开始时间排序
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1]['ES'])

    fig, ax = plt.subplots(figsize=(16, max(6, len(sorted_tasks) * 0.4)))

    y_positions = []
    y_labels = []
    for i, (tid, task) in enumerate(sorted_tasks):
        y = len(sorted_tasks) - i - 1
        y_positions.append(y)
        y_labels.append(f"{tid} {task['name']}")

        start_day = start + timedelta(days=task['ES'])
        duration = task['duration']

        # 关键路径红色，非关键蓝色
        color = '#FF4444' if task['is_critical'] else '#4488CC'
        ax.barh(y, duration, left=task['ES'], height=0.6,
                color=color, alpha=0.8, edgecolor='black', linewidth=0.5)

        # 标注工期
        ax.text(task['ES'] + duration / 2, y, f"{task['duration']}d",
                ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=8)
    ax.set_xlabel('日期', fontsize=10)
    ax.set_title(f'施工进度横道图 (总工期: {cpm_result["project_duration"]}天)', fontsize=12)

    # X轴日期格式
    max_days = cpm_result['project_duration']
    ax.set_xlim(-1, max_days + 5)
    week_ticks = list(range(0, max_days + 7, 7))
    week_labels = [(start + timedelta(days=d)).strftime('%m-%d') for d in week_ticks]
    ax.set_xticks(week_ticks)
    ax.set_xticklabels(week_labels, fontsize=7, rotation=45)

    ax.grid(axis='x', alpha=0.3)
    ax.legend(['关键路径', '非关键路径'], loc='upper right', fontsize=8)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path
    else:
        plt.close()
        return None
```

### 12.3 资源动态曲线

```python
def calculate_resource_curve(
    cpm_result: dict,
    resources: dict,  # {task_id: (workers, cost_per_day)}, 每日人工/费用
    resource_type: str = 'workers',  # 'workers'/'cost'
) -> dict:
    """
    资源动态曲线计算
    返回每日资源需求量，用于绘制资源动态曲线和峰值分析
    """
    duration = cpm_result['project_duration']
    daily_resource = [0] * (duration + 1)

    for tid, task in cpm_result['tasks'].items():
        if tid in resources:
            r = resources[tid]
            daily_amount = r if isinstance(r, (int, float)) else r[0] if resource_type == 'workers' else r[1]
            for day in range(int(task['ES']), int(task['EF'])):
                if day < len(daily_resource):
                    daily_resource[day] += daily_amount

    peak = max(daily_resource)
    peak_day = daily_resource.index(peak)
    avg = sum(daily_resource) / max(duration, 1)

    # 不均衡系数
    imbalance = peak / avg if avg > 0 else 0

    return {
        'daily_resource': daily_resource,
        'peak_value': peak,
        'peak_day': peak_day,
        'average': round(avg, 1),
        'imbalance_factor': round(imbalance, 2),
        'duration': duration,
        '评价': '均衡' if imbalance < 1.5 else '不均衡，需优化',
    }
```

### 12.4 工期优化与资源均衡

```python
def optimize_resource_leveling(
    cpm_result: dict,
    resources: dict,
    max_iterations: int = 100,
) -> dict:
    """
    资源均衡优化（启发式方法）
    将非关键工作在时差范围内移动，使资源需求更均衡
    依据: 工期固定-资源均衡问题(RCPSP)
    """
    tasks = dict(cpm_result['tasks'])
    duration = cpm_result['project_duration']

    # 初始资源曲线
    initial = calculate_resource_curve(cpm_result, resources)

    best_schedule = {tid: {'ES': t['ES']} for tid, t in tasks.items()}
    best_variance = _resource_variance(initial['daily_resource'])

    # 尝试移动非关键任务
    for _ in range(max_iterations):
        improved = False
        non_critical = [(tid, t) for tid, t in tasks.items()
                        if not t['is_critical'] and t['TF'] > 0]

        for tid, task in non_critical:
            original_es = best_schedule[tid]['ES']
            best_shift = 0

            for shift in range(0, int(task['TF']) + 1):
                best_schedule[tid]['ES'] = original_es + shift
                temp_cpm = _rebuild_schedule(tasks, best_schedule, duration)
                temp_curve = calculate_resource_curve(temp_cpm, resources)
                v = _resource_variance(temp_curve['daily_resource'])
                if v < best_variance:
                    best_variance = v
                    best_shift = shift

            best_schedule[tid]['ES'] = original_es + best_shift
            if best_shift > 0:
                improved = True

        if not improved:
            break

    # 最终结果
    final_cpm = _rebuild_schedule(tasks, best_schedule, duration)
    final_curve = calculate_resource_curve(final_cpm, resources)

    return {
        '优化前峰值': initial['peak_value'],
        '优化后峰值': final_curve['peak_value'],
        '优化前不均衡系数': initial['imbalance_factor'],
        '优化后不均衡系数': final_curve['imbalance_factor'],
        '改善率': f'{(1 - best_variance / _resource_variance(initial["daily_resource"]))*100:.1f}%',
        '优化后日程': best_schedule,
        '评价': '优化效果显著' if initial['imbalance_factor'] - final_curve['imbalance_factor'] > 0.2 else '优化效果一般',
    }

def _resource_variance(daily: list) -> float:
    """计算资源方差的Σ(Ri - Ravg)²"""
    n = len(daily)
    avg = sum(daily) / max(n, 1)
    return sum((r - avg) ** 2 for r in daily)

def _rebuild_schedule(tasks: dict, schedule: dict, duration: int) -> dict:
    """根据新的ES重建CPM结果"""
    result_tasks = {}
    for tid, task in tasks.items():
        es = schedule[tid]['ES']
        result_tasks[tid] = {
            **task,
            'ES': es,
            'EF': es + task['duration'],
            'is_critical': task['is_critical'],
        }
    return {'tasks': result_tasks, 'project_duration': duration, 'critical_path': []}
```

### 12.5 标准施工工序模板

```python
# 常见工程类型的标准工序分解
STANDARD_SEQUENCES = {
    'building': [
        # (工序号, 名称, 工期(天), 紧前工序)
        ('A', '施工准备', 7, []),
        ('B', '土方开挖', 15, ['A']),
        ('C', '基坑支护', 20, ['B']),
        ('D', '基础垫层', 3, ['C']),
        ('E', '基础施工', 25, ['D']),
        ('F', '地下室外墙', 15, ['E']),
        ('G', '±0.000以下回填', 5, ['F']),
        ('H', '一层结构', 12, ['G']),
        ('I', '二层结构', 12, ['H']),
        ('J', '主体结构(标准层)', 10, ['I']),
        ('K', '屋面工程', 15, ['J']),
        ('L', '砌筑工程', 30, ['J']),
        ('M', '抹灰工程', 25, ['L']),
        ('N', '门窗安装', 20, ['M']),
        ('O', '外墙装饰', 20, ['K', 'N']),
        ('P', '室内精装', 40, ['M', 'N']),
        ('Q', '机电安装', 45, ['J']),
        ('R', '电梯安装', 20, ['Q']),
        ('S', '室外工程', 15, ['O', 'P']),
        ('T', '竣工验收', 7, ['Q', 'R', 'S']),
    ],
    'highway': [
        ('A', '施工准备', 10, []),
        ('B', '路基清表', 15, ['A']),
        ('C', '路基填筑', 60, ['B']),
        ('D', '涵洞施工', 30, ['B']),
        ('E', '路基排水', 20, ['C']),
        ('F', '底基层施工', 25, ['C', 'D']),
        ('G', '基层施工', 20, ['F']),
        ('H', '面层施工', 30, ['G']),
        ('I', '桥梁基础', 45, ['A']),
        ('J', '桥梁下部结构', 40, ['I']),
        ('K', '桥梁上部结构', 60, ['J']),
        ('L', '桥面系', 20, ['K', 'H']),
        ('M', '交通安全设施', 15, ['H', 'L']),
        ('N', '绿化工程', 20, ['E', 'H']),
        ('O', '交工验收', 7, ['M', 'N']),
    ],
    'tunnel': [
        ('A', '施工准备', 10, []),
        ('B', '洞口工程', 15, ['A']),
        ('C', '超前支护', 10, ['B']),
        ('D', '上台阶开挖', 180, ['C']),
        ('E', '下台阶开挖', 150, ['D']),
        ('F', '初期支护', 160, ['D']),
        ('G', '防水层', 140, ['F']),
        ('H', '二次衬砌', 150, ['G']),
        ('I', '仰拱填充', 130, ['E']),
        ('J', '水沟电缆槽', 60, ['H', 'I']),
        ('K', '路面工程', 30, ['J']),
        ('L', '机电安装', 40, ['J']),
        ('M', '装饰装修', 25, ['K']),
        ('N', '竣工验收', 7, ['L', 'M']),
    ],
}

def get_standard_sequence(project_type: str) -> list:
    """获取标准施工工序模板"""
    return STANDARD_SEQUENCES.get(project_type, STANDARD_SEQUENCES['building'])
```

### 12.6 进度跟踪与偏差分析

```python
def track_schedule_progress(
    cpm_result: dict,
    actual_progress: dict,  # {task_id: 实际完成百分比(0~1)}
    current_day: int,
) -> dict:
    """
    进度跟踪与偏差分析（挣值法 EVM）
    依据: GB/T 50502-2009 附录B
    """
    tasks = cpm_result['tasks']
    total_duration = cpm_result['project_duration']

    # 计划价值 PV (Plan Value) — 计划完成百分比
    pv = 0
    for tid, task in tasks.items():
        planned = min(max((current_day - task['ES']) / max(task['duration'], 1), 0), 1)
        pv += planned * task['duration']

    # 挣值 EV (Earned Value) — 实际完成百分比
    ev = 0
    for tid, task in tasks.items():
        actual = actual_progress.get(tid, 0)
        ev += actual * task['duration']

    # 实际成本 AC (Actual Cost) — 简化: 按天数计
    ac = current_day  # 简化: 实际消耗时间

    # 偏差分析
    sv = ev - pv  # 进度偏差 (正值=提前)
    cv = ev - ac  # 成本偏差 (正值=节约)

    # 绩效指数
    spi = ev / pv if pv > 0 else 0  # 进度绩效指数 (SPI>1=提前)
    cpi = ev / ac if ac > 0 else 0  # 成本绩效指数 (CPI>1=节约)

    # 预测完工工期
    estimated_total = total_duration / spi if spi > 0 else total_duration
    remaining_days = estimated_total - current_day

    # 偏差状态判断
    if spi >= 1.0:
        status = '进度正常或提前'
    elif spi >= 0.9:
        status = '进度轻微滞后'
    elif spi >= 0.8:
        status = '进度滞后，需关注'
    else:
        status = '进度严重滞后，需采取措施'

    return {
        '当前日期': f'第{current_day}天',
        '计划工期': f'{total_duration}天',
        '计划价值PV': f'{pv:.1f} 工日',
        '挣值EV': f'{ev:.1f} 工日',
        '实际成本AC': f'{ac} 工日',
        '进度偏差SV': f'{sv:.1f} 工日 ({"提前" if sv > 0 else "滞后"})',
        '成本偏差CV': f'{cv:.1f} 工日',
        '进度绩效指数SPI': f'{spi:.3f}',
        '成本绩效指数CPI': f'{cpi:.3f}',
        '预测完工工期': f'{estimated_total:.0f}天',
        '剩余工期': f'{remaining_days:.0f}天',
        '进度状态': status,
        '建议': _schedule_suggestion(spi, cpi),
    }

def _schedule_suggestion(spi: float, cpi: float) -> str:
    """进度建议"""
    suggestions = []
    if spi < 0.9:
        suggestions.append('增加人力/机械投入，优化关键路径工序')
    if spi < 0.8:
        suggestions.append('考虑平行施工或夜间加班')
    if cpi < 0.9:
        suggestions.append('成本超支，审查资源使用效率')
    if not suggestions:
        suggestions.append('进度正常，继续保持')
    return '；'.join(suggestions)
```

---

## 十三、Excel计算表生成器 (Excel Calculation Sheet Generator)

> 多模板、公式联动、自动汇总的Excel计算表生成系统
> 依赖: openpyxl ≥ 3.1

---

### 13.1 样式系统

```python
from openpyxl import Workbook
from openpyxl.styles import (Font, Alignment, Border, Side, PatternFill,
                              Protection, NamedStyle)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule

# ============ 统一样式系统 ============
STYLES = {
    'title': {
        'font': Font(name='宋体', size=16, bold=True, color='1F4E79'),
        'alignment': Alignment(horizontal='center', vertical='center'),
    },
    'subtitle': {
        'font': Font(name='宋体', size=12, bold=True, color='FFFFFF'),
        'fill': PatternFill('solid', start_color='2E75B6'),
        'alignment': Alignment(horizontal='center', vertical='center'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'header': {
        'font': Font(name='宋体', size=10, bold=True, color='FFFFFF'),
        'fill': PatternFill('solid', start_color='4472C4'),
        'alignment': Alignment(horizontal='center', vertical='center', wrap_text=True),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'data': {
        'font': Font(name='宋体', size=10),
        'alignment': Alignment(horizontal='center', vertical='center'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'data_left': {
        'font': Font(name='宋体', size=10),
        'alignment': Alignment(horizontal='left', vertical='center', wrap_text=True),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'subtotal': {
        'font': Font(name='宋体', size=10, bold=True),
        'fill': PatternFill('solid', start_color='D6E4F0'),
        'alignment': Alignment(horizontal='center'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='medium'), bottom=Side(style='thin')),
    },
    'total': {
        'font': Font(name='宋体', size=11, bold=True, color='1F4E79'),
        'fill': PatternFill('solid', start_color='B4C7E7'),
        'alignment': Alignment(horizontal='center'),
        'border': Border(
            left=Side(style='medium'), right=Side(style='medium'),
            top=Side(style='medium'), bottom=Side(style='double')),
    },
    'note': {
        'font': Font(name='宋体', size=9, italic=True, color='808080'),
        'alignment': Alignment(horizontal='left'),
    },
    'input': {
        'font': Font(name='宋体', size=10, color='0000CC'),
        'fill': PatternFill('solid', start_color='FFF2CC'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'formula': {
        'font': Font(name='宋体', size=10, color='0070C0'),
        'fill': PatternFill('solid', start_color='E2EFDA'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
}

def apply_style(cell, style_name: str):
    """快速应用预定义样式"""
    s = STYLES.get(style_name, STYLES['data'])
    if 'font' in s: cell.font = s['font']
    if 'fill' in s: cell.fill = s['fill']
    if 'alignment' in s: cell.alignment = s['alignment']
    if 'border' in s: cell.border = s['border']

def set_column_widths(ws, widths: dict):
    """批量设置列宽 {列字母: 宽度}"""
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
```

### 13.2 混凝土工程量计算表模板

```python
def generate_concrete_quantity_sheet(
    wb: Workbook,
    project_name: str = '',
    data: list = None,  # [(部位, 构件类型, 截面尺寸, 长度/高度, 数量, 备注), ...]
) -> str:
    """
    生成混凝土工程量计算表(含公式联动)
    黄色单元格=输入项, 绿色单元格=自动计算公式
    """
    ws = wb.create_sheet("混凝土工程量计算表")

    # === 标题区 ===
    ws.merge_cells('A1:H1')
    ws['A1'] = f"混凝土工程量计算表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:H2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # === 表头 ===
    headers = ['序号', '部位/楼层', '构件类型', '截面尺寸(mm)', '长度/高度(m)',
               '数量', '体积(m³)', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[4].height = 30

    # === 数据行(含Excel公式联动) ===
    if not data:
        # 提供空模板(15行)
        data = [('', '', '', '', '', '')] * 15

    start_row = 5
    for idx, (location, elem_type, section, length, count, note) in enumerate(data):
        r = start_row + idx
        # 序号
        ws.cell(row=r, column=1, value=idx + 1)
        apply_style(ws.cell(row=r, column=1), 'data')

        # 输入项(黄色)
        for col, val in [(2, location), (3, elem_type), (4, section),
                         (5, length), (6, count), (8, note)]:
            cell = ws.cell(row=r, column=col, value=val)
            apply_style(cell, 'input')

        # 公式项(绿色): G列 = D(截面解析) × E(长度) × F(数量)
        # 截面尺寸格式如"600×600"或"300×500(宽×高)"
        formula = f'=IFERROR(_parse_section(D{r})*E{r}*F{r},"")'
        cell = ws.cell(row=r, column=7, value=formula)
        apply_style(cell, 'formula')
        cell.number_format = '0.00'

    # === 合计行 ===
    end_row = start_row + len(data)
    ws.merge_cells(f'A{end_row}:F{end_row}')
    ws.cell(row=end_row, column=1, value="合计")
    apply_style(ws.cell(row=end_row, column=1), 'total')
    sum_formula = f'=SUM(G{start_row}:G{end_row-1})'
    cell = ws.cell(row=end_row, column=7, value=sum_formula)
    apply_style(cell, 'total')
    cell.number_format = '0.00'
    ws.cell(row=end_row, column=8, value="m³")
    apply_style(ws.cell(row=end_row, column=8), 'total')

    # === 说明区 ===
    note_row = end_row + 2
    ws.merge_cells(f'A{note_row}:H{note_row}')
    ws.cell(row=note_row, column=1,
            value="说明: 黄色单元格为输入项, 绿色单元格为自动计算公式。截面尺寸格式: 宽×高(如300×500)")
    apply_style(ws.cell(row=note_row, column=1), 'note')

    # 列宽
    set_column_widths(ws, {'A': 6, 'B': 16, 'C': 14, 'D': 18, 'E': 14, 'F': 8, 'G': 12, 'H': 20})

    return ws.title
```

### 13.3 钢筋工程量计算表模板

```python
def generate_rebar_quantity_sheet(
    wb: Workbook,
    project_name: str = '',
    data: list = None,
) -> str:
    """
    生成钢筋工程量计算表(含理论重量联动)
    计算: 重量 = 长度 × 数量 × 理论重量(kg/m)
    """
    ws = wb.create_sheet("钢筋工程量计算表")

    ws.merge_cells('A1:J1')
    ws['A1'] = "钢筋工程量计算表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:J2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # 钢筋理论重量参考表
    ws.merge_cells('A4:J4')
    ws['A4'] = "钢筋理论重量参考表(kg/m)"
    apply_style(ws['A4'], 'subtitle')

    rebar_ref = [['Φ6', 0.222], ['Φ8', 0.395], ['Φ10', 0.617], ['Φ12', 0.888],
                 ['Φ14', 1.21], ['Φ16', 1.58], ['Φ18', 2.0], ['Φ20', 2.47],
                 ['Φ22', 2.98], ['Φ25', 3.85], ['Φ28', 4.83], ['Φ32', 6.31]]
    for col, (spec, weight) in enumerate(rebar_ref):
        c1 = ws.cell(row=5, column=col*2+1, value=spec)
        c2 = ws.cell(row=5, column=col*2+2, value=weight)
        apply_style(c1, 'data')
        apply_style(c2, 'data')
        c2.number_format = '0.000'

    # 表头
    headers = ['序号', '部位', '钢筋编号', '规格', '简图', '单根长度(m)',
               '根数', '理论重量(kg/m)', '总重量(kg)', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=7, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[7].height = 30

    # 数据行
    if not data:
        data = [('', '', '', '', '', '', '')] * 15

    start_row = 8
    for idx, (location, rebar_id, spec, sketch, length, count, note) in enumerate(data):
        r = start_row + idx
        ws.cell(row=r, column=1, value=idx + 1)
        apply_style(ws.cell(row=r, column=1), 'data')

        for col, val in [(2, location), (3, rebar_id), (4, spec), (5, sketch),
                         (6, length), (7, count), (10, note)]:
            cell = ws.cell(row=r, column=col, value=val)
            apply_style(cell, 'input')

        # 理论重量(H列): VLOOKUP查表
        ws.cell(row=r, column=8,
                value=f'=IFERROR(VLOOKUP(D{r},$A$5:$X$5,2,FALSE),"")')
        apply_style(ws.cell(row=r, column=8), 'formula')
        ws.cell(row=r, column=8).number_format = '0.000'

        # 总重量(I列): F(长度) × G(根数) × H(理论重量)
        ws.cell(row=r, column=9,
                value=f'=IFERROR(F{r}*G{r}*H{r},"")')
        apply_style(ws.cell(row=r, column=9), 'formula')
        ws.cell(row=r, column=9).number_format = '0.0'

    # 合计
    end_row = start_row + len(data)
    ws.merge_cells(f'A{end_row}:H{end_row}')
    ws.cell(row=end_row, column=1, value="合计")
    apply_style(ws.cell(row=end_row, column=1), 'total')
    ws.cell(row=end_row, column=9, value=f'=SUM(I{start_row}:I{end_row-1})')
    apply_style(ws.cell(row=end_row, column=9), 'total')
    ws.cell(row=end_row, column=9).number_format = '0.0'
    ws.cell(row=end_row, column=10, value="kg")
    apply_style(ws.cell(row=end_row, column=10), 'total')

    set_column_widths(ws, {'A': 6, 'B': 14, 'C': 12, 'D': 10, 'E': 16, 'F': 14, 'G': 8, 'H': 14, 'I': 14, 'J': 18})

    return ws.title
```

### 13.4 综合工程量清单汇总表

```python
def generate_quantity_summary_sheet(wb: Workbook, project_name: str = '') -> str:
    """
    综合工程量清单汇总表(多专业、自动汇总)
    """
    ws = wb.create_sheet("工程量清单汇总表")

    ws.merge_cells('A1:G1')
    ws['A1'] = "工程量清单汇总表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:G2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # 表头
    headers = ['序号', '清单编码', '项目名称', '计量单位', '工程量', '专业类别', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[4].height = 30

    # 专业分类汇总区
    categories = [
        ('土建工程', '0101~0117', 20),
        ('市政工程', '0401~0413', 15),
        ('公路工程', 'JTG', 15),
        ('幕墙工程', '0110', 10),
        ('钢结构工程', '0106', 10),
        ('隧道工程', '0114', 10),
    ]

    start_row = 5
    current_row = start_row
    category_subtotals = {}

    for cat_name, code_range, num_rows in categories:
        # 专业小标题
        ws.merge_cells(f'A{current_row}:G{current_row}')
        ws.cell(row=current_row, column=1, value=f"  ▶ {cat_name} ({code_range})")
        apply_style(ws.cell(row=current_row, column=1), 'subtitle')
        current_row += 1

        # 空行供填写
        cat_start = current_row
        for i in range(num_rows):
            ws.cell(row=current_row, column=1, value=i + 1)
            apply_style(ws.cell(row=current_row, column=1), 'data')
            for col in range(2, 8):
                apply_style(ws.cell(row=current_row, column=col), 'input')
            current_row += 1

        # 专业小计
        ws.merge_cells(f'A{current_row}:D{current_row}')
        ws.cell(row=current_row, column=1, value=f"{cat_name} 小计")
        apply_style(ws.cell(row=current_row, column=1), 'subtotal')
        ws.cell(row=current_row, column=5, value=f'=COUNTA(B{cat_start}:B{current_row-1})')
        apply_style(ws.cell(row=current_row, column=5), 'subtotal')
        ws.cell(row=current_row, column=6, value=f'共{num_rows}项')
        apply_style(ws.cell(row=current_row, column=6), 'subtotal')

        category_subtotals[cat_name] = current_row
        current_row += 1

    # 总计行
    ws.merge_cells(f'A{current_row}:D{current_row}')
    ws.cell(row=current_row, column=1, value="工程总计")
    apply_style(ws.cell(row=current_row, column=1), 'total')
    total_rows = [r for r in category_subtotals.values()]
    count_formula = '=' + '+'.join([f'COUNTA(B{s+1}:B{r-1})' for s, r in
        zip([start_row] + total_rows, total_rows + [current_row])])
    ws.cell(row=current_row, column=5, value=f'=COUNTA(B5:B{current_row-1})')
    apply_style(ws.cell(row=current_row, column=5), 'total')

    set_column_widths(ws, {'A': 6, 'B': 16, 'C': 30, 'D': 10, 'E': 14, 'F': 14, 'G': 18})

    return ws.title
```

### 13.5 工程造价汇总表

```python
def generate_cost_summary_sheet(wb: Workbook, project_name: str = '') -> str:
    """
    工程造价汇总表(含公式联动、税率自动计算)
    """
    ws = wb.create_sheet("工程造价汇总表")

    ws.merge_cells('A1:E1')
    ws['A1'] = "工程造价汇总表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:E2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # 参数区
    ws['A4'] = "计税方式:"
    apply_style(ws['A4'], 'data_left')
    ws['B4'] = "一般计税"
    apply_style(ws['B4'], 'input')
    ws['C4'] = "税率:"
    apply_style(ws['C4'], 'data_left')
    ws['D4'] = 0.09
    apply_style(ws['D4'], 'input')
    ws['D4'].number_format = '0.00%'

    # 汇总表
    headers = ['序号', '费用项目', '计算基础', '费率(%)', '金额(元)']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[6].height = 30

    # 费用行(含公式联动)
    rows_data = [
        ('1', '分部分项工程费', '按清单合计', '', '=0'),  # 手动输入或引用
        ('2', '措施项目费', '人工+机械', '按实际', '=0'),
        ('2.1', '  安全文明施工费', '分部分项工程费', '3.00%', '=D7*0.03'),
        ('2.2', '  夜间施工增加费', '分部分项工程费', '0.50%', '=D7*0.005'),
        ('2.3', '  二次搬运费', '分部分项工程费', '0.80%', '=D7*0.008'),
        ('2.4', '  冬雨季施工增加费', '分部分项工程费', '1.00%', '=D7*0.01'),
        ('2.5', '  脚手架费', '按实际', '', '=0'),
        ('2.6', '  模板费', '按实际', '', '=0'),
        ('3', '其他项目费', '按实际', '', '=0'),
        ('4', '规费', '1+2+3', '4.30%', '=(D7+D8+D15)*0.043'),
        ('4.1', '  社保费', '1+2+3', '3.20%', '=(D7+D8+D15)*0.032'),
        ('4.2', '  住房公积金', '1+2+3', '1.00%', '=(D7+D8+D15)*0.01'),
        ('4.3', '  工程排污费', '1+2+3', '0.10%', '=(D7+D8+D15)*0.001'),
        ('5', '税金', '1+2+3+4', '=D4', '=(D7+D8+D15+D16)*D4'),
        ('', '工程总造价', '1+2+3+4+5', '', '=D7+D8+D15+D16+D20'),
    ]

    start_row = 7
    for idx, (no, name, base, rate, formula) in enumerate(rows_data):
        r = start_row + idx
        ws.cell(row=r, column=1, value=no)
        ws.cell(row=r, column=2, value=name)

        if no in ('', '5') or name == '工程总造价':
            # 总计行
            apply_style(ws.cell(row=r, column=1), 'total')
            apply_style(ws.cell(row=r, column=2), 'total')
            ws.cell(row=r, column=3, value=base)
            apply_style(ws.cell(row=r, column=3), 'total')
            ws.cell(row=r, column=4, value=rate)
            apply_style(ws.cell(row=r, column=4), 'total')
            ws.cell(row=r, column=5, value=formula)
            apply_style(ws.cell(row=r, column=5), 'total')
            ws.cell(row=r, column=5).number_format = '#,##0.00'
        elif '.' in str(no):
            # 子项行
            apply_style(ws.cell(row=r, column=1), 'data')
            apply_style(ws.cell(row=r, column=2), 'data_left')
            ws.cell(row=r, column=3, value=base)
            apply_style(ws.cell(row=r, column=3), 'data_left')
            ws.cell(row=r, column=4, value=rate)
            apply_style(ws.cell(row=r, column=4), 'data')
            ws.cell(row=r, column=5, value=formula)
            apply_style(ws.cell(row=r, column=5), 'formula')
            ws.cell(row=r, column=5).number_format = '#,##0.00'
        else:
            # 主项行
            apply_style(ws.cell(row=r, column=1), 'subtotal')
            apply_style(ws.cell(row=r, column=2), 'subtotal')
            ws.cell(row=r, column=3, value=base)
            apply_style(ws.cell(row=r, column=3), 'subtotal')
            ws.cell(row=r, column=4, value=rate)
            apply_style(ws.cell(row=r, column=4), 'subtotal')
            ws.cell(row=r, column=5, value=formula)
            apply_style(ws.cell(row=r, column=5), 'subtotal')
            ws.cell(row=r, column=5).number_format = '#,##0.00'

    # 更新措施项目费合计公式
    ws.cell(row=8, column=5, value='=D9+D10+D11+D12+D13+D14')
    # 更新规费合计公式
    ws.cell(row=16, column=5, value='=D17+D18+D19')

    # 说明
    note_row = start_row + len(rows_data) + 1
    ws.merge_cells(f'A{note_row}:E{note_row}')
    ws.cell(row=note_row, column=1,
            value="说明: 黄色=输入项, 绿色=公式自动计算。修改D4税率或D7分部分项工程费后,所有费用自动联动更新。")
    apply_style(ws.cell(row=note_row, column=1), 'note')

    set_column_widths(ws, {'A': 6, 'B': 24, 'C': 16, 'D': 12, 'E': 16})

    return ws.title
```

### 13.6 一键生成完整工程Excel工作簿

```python
def generate_full_project_workbook(
    project_name: str = '',
    output_path: str = '工程量计算表.xlsx',
    sheets: list = None,
) -> str:
    """
    一键生成完整工程Excel工作簿
    包含: 混凝土算量表 + 钢筋算量表 + 清单汇总表 + 造价汇总表
    """
    wb = Workbook()

    # 删除默认Sheet
    wb.remove(wb.active)

    # 默认生成全部Sheet
    if sheets is None:
        sheets = ['concrete', 'rebar', 'summary', 'cost']

    if 'concrete' in sheets:
        generate_concrete_quantity_sheet(wb, project_name)

    if 'rebar' in sheets:
        generate_rebar_quantity_sheet(wb, project_name)

    if 'summary' in sheets:
        generate_quantity_summary_sheet(wb, project_name)

    if 'cost' in sheets:
        generate_cost_summary_sheet(wb, project_name)

    # 设置封面
    ws_cover = wb.create_sheet("封面", 0)
    ws_cover.merge_cells('A1:H1')
    ws_cover['A1'] = project_name or "工程量计算表"
    apply_style(ws_cover['A1'], 'title')
    ws_cover.row_dimensions[1].height = 40

    ws_cover.merge_cells('A2:H2')
    ws_cover['A2'] = f"生成日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}"
    apply_style(ws_cover['A2'], 'note')

    # 目录
    ws_cover.merge_cells('A4:H4')
    ws_cover['A4'] = "目录"
    apply_style(ws_cover['A4'], 'subtitle')

    sheet_names = [ws.title for ws in wb.worksheets if ws.title != '封面']
    for i, name in enumerate(sheet_names):
        ws_cover.cell(row=5 + i, column=1, value=f"{i+1}. {name}")
        apply_style(ws_cover.cell(row=5 + i, column=1), 'data_left')

    wb.save(output_path)
    return output_path
```

### 13.7 条件格式与数据校验

```python
def add_conditional_formatting(ws, cell_range: str):
    """添加条件格式: 负值红色, 正值绿色"""
    from openpyxl.formatting.rule import CellIsRule
    red_font = Font(color='FF0000', bold=True)
    green_font = Font(color='008000')
    ws.conditional_formatting.add(cell_range,
        CellIsRule(operator='lessThan', formula=['0'], font=red_font))
    ws.conditional_formatting.add(cell_range,
        CellIsRule(operator='greaterThan', formula=['0'], font=green_font))

def add_data_validation(ws, cell_range: str, validation_type: str = 'list', formula: str = ''):
    """添加数据校验下拉列表"""
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type=validation_type, formula1=formula, allow_blank=True)
    dv.error = '输入值不在允许范围内'
    dv.errorTitle = '输入错误'
    ws.add_data_validation(dv)
    dv.add(cell_range)
```

---

## 十四、函数注册表 (API Registry)

> 全部 67 个函数的标准化签名、参数说明、返回值格式和调用示例。
> AI 助手通过 §8 关键字矩阵匹配意图后，在此查找精确函数签名。

---

### 函数签名格式规范

每个函数按以下格式注册：

```
#### FUNC-XXX: function_name()
- 模块: 源模块文件
- 意图: 对应§8的意图ID
- 参数: 参数名(类型) — 说明
- 返回: dict — 返回值结构
- 依据: 规范编号
- 示例: 调用代码片段
```

---

### 14.1 工程识图函数 (DRAWING)

#### FUNC-001: `parse_cad_drawing(filepath)`
- **模块**: 01-drawing.md §1.2
- **意图**: drawing
- **参数**: `filepath` (str) — DWG/DXF文件路径
- **返回**: `dict` — `{units, min_extents, max_extents, layers[], entities{lines[],polylines[],arcs[],circles[],texts[],dimensions[],blocks[],hatches[],splines[],ellipses[],points[],inserts[]}}`
- **依赖**: `ezdxf`
- **示例**:
```python
info = parse_cad_drawing("floor_plan.dxf")
# info['layers'] → ['WALL', 'COLUMN', 'BEAM', ...]
# info['entities']['lines'] → [{start, end, length, layer, handle}, ...]
```

#### FUNC-002: `extract_block_definitions(doc)`
- **模块**: 01-drawing.md §1.4
- **意图**: drawing
- **参数**: `doc` — ezdxf文档对象
- **返回**: `dict` — `{block_name: {entities[], origin, layer}}`
- **示例**:
```python
doc = ezdxf.readfile("plan.dxf")
blocks = extract_block_definitions(doc)
# blocks['WINDOW_1500'] → {entities: [...], origin: (0,0,0)}
```

#### FUNC-003: `explode_block_reference(block_ref, block_definitions, layer)`
- **模块**: 01-drawing.md §1.4
- **意图**: drawing
- **参数**: `block_ref` — INSERT实体; `block_definitions` (dict) — FUNC-002返回值; `layer` (str, 可选) — 过滤图层
- **返回**: `list[dict]` — 展开后的图元列表

#### FUNC-004: `detect_drawing_scale(doc)`
- **模块**: 01-drawing.md §1.5
- **意图**: drawing
- **参数**: `doc` — ezdxf文档对象
- **返回**: `dict` — `{scale, paper_size, dimscale, method}`
- **说明**: 自动识别图纸比例(A0~A4 + DIMSCALE)

#### FUNC-005: `classify_layers(layers)`
- **模块**: 01-drawing.md §1.6
- **意图**: drawing
- **参数**: `layers` (list[str]) — 图层名列表
- **返回**: `dict` — `{category: [layer_names]}`，类别含 wall/column/beam/slab/door/window/dimension/text/other
- **说明**: 基于20+关键字映射

#### FUNC-006: `compare_drawings(file_old, file_new)`
- **模块**: 01-drawing.md §1.7
- **意图**: drawing
- **参数**: `file_old` (str); `file_new` (str) — 新旧版本文件路径
- **返回**: `dict` — `{added[], removed[], modified[], summary}`
- **说明**: 图纸版本对比，识别新增/删除/修改的图元

---

### 14.2 工程量计算函数 (QUANTITY)

#### FUNC-007: `calculate_concrete_detail(entities, element_type)`
- **模块**: 02-quantity.md §2.1.1
- **意图**: quantity
- **参数**:
  - `entities` (list) — 构件几何数据列表
  - `element_type` (str) — 构件类型: `'column'`/`'beam'`/`'wall'`/`'slab'`/`'foundation'`
- **返回**: `dict` — `{volume, formwork, deductions[], code, unit}`
- **依据**: GB 50854-2013, 22G101-1
- **示例**:
```python
result = calculate_concrete_detail(columns, 'column')
# result['volume'] → 12.50 (m³)
# result['formwork'] → 85.20 (m²)
# result['code'] → '010502001'
```

#### FUNC-008: `calculate_secondary_elements(data)`
- **模块**: 02-quantity.md §2.1.2
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'column'/'lintel'/'ring_beam'/'press_top', location, section, length, count, shape: '一字'/'L形'/'丁字'/'十字'}`
- **返回**: `dict` — `{volume, formwork, horse_tooth_coeff, code}`
- **说明**: 马牙槎系数 — 一字0.06/L形0.10/丁字0.13/十字0.19

#### FUNC-009: `calculate_masonry(wall_data)`
- **模块**: 02-quantity.md §2.1.3
- **意图**: quantity
- **参数**: `wall_data` (dict) — `{wall_type: '115'/'240'/'365'/'490', length, height, openings[], mortar_type}`
- **返回**: `dict` — `{volume, brick_count, mortar_volume, code}`
- **说明**: 砖用量表 — 115墙552/240墙529/365墙522/490墙518块/m³

#### FUNC-010: `anchorage_length(grade, concrete, rebar_type)`
- **模块**: 02-quantity.md §2.1.4
- **意图**: quantity
- **参数**: `grade` (int) — 钢筋直径; `concrete` (str) — 混凝土等级'C20'~'C50'; `rebar_type` (str) — 'HRB400'/'HPB300'
- **返回**: `int` — 锚固长度(mm)
- **依据**: GB 50010-2010(2015版) §8.3.1, 22G101-1
- **示例**:
```python
la = anchorage_length(20, 'C30', 'HRB400')
# la → 700 (mm)
```

#### FUNC-011: `calculate_full_rebar(element_data, element_type)`
- **模块**: 02-quantity.md §2.1.4
- **意图**: quantity
- **参数**:
  - `element_data` (dict) — 构件尺寸和配筋数据
  - `element_type` (str) — `'beam'`/`'column'`/`'slab'`/`'wall'`/`'foundation'`
- **返回**: `dict` — `{total_weight_kg, bars[], anchorage_total, lap_total, code}`
- **说明**: 内部调用 `_beam_rebar()` / `_column_rebar()` / `_slab_rebar()` / `_wall_rebar()` / `_foundation_rebar()`

#### FUNC-012: `calculate_earthwork_full(data)`
- **模块**: 02-quantity.md §2.1.5
- **意图**: quantity
- **参数**: `data` (dict) — `{excavation_type: 'trench'/'pit'/'general', length, width, depth, slope_coeff, work_space, soil_class}`
- **返回**: `dict` — `{volume, slope_coeff, work_space, backfill, export, code}`
- **依据**: GB 50854-2013 附录A
- **说明**: 放坡系数表内置(人工/机械)

#### FUNC-013: `earthwork_grid_method(points, design_elev, grid_size)`
- **模块**: 02-quantity.md §2.1.6
- **意图**: quantity
- **参数**: `points` (list) — 测点`[(x, y, natural_elev), ...]`; `design_elev` (float) — 设计标高; `grid_size` (float) — 方格网边长
- **返回**: `dict` — `{cut_volume, fill_volume, zero_line[], grid_results[]}`
- **说明**: 方格网法八公式处理零线穿越

#### FUNC-014: `calculate_waterproof(data)`
- **模块**: 02-quantity.md §2.1.7
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'roof'/'basement'/'toilet', area, extra_layers, laps}`
- **返回**: `dict` — `{area, extra_area, total_area, code}`

#### FUNC-015: `calculate_insulation(data)`
- **模块**: 02-quantity.md §2.1.8
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'EPS'/'XPS'/'rockwool', area, thickness}`
- **返回**: `dict` — `{area, volume, code}`

#### FUNC-016: `calculate_decoration(data)`
- **模块**: 02-quantity.md §2.1.9
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'plaster'/'paint'/'tile'/'stone', surface_type: 'wall'/'ceiling'/'floor', area, deductions[]}`
- **返回**: `dict` — `{net_area, deduction_area, code}`

#### FUNC-017: `calculate_doors_windows(data)`
- **模块**: 02-quantity.md §2.1.10
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'door'/'window', width, height, count, material}`
- **返回**: `dict` — `{area, perimeter, count, code}`

#### FUNC-018: `calculate_roof(data)`
- **模块**: 02-quantity.md §2.1.11
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'flat'/'sloped', area, slope_angle, layers[]}`
- **返回**: `dict` — `{area, insulation_volume, waterproof_area, code}`

#### FUNC-019: `calculate_municipal_full(data)`
- **模块**: 02-quantity.md §2.2
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'pipe'/'road'/'bridge', alignment, sections[], ...}`
- **返回**: `dict` — `{pipe_length, trench_volume, backfill, road_area, code}`

#### FUNC-020: `calculate_highway_full(alignment, cross_sections, params)`
- **模块**: 02-quantity.md §2.3
- **意图**: quantity
- **参数**: `alignment` (dict) — 路线数据; `cross_sections` (list) — 断面数据; `params` (dict) — 参数
- **返回**: `dict` — `{subgrade_volume, base_volume, surface_volume, drainage, code}`
- **依据**: JTG 3820-2018

#### FUNC-021: `calculate_curtain_wall_full(data)`
- **模块**: 02-quantity.md §2.4
- **意图**: quantity
- **参数**: `data` (dict) — `{type: 'glass'/'stone'/'metal', width, height, area, panel_size}`
- **返回**: `dict` — `{panel_area, frame_length, glass_weight, sealant_length, code}`
- **依据**: JGJ 102-2003

#### FUNC-022: `calculate_steel_full(components)`
- **模块**: 02-quantity.md §2.5
- **意图**: quantity
- **参数**: `components` (list) — `[{type, section, length, count, plate_thickness}]`
- **返回**: `dict` — `{total_weight_kg, bolts[], paint_area, fireproof_area, code}`
- **依据**: GB 50205-2020

#### FUNC-023: `calculate_tunnel_full(data)`
- **模块**: 02-quantity.md §2.6
- **意图**: quantity
- **参数**: `data` (dict) — `{type, cross_section, length, lining_thickness, rock_class}`
- **返回**: `dict` — `{excavation_volume, lining_volume, waterproof_area, anchor_count, shotcrete_volume, code}`
- **依据**: JTG 3660-2020

---

### 14.3 BIM建模函数 (BIM)

#### FUNC-024: `create_bim_model_from_cad(cad_data, project_info)`
- **模块**: 03-bim.md §3.1
- **意图**: bim
- **参数**: `cad_data` — CAD解析数据; `project_info` (dict) — `{name, ...}`
- **返回**: IfcOpenShell model对象 (IFC4)
- **依赖**: `ifcopenshell`

#### FUNC-025: `add_wall_to_bim(model, storey, wall_data)`
- **模块**: 03-bim.md §3.2
- **意图**: bim
- **参数**: `model` — IFC模型; `storey` — 楼层对象; `wall_data` (dict) — `{start, end, height, thickness, material}`
- **返回**: IfcWall实体

#### FUNC-026: `add_beam_to_bim(model, storey, beam_data)`
- **模块**: 03-bim.md §3.3
- **意图**: bim
- **参数**: `beam_data` (dict) — `{start, end, section_width, section_height}`
- **返回**: IfcBeam实体

#### FUNC-027: `add_column_to_bim(model, storey, column_data)`
- **模块**: 03-bim.md §3.4
- **意图**: bim
- **参数**: `column_data` (dict) — `{position, section_width, section_depth, height}`
- **返回**: IfcColumn实体

#### FUNC-028: `add_slab_to_bim(model, storey, slab_data)`
- **模块**: 03-bim.md §3.5
- **意图**: bim
- **参数**: `slab_data` (dict) — `{outline_points[], thickness}`
- **返回**: IfcSlab实体

#### FUNC-029: `add_foundation_to_bim(model, site, foundation_data)`
- **模块**: 03-bim.md §3.6
- **意图**: bim
- **参数**: `foundation_data` (dict) — `{type: 'isolated'/'strip'/'raft'/'pile', ...}`
- **返回**: IfcFooting实体

#### FUNC-030: `export_bim_model(model, output_path)`
- **模块**: 03-bim.md §3.7
- **意图**: bim
- **参数**: `model` — IFC模型; `output_path` (str) — 输出文件路径
- **返回**: str — 保存路径
- **说明**: 导出IFC4格式文件

#### FUNC-031: `clash_detection(model, tolerance)`
- **模块**: 03-bim.md §3.8
- **意图**: bim
- **参数**: `model` — IFC模型; `tolerance` (float, 默认0.01) — 碰撞容差(m)
- **返回**: `list[dict]` — `[{element1, element2, type, location}]`
- **说明**: 自动排除正常连接(梁-柱、墙-板等)

#### FUNC-032: `validate_bim_model(model)`
- **模块**: 03-bim.md §3.9
- **意图**: bim
- **参数**: `model` — IFC模型
- **返回**: `dict` — `{is_valid, stats{walls, columns, beams, slabs, foundations}, issues[]}`

#### FUNC-033: `add_4d_schedule(model, element, start_date, end_date)`
- **模块**: 03-bim.md §3.10
- **意图**: bim
- **参数**: `element` — IFC实体; `start_date` (str) — 'YYYY-MM-DD'; `end_date` (str)
- **返回**: IfcTask实体

#### FUNC-034: `add_5d_cost(model, element, cost_data)`
- **模块**: 03-bim.md §3.11
- **意图**: bim
- **参数**: `cost_data` (dict) — `{amount, currency, item_code, description}`
- **返回**: IfcCostItem实体

#### FUNC-035: `set_lod_level(model, element, lod_level)`
- **模块**: 03-bim.md §3.12
- **意图**: bim
- **参数**: `lod_level` (int) — 100/200/300/350/400/500
- **返回**: 更新后的实体
- **说明**: LOD 100=概念 → 500=竣工

#### FUNC-036: `add_pipe_to_bim(model, alignment, pipe_data)`
- **模块**: 03-bim.md §3.13
- **意图**: bim
- **参数**: `alignment` — 管线走向; `pipe_data` (dict) — `{diameter, material, start, end}`
- **返回**: IfcPipeSegment实体

#### FUNC-037: `add_road_alignment_to_bim(model, alignment_data)`
- **模块**: 03-bim.md §3.14
- **意图**: bim
- **参数**: `alignment_data` (dict) — `{horizontal_curve[], vertical_curve[], stations[]}`
- **返回**: IfcAlignment实体

#### FUNC-038: `add_tunnel_to_bim(model, tunnel_data)`
- **模块**: 03-bim.md §3.15
- **意图**: bim
- **参数**: `tunnel_data` (dict) — `{cross_section, alignment, lining_thickness}`
- **返回**: IfcTunnel实体

#### FUNC-039: `add_curtain_wall_to_bim(model, building_storey, cw_data)`
- **模块**: 03-bim.md §3.16
- **意图**: bim
- **参数**: `cw_data` (dict) — `{type: 'glass'/'stone'/'metal', panel_size, frame_section}`
- **返回**: IfcCurtainWall实体

---

### 14.4 工程造价计价函数 (PRICING)

#### FUNC-040: `calculate_composite_unit_price(labor_days, labor_rate, materials, machinery, mgmt_rate, profit_rate, risk_rate)`
- **模块**: 09-pricing.md §9.2
- **意图**: pricing
- **参数**:
  - `labor_days` (float) — 工日消耗量
  - `labor_rate` (float) — 人工单价(元/工日)
  - `materials` (list) — `[(name, consumption, unit_price), ...]`
  - `machinery` (list) — `[(name, shifts, shift_price), ...]`
  - `mgmt_rate` (float, 默认0.15) — 管理费费率
  - `profit_rate` (float, 默认0.08) — 利润率
  - `risk_rate` (float, 默认0.02) — 风险费率
- **返回**: `dict` — `{labor_cost, material_cost, machinery_cost, management_cost, profit, risk_cost, composite_unit_price, analysis}`
- **依据**: GB 50500-2013 §3.0.5

#### FUNC-041: `calculate_measure_cost(project_cost, project_type, area)`
- **模块**: 09-pricing.md §9.6
- **意图**: pricing
- **参数**: `project_cost` (float) — 分部分项工程费; `project_type` (str) — 'building'/'municipal'/'highway'; `area` (float) — 建筑面积
- **返回**: `dict` — `{安全文明施工费, 夜间施工增加费, 二次搬运费, 冬雨季施工增加费, 大型机械进出场费, 脚手架费, 模板费, 措施费合计}`
- **依据**: GB 50500-2013 §3.0.6

#### FUNC-042: `calculate_regulation_and_tax(sub_project_cost, measure_cost, other_cost, tax_method)`
- **模块**: 09-pricing.md §9.7
- **意图**: pricing
- **参数**: `sub_project_cost` (float); `measure_cost` (float); `other_cost` (float, 默认0); `tax_method` (str) — 'general'(9%) / 'simple'(3%)
- **返回**: `dict` — `{规费{社保费, 住房公积金, 工程排污费, 规费合计}, 税金{计税方法, 税率, 税前造价, 税金}, 工程总造价}`
- **依据**: GB 50500-2013 §3.0.7, 财税〔2018〕32号

#### FUNC-043: `generate_bid_document(quantities, project_info, output_path)`
- **模块**: 09-pricing.md §9.8
- **意图**: pricing
- **参数**:
  - `quantities` (list) — `[(code, name, unit, qty, unit_price), ...]`
  - `project_info` (dict) — `{name, client, contractor, date, type, area}`
  - `output_path` (str) — Excel输出路径
- **返回**: str — 保存路径
- **依赖**: `openpyxl`
- **说明**: 生成封面+分部分项清单+措施项目+规费税金+费用汇总

#### FUNC-044: `calculate_material_price_adjustment(contract_prices, current_prices, quantities, adjustment_threshold)`
- **模块**: 09-pricing.md §9.9
- **意图**: pricing
- **参数**: `contract_prices` (dict) — 合同单价; `current_prices` (dict) — 现行单价; `quantities` (dict) — 消耗量; `adjustment_threshold` (float, 默认0.05) — 调差阈值±5%
- **返回**: `dict` — `{调整明细[], 价差合计, 调整材料数}`

---

### 14.5 施工安全计算函数 (SAFETY)

#### FUNC-045: `check_scaffold_stability(height, step, span, layers, load_per_layer, wall_type)`
- **模块**: 10-safety.md §10.1.1
- **意图**: safety
- **参数**:
  - `height` (float) — 脚手架高度(m)
  - `step` (float, 默认1.8) — 步距(m)
  - `span` (float, 默认1.5) — 立杆纵距(m)
  - `layers` (int, 默认2) — 同时施工层数
  - `load_per_layer` (float, 默认3.0) — 每层施工荷载(kN/m²)
  - `wall_type` (str) — 'two'(两步三跨) / 'three'(三步三跨)
- **返回**: `dict` — `{长细比λ, 稳定系数φ, 计算长度l0, 结构自重NG1k, 构配件自重NG2k, 施工荷载NQk, 立杆轴向力N, 截面应力σ, 强度设计值f, 应力比σ/f, 是否安全, 建议}`
- **依据**: JGJ 130-2011 §5.1.5~5.1.9
- **示例**:
```python
result = check_scaffold_stability(height=50, step=1.8, span=1.5)
# result['是否安全'] → '✓ 满足'
# result['应力比σ/f'] → '0.723'
```

#### FUNC-046: `check_wall_connector(wind_pressure, span, vertical_step, horizontal_step)`
- **模块**: 10-safety.md §10.1.2
- **意图**: safety
- **参数**: `wind_pressure` (float) — 风压标准值(kN/m²); `vertical_step` (float, 默认3.6); `horizontal_step` (float, 默认4.5)
- **返回**: `dict` — `{连墙件轴向力Nl, 扣件抗滑力Rc, 是否安全, 建议}`
- **依据**: JGJ 130-2011 §5.1.12

#### FUNC-047: `check_formwork_support(slab_thickness, concrete_unit_weight, span, step, construction_load, wall_type)`
- **模块**: 10-safety.md §10.2
- **意图**: safety
- **参数**: `slab_thickness` (float) — 板厚(mm); `span` (float, 默认1.2) — 立杆纵距(m); `step` (float, 默认1.2) — 步距(m)
- **返回**: `dict` — `{板厚, 混凝土自重, 总恒载, 施工荷载, 立杆轴向力, 长细比λ, 稳定系数φ, 截面应力σ, 应力比, 是否安全, 建议}`
- **依据**: JGJ 162-2014 §6.2.4

#### FUNC-048: `check_deep_excavation(excavation_depth, soil_gamma, soil_phi, soil_c, surcharge, water_table)`
- **模块**: 10-safety.md §10.3
- **意图**: safety
- **参数**:
  - `excavation_depth` (float) — 开挖深度(m)
  - `soil_gamma` (float, 默认18.0) — 土体重度(kN/m³)
  - `soil_phi` (float, 默认20.0) — 内摩擦角(°)
  - `soil_c` (float, 默认15.0) — 内聚力(kPa)
  - `surcharge` (float, 默认20.0) — 地面超载(kPa)
- **返回**: `dict` — `{基坑等级, 开挖深度, 主动土压力系数Ka, 被动土压力系数Kp, 坑底主动土压力, 总主动土压力Pa, 最小嵌固深度, 桩/墙总长度, 嵌固比, 安全系数, 建议支护形式}`
- **依据**: JGJ 120-2012
- **说明**: 自动推荐支护形式(放坡/土钉墙/排桩/地连墙)

#### FUNC-049: `check_tower_crane_foundation(crane_model, tipping_moment, vertical_load, base_size, base_height, soil_bearing)`
- **模块**: 10-safety.md §10.4
- **意图**: safety
- **参数**: `tipping_moment` (float) — 倾覆力矩(kN·m); `vertical_load` (float) — 垂直力(kN); `base_size` (float, 默认5.0) — 基础边长(m); `base_height` (float, 默认1.2) — 基础高度(m); `soil_bearing` (float, 默认180) — 地基承载力(kPa)
- **返回**: `dict` — `{塔吊型号, 倾覆力矩, 基础自重, 偏心距e, 基底最大应力, 基底最小应力, 修正地基承载力, 抗倾覆安全系数, 地基承载力验算, 偏心距验算, 抗倾覆验算, 综合判断}`
- **依据**: JGJ/T 30122-2014

#### FUNC-050: `check_edge_protection(floor_height, slab_thickness, wind_pressure)`
- **模块**: 10-safety.md §10.5
- **意图**: safety
- **参数**: `floor_height` (float) — 楼层高度(m); `slab_thickness` (float) — 板厚(mm); `wind_pressure` (float, 默认0.5) — 基本风压(kN/m²)
- **返回**: `dict` — `{栏杆高度, 立杆间距, 水平荷载, 截面应力σ, 应力比, 是否安全}`
- **依据**: JGJ 80-2016

#### FUNC-051: `check_temporary_power(total_power, voltage, power_factor, cable_length, conductor)`
- **模块**: 10-safety.md §10.6
- **意图**: safety
- **参数**: `total_power` (float) — 总用电功率(kW); `voltage` (int, 默认380); `power_factor` (float, 默认0.8); `cable_length` (float, 默认100) — 电缆长度(m); `conductor` (str, 默认'copper') — 'copper'/'aluminum'
- **返回**: `dict` — `{总功率, 计算电流, 经济截面, 选择截面, 电压降, 电压降限值, 变压器容量, 建议变压器, 电压降验算}`
- **依据**: JGJ 46-2024

---

### 14.6 碳排放与绿色建筑函数 (CARBON)

#### FUNC-052: `calculate_building_carbon_emission(materials, transport_distance, transport_mode, electricity_kwh, diesel_kg, project_type, grid_region)`
- **模块**: 11-carbon.md §11.1
- **意图**: carbon
- **参数**:
  - `materials` (dict) — `{材料名: 消耗量}` (支持21种材料)
  - `transport_distance` (float, 默认50) — 运输距离(km)
  - `transport_mode` (str, 默认'truck_diesel') — 运输方式
  - `electricity_kwh` (float, 默认0) — 施工用电(kWh)
  - `diesel_kg` (float, 默认0) — 施工柴油(kg)
  - `grid_region` (str, 默认'national') — 电网区域
- **返回**: `dict` — `{建材生产碳排放{碳排放, 占比, 明细}, 运输碳排放{碳排放, 占比}, 施工碳排放{碳排放, 占比}, 施工阶段碳排放合计}`
- **依据**: GB/T 51366-2019

#### FUNC-053: `calculate_assembly_rate(prefabricated_elements, total_elements, project_area)`
- **模块**: 11-carbon.md §11.2
- **意图**: carbon
- **参数**: `prefabricated_elements` (dict) — `{columns, beams, walls, slabs}` 预制体积; `total_elements` (dict) — 全部体积
- **返回**: `dict` — `{柱装配率, 梁装配率, 墙装配率, 板装配率, 综合装配率, 装配等级}`
- **依据**: GB/T 51231-2016

#### FUNC-054: `evaluate_green_building(project_info, scores)`
- **模块**: 11-carbon.md §11.3
- **意图**: carbon
- **参数**: `scores` (dict) — `{安全耐久, 健康舒适, 生活便利, 资源节约, 环境宜居, 提高与创新}` 各项满分100
- **返回**: `dict` — `{评价指标, 加分项得分, 总得分, 绿色建筑等级, 是否全部达标}`
- **依据**: GB/T 50378-2019

#### FUNC-055: `calculate_building_energy(area, climate_zone, building_type, heating_days, cooling_days, u_walls, u_roof, u_windows, window_wall_ratio, ac_cop)`
- **模块**: 11-carbon.md §11.4
- **意图**: carbon
- **参数**: `area` (float) — 建筑面积(m²); `climate_zone` (str) — 气候区; `building_type` (str) — 'residential'/'office'/'commercial'; `u_walls/u_roof/u_windows` (float) — 传热系数
- **返回**: `dict` — `{采暖能耗, 空调能耗, 照明能耗, 设备能耗, 总能耗, 单位面积能耗, 年运行碳排放, 节能评价}`
- **依据**: GB 50189-2015, JGJ 26-2018

---

### 14.7 施工组织与进度函数 (SCHEDULE)

#### FUNC-056: `build_cpm_network(tasks)`
- **模块**: 12-schedule.md §12.1
- **意图**: schedule
- **参数**: `tasks` (list) — `[(task_id, name, duration_days, predecessors: list), ...]`
- **返回**: `dict` — `{tasks{id: {name, duration, ES, EF, LS, LF, TF, FF, is_critical}}, project_duration, critical_path[]}`
- **说明**: CPM关键路径法，自动计算6个时间参数

#### FUNC-057: `generate_gantt_chart(cpm_result, output_path, start_date)`
- **模块**: 12-schedule.md §12.2
- **意图**: schedule
- **参数**: `cpm_result` (dict) — FUNC-056返回值; `output_path` (str); `start_date` (str, 默认'2026-01-01')
- **返回**: str — 图片保存路径
- **依赖**: `matplotlib`
- **说明**: 关键路径红色标注，非关键蓝色

#### FUNC-058: `calculate_resource_curve(cpm_result, resources, resource_type)`
- **模块**: 12-schedule.md §12.3
- **意图**: schedule
- **参数**: `resources` (dict) — `{task_id: (workers, cost_per_day)}`; `resource_type` (str) — 'workers'/'cost'
- **返回**: `dict` — `{daily_resource[], peak_value, peak_day, average, imbalance_factor, duration, 评价}`

#### FUNC-059: `optimize_resource_leveling(cpm_result, resources, max_iterations)`
- **模块**: 12-schedule.md §12.4
- **意图**: schedule
- **参数**: `max_iterations` (int, 默认100)
- **返回**: `dict` — `{优化前峰值, 优化后峰值, 优化前不均衡系数, 优化后不均衡系数, 改善率, 优化后日程, 评价}`

#### FUNC-060: `get_standard_sequence(project_type)`
- **模块**: 12-schedule.md §12.5
- **意图**: schedule
- **参数**: `project_type` (str) — 'building'(20道工序) / 'highway'(15道) / 'tunnel'(14道)
- **返回**: `list[tuple]` — `[(task_id, name, duration, predecessors), ...]`

#### FUNC-061: `track_schedule_progress(cpm_result, actual_progress, current_day)`
- **模块**: 12-schedule.md §12.6
- **意图**: schedule
- **参数**: `actual_progress` (dict) — `{task_id: 完成百分比(0~1)}`; `current_day` (int) — 当前天数
- **返回**: `dict` — `{当前日期, 计划工期, PV, EV, AC, SV, CV, SPI, CPI, 预测完工工期, 剩余工期, 进度状态, 建议}`
- **说明**: 挣值法(EVM)，SPI<1滞后，CPI<1超支

---

### 14.8 Excel计算表生成函数 (EXCEL)

#### FUNC-062: `generate_concrete_quantity_sheet(wb, project_name, data)`
- **模块**: 13-excel.md §13.2
- **意图**: excel
- **参数**: `wb` — openpyxl Workbook对象; `data` (list, 可选) — 预填数据
- **返回**: str — Sheet名称
- **说明**: 黄色=输入项, 绿色=公式自动计算, 含合计行

#### FUNC-063: `generate_rebar_quantity_sheet(wb, project_name, data)`
- **模块**: 13-excel.md §13.3
- **意图**: excel
- **参数**: 同FUNC-062
- **返回**: str — Sheet名称
- **说明**: 内置VLOOKUP理论重量查表(Φ6~Φ32)

#### FUNC-064: `generate_quantity_summary_sheet(wb, project_name)`
- **模块**: 13-excel.md §13.4
- **意图**: excel
- **参数**: `wb` — Workbook对象
- **返回**: str — Sheet名称
- **说明**: 六大专业分区，自动小计

#### FUNC-065: `generate_cost_summary_sheet(wb, project_name)`
- **模块**: 13-excel.md §13.5
- **意图**: excel
- **参数**: `wb` — Workbook对象
- **返回**: str — Sheet名称
- **说明**: 税率联动，修改分部分项工程费后全部费用自动更新

#### FUNC-066: `generate_full_project_workbook(project_name, output_path, sheets)`
- **模块**: 13-excel.md §13.6
- **意图**: excel
- **参数**: `output_path` (str) — 输出路径; `sheets` (list, 可选) — `['concrete', 'rebar', 'summary', 'cost']`
- **返回**: str — 保存路径
- **依赖**: `openpyxl`
- **说明**: 一键生成封面+目录+多Sheet完整工作簿

#### FUNC-067: `add_conditional_formatting(ws, cell_range)`
- **模块**: 13-excel.md §13.7
- **意图**: excel
- **参数**: `ws` — Worksheet对象; `cell_range` (str) — 如'G5:G20'
- **说明**: 负值红色加粗，正值绿色

---

### 14.9 实用工具函数 (UTILITIES)

#### FUNC-068: `coordinate_transform(x, y, z, from_system, to_system)`
- **模块**: 06-utilities.md §6.1
- **意图**: utilities
- **参数**: `from_system`/`to_system` (str) — 'WGS84'/'CGCS2000'/'BJ54'/'XA80'
- **返回**: `tuple` — (x, y, z)

#### FUNC-069: `gauss_kruger_to_lonlat(X, Y, central_meridian)`
- **模块**: 06-utilities.md §6.1
- **意图**: utilities
- **参数**: `X`/`Y` (float) — 高斯坐标; `central_meridian` (float, 默认114.0) — 中央子午线经度
- **返回**: `tuple` — (lon, lat)

#### FUNC-070: `convert_unit(value, from_unit, to_unit)`
- **模块**: 06-utilities.md §6.2
- **意图**: utilities
- **参数**: `from_unit`/`to_unit` (str) — 如'mm'/'m'/'km'/'kg'/'t'/'MPa'/'kPa'
- **返回**: float — 转换后的值

#### FUNC-071: `export_quantity_to_excel(quantities, output_path)`
- **模块**: 06-utilities.md §6.3
- **意图**: utilities
- **参数**: `quantities` (dict) — `{name: {code, unit, value, remark}}`; `output_path` (str)
- **返回**: str — 保存路径

#### FUNC-072: `batch_process_cad(input_dir, output_dir)`
- **模块**: 06-utilities.md §6.4
- **意图**: utilities
- **参数**: `input_dir` (str) — 输入目录; `output_dir` (str) — 输出目录
- **返回**: `list[dict]` — `[{file, status, layers, entities} or {file, status, error}]`

---

### 14.10 工作流函数 (WORKFLOWS)

#### FUNC-073: `full_workflow_building(cad_path, output_ifc_path, output_excel_path)`
- **模块**: 05-workflows.md §5.1
- **意图**: drawing+quantity+bim (组合)
- **参数**: CAD文件路径 + IFC输出路径 + Excel输出路径
- **返回**: `dict` — `{quantities, bim_model, excel_report, clashes, validation}`
- **说明**: CAD解析→构件提取→算量→Excel导出→BIM建模→碰撞检测→模型验证→IFC导出

#### FUNC-074: `full_workflow_highway(alignment_data, cross_sections, output_ifc_path)`
- **模块**: 05-workflows.md §5.2
- **意图**: quantity+bim (组合)
- **返回**: `dict` — 路基/基层/面层工程量 + IFC模型

#### FUNC-075: `full_workflow_tunnel(geological_data, tunnel_design, output_ifc_path)`
- **模块**: 05-workflows.md §5.3
- **意图**: quantity+bim (组合)
- **返回**: `dict` — 隧道工程量 + IFC模型

---

### 14.11 函数快速索引

| 意图 | 函数数 | 函数列表 |
|------|:---:|---------|
| drawing | 6 | FUNC-001~006 |
| quantity | 17 | FUNC-007~023 |
| bim | 16 | FUNC-024~039 |
| pricing | 5 | FUNC-040~044 |
| safety | 7 | FUNC-045~051 |
| carbon | 4 | FUNC-052~055 |
| schedule | 6 | FUNC-056~061 |
| excel | 6 | FUNC-062~067 |
| utilities | 5 | FUNC-068~072 |
| workflows | 3 | FUNC-073~075 |
| **合计** | **75** | |

---

<!-- 自动生成于 2026-07-13 00:09:45 | 模块数: 15 | 文件大小: 186,609 bytes -->
