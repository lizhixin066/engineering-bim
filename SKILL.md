---
name: "engineering-bim"
description: "大型工程综合技能：支持工程识图、工程量计算、CAD转BIM模型。覆盖土建工程、市政工程、公路工程、幕墙工程、钢结构工程、隧道工程六大专业。当用户需要识图、算量、BIM建模或涉及上述工程专业时调用。"
---

# 大型工程综合技能 (Engineering & BIM)

> 模块化框架版本 | 更新时间: 2026-07-12
> 编辑任意 `modules/*.md` 后运行 `python assemble.py` 重新生成 SKILL.md

本技能为大型工程综合工具，覆盖工程识图、工程量计算、CAD转BIM模型三大核心能力，支持土建、市政、公路、幕墙、钢结构、隧道六大工程专业，并提供碰撞检测、4D/5D BIM、图纸对比等高级功能。

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

## 八、使用说明

### 何时调用本技能
当用户提及以下关键词或场景时，应立即调用本技能：
- **工程识图**: "识图", "读取CAD", "解析图纸", "看图", "读图", "提取尺寸", "图纸对比", "图层"
- **工程量计算**: "算量", "工程量", "混凝土量", "钢筋量", "土方量", "清单计价", "模板", "脚手架"
- **BIM建模**: "BIM", "IFC", "三维模型", "Revit模型", "CAD转BIM", "翻模", "碰撞检测", "4D", "5D"
- **专业工程**: "土建", "市政", "公路", "幕墙", "钢结构", "隧道", "桥梁", "道路", "管道", "基础"

### 处理原则
1. **识图优先**: 先读取并解析图纸，确认图层、图块和构件信息
2. **算量准确**: 严格按照国家规范公式计算，标注计算依据
3. **BIM规范**: 使用IFC4标准，确保模型可导入Revit、Tekla等主流软件
4. **专业区分**: 不同专业使用不同的算量规则和BIM构件类型
5. **碰撞必检**: BIM模型生成后务必进行碰撞检测
6. **输出清晰**: 工程量清单使用表格形式，BIM模型标注构件属性

<!-- 自动生成于 2026-07-12 23:34:40 | 模块数: 9 | 文件大小: 84,424 bytes -->
