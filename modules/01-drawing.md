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