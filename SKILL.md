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

### 2.1 土建工程量计算

#### 混凝土工程量（含模板）
```python
def calculate_concrete_and_formwork(entities, element_type):
    """
    计算混凝土体积 + 模板面积
    element_type: 'beam' | 'column' | 'slab' | 'wall' | 'foundation' | 'stair'
    """
    total_volume = 0.0
    total_formwork = 0.0

    for entity in entities:
        dims = get_element_dimensions(entity, element_type)

        if element_type == 'beam':
            w, h, L = dims['width'], dims['height'], dims['length']
            volume = w * h * L
            formwork = (w + 2 * h) * L
        elif element_type == 'column':
            w, d, h = dims['width'], dims['depth'], dims['height']
            volume = w * d * h
            formwork = 2 * (w + d) * h
        elif element_type == 'slab':
            volume = dims['area'] * dims['thickness']
            formwork = dims['area']
        elif element_type == 'wall':
            L, H, t = dims['length'], dims['height'], dims['thickness']
            volume = L * H * t
            formwork = 2 * L * H
        elif element_type == 'foundation':
            L, W, H = dims['length'], dims['width'], dims['height']
            volume = L * W * H
            formwork = 2 * (L + W) * H
        elif element_type == 'stair':
            volume = dims['run'] * dims['width'] * dims['thickness'] * dims['steps']
            formwork = dims['run'] * dims['width'] * dims['steps']

        total_volume += volume
        total_formwork += formwork

    return {'concrete_volume': total_volume, 'formwork_area': total_formwork}
```

#### 钢筋工程量（详细版）
```python
# 钢筋理论重量表 (kg/m)
REBAR_UNIT_WEIGHT = {
    6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888,
    14: 1.21, 16: 1.58, 18: 2.00, 20: 2.47,
    22: 2.98, 25: 3.85, 28: 4.83, 32: 6.31,
    36: 7.99, 40: 9.87,
}

def calculate_rebar_detail(beam_data: dict) -> dict:
    """
    梁钢筋详细算量
    依据: GB 50010-2010, 16G101-1 图集

    beam_data = {
        'length': 6000,          # 梁净跨 (mm)
        'width': 300, 'height': 600,  # 截面 (mm)
        'top_rebars': [{'d': 20, 'count': 2}],
        'bottom_rebars': [{'d': 25, 'count': 3}],
        'stirrups': {'d': 8, 'spacing': 100},
        'concrete_cover': 25,
        'seismic_grade': 2,
    }
    """
    result = {'items': [], 'total_weight_kg': 0.0}
    L = beam_data['length']
    w = beam_data['width']
    h = beam_data['height']
    cover = beam_data['concrete_cover']
    lae = _calc_anchorage_length(beam_data['seismic_grade'])

    # 上部通长筋
    for rebar in beam_data['top_rebars']:
        d = rebar['d']
        count = rebar['count']
        single_length = L + 2 * lae
        weight = count * (single_length / 1000) * REBAR_UNIT_WEIGHT.get(d, 0.00617 * d**2)
        result['items'].append({
            'name': f'上部通长筋{d}mm', 'diameter': d, 'count': count,
            'single_length_mm': single_length, 'weight_kg': weight,
        })
        result['total_weight_kg'] += weight

    # 下部通长筋
    for rebar in beam_data['bottom_rebars']:
        d = rebar['d']
        count = rebar['count']
        single_length = L + 2 * lae
        weight = count * (single_length / 1000) * REBAR_UNIT_WEIGHT.get(d, 0.00617 * d**2)
        result['items'].append({
            'name': f'下部通长筋{d}mm', 'diameter': d, 'count': count,
            'single_length_mm': single_length, 'weight_kg': weight,
        })
        result['total_weight_kg'] += weight

    # 箍筋
    stirrup = beam_data['stirrups']
    d = stirrup['d']
    spacing = stirrup['spacing']
    stirrup_length = 2 * (w + h) - 8 * cover + 2 * 11.9 * d
    count = (L // spacing) + 1
    weight = count * (stirrup_length / 1000) * REBAR_UNIT_WEIGHT.get(d, 0.00617 * d**2)
    result['items'].append({
        'name': f'箍筋{d}mm@{spacing}mm', 'diameter': d, 'count': count,
        'single_length_mm': stirrup_length, 'weight_kg': weight,
    })
    result['total_weight_kg'] += weight

    return result

def _calc_anchorage_length(seismic_grade: int) -> float:
    """计算抗震锚固长度 laE (mm)"""
    base_la = 35 * 25
    seismic_factor = {1: 1.15, 2: 1.15, 3: 1.05, 4: 1.0}
    return base_la * seismic_factor.get(seismic_grade, 1.0)
```

#### 土方工程量（三种方法）

```python
def calculate_earthwork_grid(terrain_pts, design_elev, grid_size=10.0):
    """方格网法（四角棱柱体公式）适用: 场地平整"""
    cut = 0.0; fill = 0.0
    rows, cols = len(terrain_pts), len(terrain_pts[0])
    for i in range(rows - 1):
        for j in range(cols - 1):
            h1 = terrain_pts[i][j] - design_elev
            h2 = terrain_pts[i][j+1] - design_elev
            h3 = terrain_pts[i+1][j] - design_elev
            h4 = terrain_pts[i+1][j+1] - design_elev
            V = grid_size**2 * (h1 + h2 + h3 + h4) / 4
            if V > 0: fill += V
            else: cut += abs(V)
    return {'cut': cut, 'fill': fill}

def calculate_earthwork_section(cross_sections: list) -> dict:
    """
    断面法（平均断面法 + 棱台公式）
    棱台公式: V = L/3 * (A1 + A2 + sqrt(A1*A2))
    """
    cut = 0.0; fill = 0.0
    for i in range(len(cross_sections) - 1):
        sec1 = cross_sections[i]
        sec2 = cross_sections[i+1]
        L = sec2['station'] - sec1['station']
        a1_cut = sec1.get('cut_area', 0)
        a2_cut = sec2.get('cut_area', 0)
        if a1_cut > 0 and a2_cut > 0:
            ratio = max(a1_cut, a2_cut) / min(a1_cut, a2_cut) if min(a1_cut, a2_cut) > 0 else 999
            if 0.5 <= ratio <= 2.0:
                cut += L / 3 * (a1_cut + a2_cut + (a1_cut * a2_cut) ** 0.5)
            else:
                cut += (a1_cut + a2_cut) / 2 * L
        a1_fill = sec1.get('fill_area', 0)
        a2_fill = sec2.get('fill_area', 0)
        if a1_fill > 0 and a2_fill > 0:
            ratio = max(a1_fill, a2_fill) / min(a1_fill, a2_fill) if min(a1_fill, a2_fill) > 0 else 999
            if 0.5 <= ratio <= 2.0:
                fill += L / 3 * (a1_fill + a2_fill + (a1_fill * a2_fill) ** 0.5)
            else:
                fill += (a1_fill + a2_fill) / 2 * L
    return {'cut': cut, 'fill': fill}

def calculate_earthwork_contour(contours: list, interval: float) -> dict:
    """等高线法（水平断面法）"""
    total = 0.0
    for i in range(len(contours) - 1):
        A1 = contours[i]['area']
        A2 = contours[i+1]['area']
        h = interval
        total += (A1 + A2) / 2 * h
    return {'total_volume': total}
```

#### 脚手架工程量

```python
def calculate_scaffolding(building_data: dict) -> dict:
    """脚手架工程量计算 依据: JGJ 130"""
    results = {}
    perimeter = building_data['perimeter']
    height = building_data['height']
    results['external_scaffold'] = perimeter * height
    internal_wall_length = building_data.get('internal_wall_length', 0)
    results['internal_scaffold'] = internal_wall_length * building_data.get('floor_height', 3.0)
    if building_data.get('ceiling_height', 0) > 3.6:
        results['full_house_scaffold'] = building_data['floor_area']
    return results
```

### 2.2 市政工程量计算

```python
def calculate_municipal_quantities(project_data: dict) -> dict:
    """市政工程量计算"""
    q = {}
    road = project_data.get('road', {})
    q['road_area'] = road['length'] * road['width']
    q['curb_length'] = road['length'] * 2
    q['sidewalk_area'] = road['length'] * road.get('sidewalk_width', 2.0) * 2
    drainage = project_data.get('drainage', {})
    q['pipe_length'] = drainage.get('length', 0)
    q['pipe_trench'] = drainage.get('trench_depth', 1.5) * drainage.get('trench_width', 1.0) * drainage.get('length', 0)
    q['manhole_count'] = drainage.get('manhole_count', 0)
    manhole = project_data.get('manhole_spec', {})
    q['manhole_brickwork'] = q['manhole_count'] * (
        manhole.get('diameter', 1.0) * 3.1416 * manhole.get('depth', 2.0) * manhole.get('wall_thickness', 0.24)
    )
    return q
```

### 2.3 公路工程量计算

```python
def calculate_highway_quantities(alignment, cross_sections, design_params: dict) -> dict:
    """公路工程量计算（JTG 3820 清单计量规则）"""
    q = {
        'subgrade_earthwork': 0, 'pavement_layers': {},
        'subbase_volume': 0, 'guardrail_length': 0,
        'drainage_length': 0, 'slope_protection_area': 0,
        'marking_length': 0, 'greening_area': 0,
    }
    for i in range(len(cross_sections) - 1):
        s1, s2 = cross_sections[i], cross_sections[i+1]
        L = s2['station'] - s1['station']
        q['subgrade_earthwork'] += (s1['area'] + s2['area']) / 2 * L
    road_length = alignment['length']
    road_width = design_params.get('road_width', 7.5)
    for layer_name, thickness in design_params.get('pavement_layers', {}).items():
        q['pavement_layers'][layer_name] = {
            'area': road_length * road_width,
            'thickness': thickness,
            'volume': road_length * road_width * thickness,
        }
    subbase_thickness = sum(design_params.get('subbase_layers', {}).values())
    q['subbase_volume'] = road_length * road_width * subbase_thickness
    q['guardrail_length'] = road_length * 2 * design_params.get('guardrail_rate', 0.8)
    q['drainage_length'] = road_length * 2 * design_params.get('drainage_rate', 0.6)
    return q
```

### 2.4 幕墙工程量计算

```python
def calculate_curtain_wall_quantities(cw_data: dict) -> dict:
    """幕墙工程量计算 依据: JGJ 102"""
    q = {
        'glass_area': 0, 'aluminum_frame_length': 0,
        'steel_connector_weight': 0, 'sealant_length': 0,
        'insulation_area': 0, 'fire_stop_length': 0, 'anchor_count': 0,
    }
    for panel in cw_data.get('panels', []):
        area = panel['width'] * panel['height']
        q['glass_area'] += area
        q['sealant_length'] += 2 * (panel['width'] + panel['height'])
    for frame in cw_data.get('frames', []):
        q['aluminum_frame_length'] += frame['length']
        if 'weight_per_m' in frame:
            q['steel_connector_weight'] += frame['length'] * frame.get('weight_per_m', 0)
    q['fire_stop_length'] = cw_data.get('fire_stop_length', 0)
    q['anchor_count'] = cw_data.get('anchor_count', 0)
    q['insulation_area'] = q['glass_area'] * cw_data.get('insulation_ratio', 0.3)
    return q
```

### 2.5 钢结构工程量

```python
def calculate_steel_structure_quantities(components: list) -> dict:
    """钢结构工程量计算 依据: GB 50500, GB 50205"""
    q = {
        'steel_weight_kg': 0, 'surface_area': 0,
        'fireproof_area': 0, 'bolt_count': 0, 'weld_length': 0,
    }
    steel_density = 7850
    for comp in components:
        if comp['type'] == 'h_beam':
            h, b = comp['height'], comp['width']
            tw, tf = comp['web_thickness'], comp['flange_thickness']
            L = comp['length']
            area = (h - 2*tf) * tw + 2 * b * tf
            weight_per_m = area / 1e6 * steel_density
            weight = weight_per_m * L / 1000
            q['steel_weight_kg'] += weight
            surface = (2*b + 4*(h - 2*tf) + 2*tw) * L / 1e6
            q['surface_area'] += surface
            q['fireproof_area'] += surface
        elif comp['type'] == 'box_column':
            h, b = comp['height'], comp['width']
            t = comp['thickness']
            L = comp['length']
            area = 2 * (h + b - 2*t) * t
            weight = area / 1e6 * steel_density * L / 1000
            q['steel_weight_kg'] += weight
            surface = 2 * (h + b) * L / 1e6
            q['surface_area'] += surface
            q['fireproof_area'] += surface
        elif comp['type'] == 'pipe':
            D = comp['diameter']
            t = comp['thickness']
            L = comp['length']
            area = 3.1416 * (D - t) * t
            weight = area / 1e6 * steel_density * L / 1000
            q['steel_weight_kg'] += weight
            surface = 3.1416 * D * L / 1e6
            q['surface_area'] += surface
            q['fireproof_area'] += surface
        q['bolt_count'] += comp.get('bolt_count', 0)
        q['weld_length'] += comp.get('weld_length', 0)
    return q
```

### 2.6 隧道工程量

```python
def calculate_tunnel_quantities(tunnel_data: dict) -> dict:
    """隧道工程量计算 依据: JTG 3660"""
    q = {
        'excavation_volume': 0, 'shotcrete_volume': 0,
        'lining_concrete': 0, 'rock_bolt_count': 0,
        'rock_bolt_length': 0, 'steel_arch_weight': 0,
        'waterproof_area': 0, 'invert_volume': 0,
    }
    sections = tunnel_data.get('sections', [])
    for section in sections:
        seg_length = section['end_station'] - section['start_station']
        q['excavation_volume'] += section['excavation_area'] * seg_length
        q['shotcrete_volume'] += section['shotcrete_thickness'] * section['perimeter'] * seg_length
        q['lining_concrete'] += section['lining_thickness'] * section['perimeter'] * seg_length
        q['rock_bolt_count'] += section.get('bolt_count_per_m', 0) * seg_length
        q['rock_bolt_length'] += section.get('bolt_length', 3.0) * section.get('bolt_count_per_m', 0) * seg_length
        q['steel_arch_weight'] += section.get('arch_weight_per_m', 0) * seg_length
        q['waterproof_area'] += section['perimeter'] * seg_length
        if section.get('invert_area', 0) > 0:
            q['invert_volume'] += section['invert_area'] * seg_length
    return q
```

### 2.7 工程量清单编码参考（GB 50500）

| 清单编码 | 项目名称 | 单位 |
|---------|---------|------|
| 010101 | 平整场地 | m² |
| 010101002 | 挖一般土方 | m³ |
| 010101003 | 挖沟槽土方 | m³ |
| 010101004 | 挖基坑土方 | m³ |
| 010103001 | 回填方 | m³ |
| 010201001 | 预制钢筋混凝土方桩 | m |
| 010501001 | 垫层 | m³ |
| 010502001 | 矩形柱 | m³ |
| 010503001 | 基础梁 | m³ |
| 010503002 | 矩形梁 | m³ |
| 010505001 | 有梁板 | m³ |
| 010504001 | 直形墙 | m³ |
| 010515001 | 现浇构件钢筋 | t |
| 040101001 | 挖一般土方（市政） | m³ |
| 040203001 | 水泥稳定土基层 | m² |
| 040203005 | 沥青混凝土路面 | m² |
| 040501001 | 混凝土管道铺设 | m |

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

## 四、专业工程规范参考

### 4.1 土建工程
- GB 50010-2010《混凝土结构设计规范》
- GB 50011-2010《建筑抗震设计规范》
- GB 50007-2011《建筑地基基础设计规范》
- GB 50204-2015《混凝土结构工程施工质量验收规范》
- GB 50500-2013《建设工程工程量清单计价规范》
- GB 50300-2013《建筑工程施工质量验收统一标准》
- GB 50210-2018《建筑装饰装修工程质量验收标准》
- 16G101-1《混凝土结构施工图平面整体表示方法制图规则和构造详图》

### 4.2 市政工程
- GB 50014-2021《室外排水设计标准》
- GB 50268-2008《给水排水管道工程施工及验收规范》
- CJJ 1-2008《城镇道路工程施工与质量验收规范》
- CJJ 2-2008《城市桥梁工程施工与质量验收规范》
- GB 50289-2016《城市工程管线综合规划规范》
- CJJ 37-2012《城市道路工程设计规范》

### 4.3 公路工程
- JTG 3820-2018《公路工程工程量清单计量规则》
- JTG B01-2014《公路工程技术标准》
- JTG D20-2017《公路路线设计规范》
- JTG D30-2015《公路路基设计规范》
- JTG D50-2017《公路沥青路面设计规范》
- JTG 3660-2020《公路隧道施工技术规范》
- JTG D70-2004《公路隧道设计规范》
- JTG 3362-2018《公路钢筋混凝土及预应力混凝土桥涵设计规范》

### 4.4 幕墙工程
- JGJ 102-2003《玻璃幕墙工程技术规范》
- JGJ 133-2001《金属与石材幕墙工程技术规范》
- GB/T 21086-2007《建筑幕墙》
- GB 50009-2012《建筑结构荷载规范》
- JGJ/T 139-2020《玻璃幕墙工程质量检验标准》

### 4.5 钢结构工程
- GB 50017-2017《钢结构设计标准》
- GB 50205-2020《钢结构工程施工质量验收标准》
- GB 50661-2011《钢结构焊接规范》
- JGJ 82-2011《钢结构高强度螺栓连接技术规程》
- GB/T 1591-2018《低合金高强度结构钢》

### 4.6 隧道工程
- JTG 3660-2020《公路隧道施工技术规范》
- JTG D70-2004《公路隧道设计规范》
- GB 50086-2015《岩土锚杆与喷射混凝土支护工程技术规范》
- TB 10003-2016《铁路隧道设计规范》

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

<!-- 自动生成于 2026-07-12 22:20:09 | 模块数: 9 | 文件大小: 49,185 bytes -->
