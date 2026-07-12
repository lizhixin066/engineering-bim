## 十五、图纸智能分析与自动算量 (Drawing-to-Quantity Pipeline)

> 从CAD图纸自动识别构件、提取尺寸、计算工程量的完整智能管线。
> 桥接 `parse_cad_drawing()` (§1) → `calculate_concrete_detail()` (§2) 的自动化链路。

---

### 15.1 图纸→工程量 全流程管线

```
CAD文件(.dxf/.dwg)
    │
    ▼
┌──────────────────────────┐
│ Step 1: 图纸解析          │  parse_cad_drawing()
│ → 原始图元(线/文字/标注)   │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Step 2: 图层分类          │  classify_layers()
│ → 构件类型分组            │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Step 3: 构件识别          │  extract_elements_from_drawing()
│ → 墙/柱/梁/板/基础几何体  │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Step 4: 尺寸提取          │  extract_dimensions_from_text()
│ → 截面尺寸/标高/板厚      │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Step 5: 钢筋信息提取      │  extract_rebar_info()
│ → 钢筋规格/间距/长度      │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Step 6: 自动算量          │  auto_quantity_from_drawing()
│ → 混凝土/模板/钢筋/土方   │
└──────────┬───────────────┘
           ▼
┌──────────────────────────┐
│ Step 7: 结果校核          │  audit_quantity_result()
│ → 图纸标注 vs 计算结果    │
└──────────────────────────┘
```

---

### 15.2 构件智能识别

#### 15.2.1 图层分类→构件类型映射

```python
# 图层关键字→构件类型 完整映射表
LAYER_ELEMENT_MAP = {
    # 柱
    'column': {
        'keywords': ['COLUMN', '柱', 'KZ-', 'GZ-', 'Z-', 'COL-', 'C-'],
        'subtypes': {
            'kz': ['KZ'],      # 框架柱
            'gz': ['GZ'],       # 构造柱
            'xz': ['XZ'],       # 悬挑柱
            'zz': ['ZZ'],       # 转角柱
        }
    },
    # 梁
    'beam': {
        'keywords': ['BEAM', '梁', 'KL-', 'LL-', 'WKL-', 'L-', 'BL-'],
        'subtypes': {
            'kl': ['KL'],       # 框架梁
            'll': ['LL'],       # 连系梁
            'wkl': ['WKL'],     # 屋面框架梁
            'jl': ['JL'],       # 基础梁
            'xl': ['XL'],       # 悬挑梁
        }
    },
    # 墙
    'wall': {
        'keywords': ['WALL', '墙', '墙体', 'WA-', 'W-', 'Q-', 'SQ-'],
        'subtypes': {
            'sq': ['SQ'],       # 剪力墙
            'q': ['Q'],         # 砌体墙
            'dq': ['DQ'],       # 挡土墙
        }
    },
    # 板
    'slab': {
        'keywords': ['SLAB', '板', 'B-', 'LB-', 'WB-', 'KB-'],
        'subtypes': {
            'lb': ['LB'],       # 楼板
            'wb': ['WB'],       # 屋面板
            'kb': ['KB'],       # 空心板
            'yt': ['YT'],       # 阳台板
        }
    },
    # 基础
    'foundation': {
        'keywords': ['FOUNDATION', '基础', 'JC-', 'CT-', 'ZJ-', 'DT-', 'J-'],
        'subtypes': {
            'ct': ['CT'],       # 独立基础
            'jt': ['JT'],       # 条形基础
            'fb': ['FB'],       # 筏板基础
            'zj': ['ZJ'],       # 桩基础
        }
    },
    # 门窗
    'opening': {
        'keywords': ['DOOR', 'WINDOW', '门', '窗', 'M-', 'C-', 'FM-', 'TC-'],
        'subtypes': {
            'door': ['M', 'DOOR', '门', 'FM'],
            'window': ['C', 'WINDOW', '窗', 'TC'],
        }
    },
    # 楼梯
    'stair': {
        'keywords': ['STAIR', '楼梯', 'LT-', 'ST-'],
        'subtypes': {}
    },
    # 轴网
    'axis': {
        'keywords': ['AXIS', '轴线', 'ZX-', 'AX-'],
        'subtypes': {}
    },
    # 标高
    'elevation': {
        'keywords': ['ELEVATION', '标高', 'BG-', 'EL-'],
        'subtypes': {}
    },
}


def classify_layers(layers: list) -> dict:
    """
    将图层名分类为构件类型
    输入: ['WALL', 'KZ-COLUMN', 'KL-BEAM', 'LB-SLAB', ...]
    输出: {'wall': ['WALL'], 'column': ['KZ-COLUMN'], 'beam': ['KL-BEAM'], ...}
    """
    result = {elem: [] for elem in LAYER_ELEMENT_MAP}
    result['other'] = []

    for layer in layers:
        upper = layer.upper()
        matched = False
        for elem_type, config in LAYER_ELEMENT_MAP.items():
            for kw in config['keywords']:
                if kw.upper() in upper:
                    result[elem_type].append(layer)
                    matched = True
                    break
            if matched:
                break
        if not matched:
            result['other'].append(layer)

    return result
```

#### 15.2.2 从图元中识别构件几何体

```python
def extract_elements_from_drawing(
    drawing_info: dict,
    floor_height: float = 3.0,
    slab_thickness: float = 0.12,
) -> dict:
    """
    从解析后的CAD图元中智能识别结构构件
    输入: parse_cad_drawing() 的返回值
    输出: 结构化构件数据(可直接传入算量函数)

    识别策略:
      - 柱: 闭合矩形多段线 / 图块参照(柱截面块)
      - 梁: 线段对(平行线) / 多段线(梁轮廓)
      - 墙: 平行线对 / 多段线(墙线)
      - 板: 闭合多段线围合区域
      - 门窗: 图块参照(门窗块) / 文字标注
    """
    entities = drawing_info['entities']
    layers = drawing_info.get('layers', [])
    layer_map = classify_layers(layers)

    elements = {
        'columns': [],
        'beams': [],
        'walls': [],
        'slabs': [],
        'foundations': [],
        'openings': [],    # 门窗洞口
        'stairs': [],
    }

    # === 柱识别 ===
    # 策略1: 从闭合多段线中找矩形(长宽比<2) → 柱截面
    column_layers = layer_map.get('column', [])
    for poly in entities['polylines']:
        if not poly['closed']:
            continue
        if not _layer_match(poly['layer'], column_layers):
            continue
        rect = _detect_rectangle(poly['points'])
        if rect and 0.2 < rect['width'] < 2.0 and 0.2 < rect['height'] < 2.0:
            elements['columns'].append({
                'id': f"COL_{len(elements['columns'])+1}",
                'position': rect['center'],
                'width': rect['width'],
                'depth': rect['height'],
                'height': floor_height,
                'layer': poly['layer'],
                'source': 'polyline',
            })

    # 策略2: 从文字标注中识别柱编号和截面
    for text in entities['texts']:
        col_info = _parse_column_label(text['content'])
        if col_info:
            col_info['position'] = text['position']
            col_info['height'] = floor_height
            col_info['source'] = 'text'
            elements['columns'].append(col_info)

    # 策略3: 从图块参照中识别柱(块名含KZ/GZ等)
    for insert in entities['inserts']:
        if _layer_match(insert['layer'], column_layers):
            block_name = insert['block_name'].upper()
            col_info = _parse_column_label(block_name)
            if col_info:
                col_info['position'] = insert['position']
                col_info['height'] = floor_height
                col_info['source'] = 'block'
                elements['columns'].append(col_info)

    # === 梁识别 ===
    # 策略1: 从文字标注中识别梁编号和截面
    beam_layers = layer_map.get('beam', [])
    beam_texts = {}  # 按位置聚类
    for text in entities['texts']:
        if not _layer_match(text['layer'], beam_layers):
            continue
        beam_info = _parse_beam_label(text['content'])
        if beam_info:
            beam_info['position'] = text['position']
            beam_texts[beam_info['id']] = beam_info

    # 策略2: 从线段中找梁线(平行线对)
    beam_lines = [l for l in entities['lines']
                  if _layer_match(l['layer'], beam_layers)]
    beam_pairs = _find_parallel_pairs(beam_lines, max_gap=0.5)
    for pair in beam_pairs:
        center_line = _line_center(pair['line1'], pair['line2'])
        gap = _line_distance(pair['line1'], pair['line2'])
        beam_id = f"KL_{len(elements['beams'])+1}"
        elements['beams'].append({
            'id': beam_id,
            'start': center_line['start'],
            'end': center_line['end'],
            'width': gap,
            'height': 0.5,  # 默认梁高,优先从文字标注获取
            'length': center_line['length'],
            'layer': pair['line1']['layer'],
            'source': 'parallel_lines',
        })

    # 用文字标注更新梁截面信息
    for beam in elements['beams']:
        nearest_text = _find_nearest_text(beam, list(beam_texts.values()), max_dist=2.0)
        if nearest_text:
            beam['id'] = nearest_text.get('id', beam['id'])
            beam['width'] = nearest_text.get('width', beam['width'])
            beam['height'] = nearest_text.get('height', beam['height'])

    # === 墙识别 ===
    wall_layers = layer_map.get('wall', [])
    wall_lines = [l for l in entities['lines']
                  if _layer_match(l['layer'], wall_layers)]
    wall_polys = [p for p in entities['polylines']
                  if _layer_match(p['layer'], wall_layers)]

    # 策略1: 平行线对识别墙
    wall_pairs = _find_parallel_pairs(wall_lines, max_gap=0.5)
    for pair in wall_pairs:
        center_line = _line_center(pair['line1'], pair['line2'])
        gap = _line_distance(pair['line1'], pair['line2'])
        elements['walls'].append({
            'id': f"Q_{len(elements['walls'])+1}",
            'start': center_line['start'],
            'end': center_line['end'],
            'length': center_line['length'],
            'thickness': gap if 0.1 < gap < 0.6 else 0.24,  # 默认240墙
            'height': floor_height,
            'source': 'parallel_lines',
        })

    # 策略2: 多段线识别墙
    for poly in wall_polys:
        if not poly['closed']:
            # 非闭合多段线 → 墙线
            pts = poly['points']
            for i in range(len(pts) - 1):
                length = _dist(pts[i], pts[i+1])
                elements['walls'].append({
                    'id': f"Q_{len(elements['walls'])+1}",
                    'start': pts[i],
                    'end': pts[i+1],
                    'length': length,
                    'thickness': 0.24,
                    'height': floor_height,
                    'source': 'polyline',
                })

    # === 板识别 ===
    slab_layers = layer_map.get('slab', [])
    for poly in entities['polylines']:
        if not poly['closed']:
            continue
        if not _layer_match(poly['layer'], slab_layers):
            continue
        area = poly.get('area', 0)
        if area > 1.0:  # 大于1m²的闭合区域视为板
            elements['slabs'].append({
                'id': f"LB_{len(elements['slabs'])+1}",
                'outline': poly['points'],
                'area': area,
                'thickness': slab_thickness,
                'perimeter': _perimeter(poly['points']),
                'source': 'polyline',
            })

    # 从文字标注中提取板厚
    for text in entities['texts']:
        if _layer_match(text['layer'], slab_layers):
            thickness = _parse_slab_thickness(text['content'])
            if thickness:
                # 找最近的板并更新板厚
                nearest = _find_nearest_slab(text['position'], elements['slabs'])
                if nearest:
                    nearest['thickness'] = thickness

    # === 门窗识别 ===
    opening_layers = layer_map.get('opening', [])
    for insert in entities['inserts']:
        if _layer_match(insert['layer'], opening_layers):
            block_name = insert['block_name'].upper()
            opening_info = _parse_opening_block(block_name)
            if opening_info:
                opening_info['position'] = insert['position']
                elements['openings'].append(opening_info)

    # 从文字标注中识别门窗
    for text in entities['texts']:
        if _layer_match(text['layer'], opening_layers):
            opening_info = _parse_opening_label(text['content'])
            if opening_info:
                opening_info['position'] = text['position']
                elements['openings'].append(opening_info)

    return elements
```

#### 15.2.3 辅助识别函数

```python
import re
import math

def _layer_match(layer_name: str, target_layers: list) -> bool:
    """检查图层名是否匹配目标图层列表"""
    upper = layer_name.upper()
    for tl in target_layers:
        if tl.upper() in upper or upper in tl.upper():
            return True
    return False

def _detect_rectangle(points: list) -> dict:
    """
    检测闭合多段线是否为矩形
    返回: {is_rect, width, height, center} or None
    """
    if len(points) < 4:
        return None
    # 取前4个点(矩形)
    pts = points[:4]
    # 检查是否有4个直角
    angles = []
    for i in range(4):
        v1 = _sub(pts[(i+1)%4], pts[i])
        v2 = _sub(pts[(i-1)%4], pts[i])
        angle = _angle_between(v1, v2)
        angles.append(angle)

    # 4个角都接近90°(容差±5°)
    if all(abs(a - 90) < 5 for a in angles):
        w = _dist(pts[0], pts[1])
        h = _dist(pts[1], pts[2])
        cx = sum(p[0] for p in pts) / 4
        cy = sum(p[1] for p in pts) / 4
        return {'width': w, 'height': h, 'center': (cx, cy)}
    return None

def _parse_column_label(text: str) -> dict:
    """
    从文字标注中解析柱编号和截面
    示例: "KZ-1 600x600" → {id: 'KZ-1', width: 0.6, depth: 0.6}
         "KZ-2(500×500)" → {id: 'KZ-2', width: 0.5, depth: 0.5}
    """
    # 匹配柱编号
    id_pattern = r'([KGXZ][Z])-?(\d+)'
    id_match = re.search(id_pattern, text.upper())
    if not id_match:
        return None

    col_id = f"{id_match.group(1)}-{id_match.group(2)}"

    # 匹配截面尺寸 "600x600" 或 "500×500" 或 "D=800"(圆柱)
    rect_pattern = r'(\d+)\s*[x×*]\s*(\d+)'
    circle_pattern = r'[Dd][=＝:]?\s*(\d+)'

    rect_match = re.search(rect_pattern, text)
    circle_match = re.search(circle_pattern, text)

    if rect_match:
        w = int(rect_match.group(1)) / 1000  # mm → m
        d = int(rect_match.group(2)) / 1000
        return {'id': col_id, 'width': w, 'depth': d, 'shape': 'rect'}
    elif circle_match:
        dia = int(circle_match.group(1)) / 1000
        return {'id': col_id, 'width': dia, 'depth': dia, 'shape': 'circle'}
    else:
        return {'id': col_id, 'width': 0.4, 'depth': 0.4, 'shape': 'unknown'}

def _parse_beam_label(text: str) -> dict:
    """
    从文字标注中解析梁编号和截面
    示例: "KL1(1) 300x600" → {id: 'KL1', width: 0.3, height: 0.6}
         "KL2(2A) 250×500" → {id: 'KL2', width: 0.25, height: 0.5}
    """
    # 匹配梁编号: KL1, LL2, WKL3, XL4, JL5
    id_pattern = r'([KLWJX][L])-?(\d+)'
    id_match = re.search(id_pattern, text.upper())
    if not id_match:
        return None

    beam_id = f"{id_match.group(1)}{id_match.group(2)}"

    # 匹配截面
    section_pattern = r'(\d+)\s*[x×*]\s*(\d+)'
    section_match = re.search(section_pattern, text)
    if section_match:
        w = int(section_match.group(1)) / 1000
        h = int(section_match.group(2)) / 1000
    else:
        w, h = 0.25, 0.5  # 默认值

    # 匹配跨数: (1), (2A), (3B)
    span_pattern = r'\((\d+)([AB]?)\)'
    span_match = re.search(span_pattern, text)
    spans = int(span_match.group(1)) if span_match else 1
    cantilever = span_match.group(2) if span_match else ''

    return {
        'id': beam_id,
        'width': w,
        'height': h,
        'spans': spans,
        'cantilever': cantilever,
    }

def _parse_slab_thickness(text: str) -> float:
    """
    从文字标注中解析板厚
    示例: "h=120" → 0.12, "板厚150" → 0.15, "LB1 h=100" → 0.10
    """
    patterns = [
        r'[hH][=＝:]\s*(\d+)',
        r'板厚\s*(\d+)',
        r'thickness\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1)) / 1000  # mm → m
    return None

def _parse_opening_label(text: str) -> dict:
    """
    从文字标注中解析门窗信息
    示例: "M-1 900x2100" → {id: 'M-1', type: 'door', width: 0.9, height: 2.1}
         "C-1 1500×1800" → {id: 'C-1', type: 'window', width: 1.5, height: 1.8}
    """
    upper = text.upper().strip()

    # 判断门窗类型
    if any(upper.startswith(p) for p in ['M-', 'M ', 'FM-', '门']):
        open_type = 'door'
    elif any(upper.startswith(p) for p in ['C-', 'C ', 'TC-', 'FC-', '窗']):
        open_type = 'window'
    else:
        return None

    # 匹配编号
    id_pattern = r'([MCF][MTCF]?)-?(\d+)'
    id_match = re.search(id_pattern, upper)
    open_id = f"{id_match.group(1)}-{id_match.group(2)}" if id_match else ''

    # 匹配尺寸
    size_pattern = r'(\d+)\s*[x×*]\s*(\d+)'
    size_match = re.search(size_pattern, text)
    if size_match:
        w = int(size_match.group(1)) / 1000
        h = int(size_match.group(2)) / 1000
    else:
        w, h = 0.9, 2.1  # 默认门尺寸

    return {'id': open_id, 'type': open_type, 'width': w, 'height': h}

def _parse_opening_block(block_name: str) -> dict:
    """从图块名中解析门窗信息"""
    return _parse_opening_label(block_name)

def _find_parallel_pairs(lines: list, max_gap: float = 0.5) -> list:
    """找出平行线对(用于识别墙/梁)"""
    pairs = []
    used = set()
    for i, l1 in enumerate(lines):
        if i in used:
            continue
        for j, l2 in enumerate(lines):
            if j <= i or j in used:
                continue
            if _is_parallel(l1, l2) and _line_distance(l1, l2) <= max_gap:
                pairs.append({'line1': l1, 'line2': l2})
                used.add(i)
                used.add(j)
                break
    return pairs

def _is_parallel(l1: dict, l2: dict, tol: float = 5.0) -> bool:
    """判断两条线段是否平行"""
    v1 = _sub(l1['end'], l1['start'])
    v2 = _sub(l2['end'], l2['start'])
    if _magnitude(v1) < 1e-6 or _magnitude(v2) < 1e-6:
        return False
    cos_angle = abs(_dot(v1, v2) / (_magnitude(v1) * _magnitude(v2)))
    return cos_angle > math.cos(math.radians(tol))

def _line_distance(l1: dict, l2: dict) -> float:
    """两条平行线间的距离"""
    v = _sub(l1['end'], l1['start'])
    n = _normalize(_perpendicular(v))
    d = _sub(l2['start'], l1['start'])
    return abs(_dot(d, n))

def _line_center(l1: dict, l2: dict) -> dict:
    """两条平行线的中线"""
    s1, e1 = l1['start'], l1['end']
    s2, e2 = l2['start'], l2['end']
    mid_s = ((s1[0]+s2[0])/2, (s1[1]+s2[1])/2, 0)
    mid_e = ((e1[0]+e2[0])/2, (e1[1]+e2[1])/2, 0)
    length = _dist(mid_s, mid_e)
    return {'start': mid_s, 'end': mid_e, 'length': length}

def _find_nearest_text(element: dict, texts: list, max_dist: float = 2.0) -> dict:
    """找到离构件最近的文字标注"""
    pos = element.get('start') or element.get('position')
    if not pos:
        return None
    nearest = None
    min_dist = max_dist
    for t in texts:
        d = _dist(pos, t['position'])
        if d < min_dist:
            min_dist = d
            nearest = t
    return nearest

def _find_nearest_slab(position: tuple, slabs: list) -> dict:
    """找到离文字标注最近的板"""
    if not slabs:
        return None
    nearest = slabs[0]
    min_dist = float('inf')
    for slab in slabs:
        cx = sum(p[0] for p in slab['outline']) / len(slab['outline'])
        cy = sum(p[1] for p in slab['outline']) / len(slab['outline'])
        d = math.sqrt((position[0]-cx)**2 + (position[1]-cy)**2)
        if d < min_dist:
            min_dist = d
            nearest = slab
    return nearest

# 向量运算工具
def _sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2] if len(a)>2 else 0)
def _dot(a, b): return a[0]*b[0] + a[1]*b[1]
def _magnitude(v): return math.sqrt(v[0]**2 + v[1]**2)
def _normalize(v):
    m = _magnitude(v)
    return (v[0]/m, v[1]/m, 0) if m > 0 else (0, 0, 0)
def _perpendicular(v): return (-v[1], v[0], 0)
def _dist(a, b): return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)
def _angle_between(v1, v2):
    m1, m2 = _magnitude(v1), _magnitude(v2)
    if m1 < 1e-6 or m2 < 1e-6: return 0
    cos_a = _dot(v1, v2) / (m1 * m2)
    cos_a = max(-1, min(1, cos_a))
    return math.degrees(math.acos(cos_a))
def _perimeter(points: list) -> float:
    n = len(points)
    return sum(_dist(points[i], points[(i+1)%n]) for i in range(n))
```

---

### 15.3 尺寸与标高提取

```python
def extract_dimensions_from_drawing(drawing_info: dict) -> dict:
    """
    从图纸中提取尺寸标注和标高信息
    输入: parse_cad_drawing() 的返回值
    输出: {
        dimensions: [{type, measurement, text, position}],
        elevations: [{value, position, label}],
        axis_grid: {x_axes, y_axes},
    }
    """
    entities = drawing_info['entities']

    # === 尺寸标注提取 ===
    dimensions = []
    for dim in entities['dimensions']:
        dim_record = {
            'type': dim.get('type', 'DIMENSION'),
            'measurement': dim.get('measurement', 0),
            'text_override': dim.get('text_override', ''),
            'layer': dim.get('layer', ''),
        }
        # 从文字覆盖中提取数值
        if dim_record['text_override'] and dim_record['text_override'] != '<>':
            parsed = _parse_dimension_text(dim_record['text_override'])
            if parsed:
                dim_record['measurement'] = parsed
        dimensions.append(dim_record)

    # === 标高提取 ===
    elevations = []
    for text in entities['texts']:
        elev = _parse_elevation(text['content'])
        if elev is not None:
            elevations.append({
                'value': elev,
                'position': text['position'],
                'raw_text': text['content'],
                'layer': text['layer'],
            })

    # === 轴网提取 ===
    axis_lines = [l for l in entities['lines']
                  if _layer_match(l['layer'], ['AXIS', '轴线', 'ZX-', 'AX-'])]
    x_axes, y_axes = _extract_axis_grid(axis_lines)

    # 从文字中提取轴线编号
    axis_labels = []
    for text in entities['texts']:
        label = _parse_axis_label(text['content'])
        if label:
            axis_labels.append({
                'label': label,
                'position': text['position'],
            })

    # 将轴线编号与轴线关联
    x_axes = _assign_axis_labels(x_axes, axis_labels, 'x')
    y_axes = _assign_axis_labels(y_axes, axis_labels, 'y')

    return {
        'dimensions': dimensions,
        'elevations': elevations,
        'axis_grid': {
            'x_axes': x_axes,  # X方向轴线(纵向线)
            'y_axes': y_axes,  # Y方向轴线(横向线)
            'labels': axis_labels,
        },
    }

def _parse_dimension_text(text: str) -> float:
    """从尺寸标注文字中提取数值"""
    # "%%c1200" → 1200, "4500" → 4500, "4.5m" → 4500
    match = re.search(r'(\d+\.?\d*)\s*m?m?', text.replace('%%c', ''))
    if match:
        val = float(match.group(1))
        return val if val > 50 else val * 1000  # 小数可能是米
    return None

def _parse_elevation(text: str) -> float:
    """
    从文字中解析标高
    示例: "%%p0.000" → 0.0, "+3.500" → 3.5, "±0.000" → 0.0, "H=3.600" → 3.6
    """
    # 标高符号: △, ±, %%p, +-, H=
    patterns = [
        r'[%%][pP]\s*(-?\d+\.?\d*)',
        r'[±]\s*(-?\d+\.?\d*)',
        r'[+-]\s*(-?\d+\.?\d*)',
        r'[Hh][=＝:]\s*(-?\d+\.?\d*)',
        r'△\s*(-?\d+\.?\d*)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return float(match.group(1))
    return None

def _parse_axis_label(text: str) -> str:
    """从文字中解析轴线编号 (A/B/C 或 1/2/3)"""
    text = text.strip()
    # 单字母 A-Z 或 单数字 1-99
    if re.match(r'^[A-Z]$', text) or re.match(r'^\d{1,2}$', text):
        return text
    # ①②③ 等圆圈数字
    circle_map = {'①':'1','②':'2','③':'3','④':'4','⑤':'5',
                  '⑥':'6','⑦':'7','⑧':'8','⑨':'9','⑩':'10'}
    if text in circle_map:
        return circle_map[text]
    return None

def _extract_axis_grid(axis_lines: list) -> tuple:
    """从轴线中提取X方向和Y方向的轴网"""
    x_axes = []  # 纵向线(X=const)
    y_axes = []  # 横向线(Y=const)

    for line in axis_lines:
        s, e = line['start'], line['end']
        dx = abs(e[0] - s[0])
        dy = abs(e[1] - s[1])

        if dy > dx * 3:  # 纵向线
            x = (s[0] + e[0]) / 2
            x_axes.append({
                'x': x, 'y_start': min(s[1], e[1]),
                'y_end': max(s[1], e[1]), 'label': ''
            })
        elif dx > dy * 3:  # 横向线
            y = (s[1] + e[1]) / 2
            y_axes.append({
                'y': y, 'x_start': min(s[0], e[0]),
                'x_end': max(s[0], e[0]), 'label': ''
            })

    # 按坐标排序
    x_axes.sort(key=lambda a: a['x'])
    y_axes.sort(key=lambda a: a['y'])

    return x_axes, y_axes

def _assign_axis_labels(axes: list, labels: list, direction: str) -> list:
    """将轴线编号分配给最近的轴线"""
    if not axes or not labels:
        return axes

    for label_info in labels:
        nearest = min(axes, key=lambda a:
            _dist(a.get('x' if direction == 'x' else 'y', 0) and
                  (a['x'] if direction == 'x' else a['y']),
                  label_info['position'][0 if direction == 'x' else 1]))
        nearest['label'] = label_info['label']

    return axes
```

---

### 15.4 钢筋信息提取

```python
def extract_rebar_info(drawing_info: dict) -> dict:
    """
    从结构图纸中提取钢筋信息
    识别: 钢筋编号、直径、间距、长度、级别
    示例文字: "Φ10@200", "C16@150", "2C20", "Φ8@150(双肢箍)"

    返回: {
        rebar_items: [{id, diameter, grade, spacing, count, length, location}],
        summary: {total_weight_kg, by_diameter, by_element}
    }
    """
    entities = drawing_info['entities']
    rebar_items = []

    for text in entities['texts']:
        content = text['content']
        items = _parse_rebar_text(content)
        for item in items:
            item['position'] = text['position']
            item['layer'] = text['layer']
            item['source_text'] = content
            rebar_items.append(item)

    # 按构件位置聚类
    element_rebar = _cluster_rebar_by_element(rebar_items, drawing_info)

    # 汇总
    total_weight = 0
    by_diameter = {}
    for item in rebar_items:
        weight = _rebar_weight(item)
        item['weight_kg'] = weight
        total_weight += weight
        dia = item['diameter']
        by_diameter[dia] = by_diameter.get(dia, 0) + weight

    return {
        'rebar_items': rebar_items,
        'element_rebar': element_rebar,
        'summary': {
            'total_weight_kg': round(total_weight, 1),
            'total_weight_t': round(total_weight / 1000, 3),
            'by_diameter': {k: round(v, 1) for k, v in sorted(by_diameter.items())},
            'item_count': len(rebar_items),
        }
    }

def _parse_rebar_text(text: str) -> list:
    """
    解析钢筋标注文字
    支持格式:
      "Φ10@200"     → [{diameter:10, grade:'HPB300', spacing:200}]
      "C16@150"     → [{diameter:16, grade:'HRB400', spacing:150}]
      "2C20"        → [{diameter:20, grade:'HRB400', count:2}]
      "Φ8@150(双肢)" → [{diameter:8, grade:'HPB300', spacing:150, legs:2}]
      "4C25+2C20"   → [{diameter:25, count:4}, {diameter:20, count:2}]
    """
    results = []

    # 钢筋级别映射: Φ/A=HPB300, B/C=HRB400, D=HRB500
    grade_map = {
        'Φ': 'HPB300', 'A': 'HPB300', 'a': 'HPB300',
        'B': 'HRB400', 'b': 'HRB400', 'C': 'HRB400', 'c': 'HRB400',
        'D': 'HRB500', 'd': 'HRB500',
    }

    # 匹配模式: [级别符号][直径]@[间距] 或 [数量][级别符号][直径]
    # 模式1: X铜@间距 (如 Φ10@200, C16@150)
    pattern1 = r'([ΦABCDabcd])\s*(\d+)\s*[@＠]\s*(\d+)'
    # 模式2: 数量X直径 (如 2C20, 4B25)
    pattern2 = r'(\d+)\s*([ΦABCDabcd])\s*(\d+)'
    # 模式3: 肢数 (如 双肢, 四肢)
    legs_pattern = r'(\d+)[肢支]|([双四两])肢'

    legs_map = {'双': 2, '两': 2, '四': 4, '六': 6}

    # 先匹配模式1
    for m in re.finditer(pattern1, text):
        grade_sym = m.group(1)
        diameter = int(m.group(2))
        spacing = int(m.group(3))
        grade = grade_map.get(grade_sym, 'HRB400')

        # 查找肢数
        legs_match = re.search(legs_pattern, text)
        legs = 2
        if legs_match:
            if legs_match.group(1):
                legs = int(legs_match.group(1))
            elif legs_match.group(2):
                legs = legs_map.get(legs_match.group(2), 2)

        results.append({
            'diameter': diameter,
            'grade': grade,
            'spacing': spacing,
            'count': 0,  # 由间距和长度计算
            'legs': legs,
            'type': 'stirrup' if legs > 1 else 'main',
        })

    # 再匹配模式2 (排除已被模式1匹配的部分)
    remaining = re.sub(pattern1, '', text)
    for m in re.finditer(pattern2, remaining):
        count = int(m.group(1))
        grade_sym = m.group(2)
        diameter = int(m.group(3))
        grade = grade_map.get(grade_sym, 'HRB400')

        results.append({
            'diameter': diameter,
            'grade': grade,
            'spacing': 0,
            'count': count,
            'legs': 0,
            'type': 'main',
        })

    return results

# 钢筋理论重量表 (kg/m)
REBAR_UNIT_WEIGHT = {
    6: 0.222, 8: 0.395, 10: 0.617, 12: 0.888, 14: 1.21,
    16: 1.58, 18: 2.0, 20: 2.47, 22: 2.98, 25: 3.85,
    28: 4.83, 32: 6.31, 36: 7.99, 40: 9.87,
}

def _rebar_weight(item: dict) -> float:
    """估算单根钢筋重量(kg)"""
    diameter = item['diameter']
    unit_w = REBAR_UNIT_WEIGHT.get(diameter, 0)

    if item['type'] == 'main':
        # 主筋: 假设平均长度6m(一层高+锚固)
        length = item.get('length', 6.0)
        count = item.get('count', 1)
        return unit_w * length * count
    else:
        # 箍筋: 假设构件长度3m,按间距计算根数
        element_length = item.get('element_length', 3.0)
        spacing = item.get('spacing', 200) / 1000  # mm → m
        count = int(element_length / spacing) + 1
        # 箍筋单根长度 ≈ 构件周长 (简化)
        length = item.get('length', 1.5)
        return unit_w * length * count

def _cluster_rebar_by_element(rebar_items: list, drawing_info: dict) -> dict:
    """将钢筋按最近的构件聚类"""
    # 简化: 按图层分组
    clusters = {}
    for item in rebar_items:
        layer = item.get('layer', 'unknown')
        if layer not in clusters:
            clusters[layer] = []
        clusters[layer].append(item)
    return clusters
```

---

### 15.5 自动算量管线

```python
def auto_quantity_from_drawing(
    filepath: str,
    floor_height: float = 3.0,
    slab_thickness: float = 0.12,
    project_info: dict = None,
) -> dict:
    """
    从CAD图纸自动计算工程量 — 一键管线
    输入: CAD文件路径 + 楼层信息
    输出: 完整工程量报告

    调用链:
      parse_cad_drawing() → extract_elements_from_drawing()
      → extract_dimensions_from_drawing() → extract_rebar_info()
      → calculate_concrete_detail() → calculate_full_rebar()
      → 生成报告
    """
    # === Step 1: 解析CAD ===
    drawing = parse_cad_drawing(filepath)

    # === Step 2: 识别构件 ===
    elements = extract_elements_from_drawing(
        drawing, floor_height, slab_thickness)

    # === Step 3: 提取尺寸标注 ===
    dims = extract_dimensions_from_drawing(drawing)

    # === Step 4: 提取钢筋信息 ===
    rebar = extract_rebar_info(drawing)

    # === Step 5: 计算混凝土和模板 ===
    concrete_results = {}

    # 柱
    if elements['columns']:
        col_entities = [
            {'width': c['width'], 'depth': c.get('depth', c['width']),
             'height': c['height']}
            for c in elements['columns']
        ]
        concrete_results['column'] = calculate_concrete_detail(
            col_entities, 'column')
        concrete_results['column']['count'] = len(elements['columns'])

    # 梁
    if elements['beams']:
        beam_entities = [
            {'width': b['width'], 'height': b['height'], 'length': b['length']}
            for b in elements['beams']
        ]
        concrete_results['beam'] = calculate_concrete_detail(
            beam_entities, 'beam')
        concrete_results['beam']['count'] = len(elements['beams'])

    # 墙
    if elements['walls']:
        wall_entities = [
            {'length': w['length'], 'height': w['height'],
             'thickness': w['thickness']}
            for w in elements['walls']
        ]
        concrete_results['wall'] = calculate_concrete_detail(
            wall_entities, 'wall')
        concrete_results['wall']['count'] = len(elements['walls'])

    # 板
    if elements['slabs']:
        slab_entities = [
            {'area': s['area'], 'thickness': s['thickness'],
             'perimeter': s.get('perimeter', 0)}
            for s in elements['slabs']
        ]
        concrete_results['slab'] = calculate_concrete_detail(
            slab_entities, 'slab')
        concrete_results['slab']['count'] = len(elements['slabs'])

    # === Step 6: 汇总 ===
    total_concrete = sum(
        r.get('concrete_volume_m3', 0) for r in concrete_results.values())
    total_formwork = sum(
        r.get('formwork_area_m2', 0) for r in concrete_results.values())

    # === Step 7: 生成报告 ===
    report = {
        'project_info': project_info or {'source_file': filepath},
        'drawing_info': {
            'file': filepath,
            'layers': len(drawing['layers']),
            'total_entities': sum(
                len(v) for v in drawing['entities'].values()),
        },
        'elements_detected': {
            'columns': len(elements['columns']),
            'beams': len(elements['beams']),
            'walls': len(elements['walls']),
            'slabs': len(elements['slabs']),
            'openings': len(elements['openings']),
        },
        'concrete_quantities': concrete_results,
        'rebar_quantities': rebar.get('summary', {}),
        'summary': {
            'total_concrete_m3': round(total_concrete, 2),
            'total_formwork_m2': round(total_formwork, 2),
            'total_rebar_kg': rebar.get('summary', {}).get('total_weight_kg', 0),
            'total_rebar_t': rebar.get('summary', {}).get('total_weight_t', 0),
        },
        'dimensions': {
            'count': len(dims['dimensions']),
            'elevations': len(dims['elevations']),
            'axis_x': len(dims['axis_grid']['x_axes']),
            'axis_y': len(dims['axis_grid']['y_axes']),
        },
    }

    return report
```

---

### 15.6 多层楼层组装

```python
def assemble_multi_floor_quantities(
    floor_drawings: list,  # [(floor_name, filepath, floor_height), ...]
    project_info: dict = None,
) -> dict:
    """
    多层楼层图纸组装 — 合并各层工程量
    输入: [(地下室, -1F.dxf, 3.6), (一层, 1F.dxf, 4.0), (二层, 2F.dxf, 3.0), ...]
    输出: 全楼汇总工程量
    """
    floor_results = []
    total = {
        'concrete_volume': 0,
        'formwork_area': 0,
        'rebar_weight': 0,
        'columns': 0,
        'beams': 0,
        'walls': 0,
        'slabs': 0,
    }

    for floor_name, filepath, floor_height in floor_drawings:
        result = auto_quantity_from_drawing(
            filepath, floor_height=floor_height, project_info=project_info)

        floor_result = {
            'floor': floor_name,
            'height': floor_height,
            'summary': result['summary'],
            'elements': result['elements_detected'],
        }
        floor_results.append(floor_result)

        total['concrete_volume'] += result['summary']['total_concrete_m3']
        total['formwork_area'] += result['summary']['total_formwork_m2']
        total['rebar_weight'] += result['summary']['total_rebar_kg']
        total['columns'] += result['elements_detected']['columns']
        total['beams'] += result['elements_detected']['beams']
        total['walls'] += result['elements_detected']['walls']
        total['slabs'] += result['elements_detected']['slabs']

    return {
        'project_info': project_info or {},
        'floors': floor_results,
        'floor_count': len(floor_results),
        'total': {
            'concrete_volume_m3': round(total['concrete_volume'], 2),
            'formwork_area_m2': round(total['formwork_area'], 2),
            'rebar_weight_kg': round(total['rebar_weight'], 1),
            'rebar_weight_t': round(total['rebar_weight'] / 1000, 2),
            'total_columns': total['columns'],
            'total_beams': total['beams'],
            'total_walls': total['walls'],
            'total_slabs': total['slabs'],
        },
    }
```

---

### 15.7 图纸算量结果校核

```python
def audit_quantity_result(
    quantity_report: dict,
    drawing_info: dict = None,
    tolerance: float = 0.05,
) -> dict:
    """
    校核图纸算量结果
    检查项:
      1. 构件数量是否合理(柱间距6~9m, 梁间距3~6m)
      2. 混凝土用量指标是否在正常范围
      3. 钢筋含量指标是否在正常范围
      4. 模板系数是否合理
    """
    issues = []
    warnings = []
    passed = []

    summary = quantity_report.get('summary', {})
    elements = quantity_report.get('elements_detected', {})

    # 检查1: 构件数量校核
    col_count = elements.get('columns', 0)
    beam_count = elements.get('beams', 0)
    slab_count = elements.get('slabs', 0)

    if col_count == 0:
        issues.append('未识别到柱构件 — 检查图层名是否包含COLUMN/KZ等关键字')
    if beam_count == 0 and slab_count == 0:
        warnings.append('未识别到梁或板 — 可能是基础平面图或非结构平面')

    # 检查2: 混凝土用量指标 (m³/m²)
    concrete_vol = summary.get('total_concrete_m3', 0)
    if slab_count > 0 and concrete_vol > 0:
        total_area = sum(s.get('area', 0) for s in
            quantity_report.get('concrete_quantities', {}).get('slab', {}).get('items', []))
        if total_area > 0:
            concrete_index = concrete_vol / total_area
            if concrete_index > 1.5:
                warnings.append(f'混凝土用量指标 {concrete_index:.2f} m³/m² 偏高(正常0.3~0.8)')
            elif concrete_index < 0.1:
                warnings.append(f'混凝土用量指标 {concrete_index:.2f} m³/m² 偏低')
            else:
                passed.append(f'混凝土用量指标 {concrete_index:.2f} m³/m² 正常')

    # 检查3: 钢筋含量指标 (kg/m³)
    rebar_weight = summary.get('total_rebar_kg', 0)
    if concrete_vol > 0 and rebar_weight > 0:
        rebar_index = rebar_weight / concrete_vol
        if rebar_index > 300:
            warnings.append(f'钢筋含量 {rebar_index:.0f} kg/m³ 偏高(正常40~150)')
        elif rebar_index < 10:
            warnings.append(f'钢筋含量 {rebar_index:.0f} kg/m³ 偏低 — 可能钢筋信息提取不完整')
        else:
            passed.append(f'钢筋含量 {rebar_index:.0f} kg/m³ 正常')

    # 检查4: 模板系数 (m²/m³)
    formwork = summary.get('total_formwork_m2', 0)
    if concrete_vol > 0 and formwork > 0:
        formwork_ratio = formwork / concrete_vol
        if formwork_ratio > 25:
            warnings.append(f'模板系数 {formwork_ratio:.1f} m²/m³ 偏高(正常8~18)')
        elif formwork_ratio < 2:
            warnings.append(f'模板系数 {formwork_ratio:.1f} m²/m³ 偏低')
        else:
            passed.append(f'模板系数 {formwork_ratio:.1f} m²/m³ 正常')

    # 综合评价
    if issues:
        status = '存在问题'
    elif warnings:
        status = '基本正常(有警告)'
    else:
        status = '校核通过'

    return {
        'status': status,
        'issues': issues,
        'warnings': warnings,
        'passed': passed,
        'summary': {
            'issue_count': len(issues),
            'warning_count': len(warnings),
            'passed_count': len(passed),
        },
    }
```

---

### 15.8 图纸算量完整输出报告

```python
def generate_drawing_quantity_report(
    filepath: str,
    output_path: str = None,
    floor_height: float = 3.0,
    project_info: dict = None,
) -> dict:
    """
    图纸算量完整报告生成 — 端到端管线
    输入: CAD文件路径
    输出: 完整报告(dict) + Excel文件(可选)
    """
    # 自动算量
    report = auto_quantity_from_drawing(
        filepath, floor_height, project_info)

    # 校核
    audit = audit_quantity_result(report)

    # 组装最终报告
    final_report = {
        'project': project_info or {'source_file': filepath},
        'source_file': filepath,
        'generated_at': __import__('datetime').datetime.now().isoformat(),
        'drawing_info': report['drawing_info'],
        'elements_detected': report['elements_detected'],
        'concrete_quantities': report['concrete_quantities'],
        'rebar_quantities': report['rebar_quantities'],
        'summary': report['summary'],
        'audit': audit,
    }

    # 可选: 导出Excel
    if output_path:
        _export_report_to_excel(final_report, output_path)

    return final_report


def _export_report_to_excel(report: dict, output_path: str):
    """将报告导出为Excel"""
    from openpyxl import Workbook
    wb = Workbook()

    # Sheet 1: 汇总
    ws = wb.active
    ws.title = "汇总"
    ws['A1'] = "图纸自动算量报告"
    ws['A1'].font = ws['A1'].font.copy(bold=True, size=14)

    ws['A3'] = "源文件"; ws['B3'] = report['source_file']
    ws['A4'] = "生成时间"; ws['B4'] = report['generated_at']

    ws['A6'] = "构件统计"
    for i, (elem, count) in enumerate(report['elements_detected'].items()):
        ws.cell(row=7+i, column=1, value=elem)
        ws.cell(row=7+i, column=2, value=count)

    ws['A13'] = "工程量汇总"
    for i, (key, val) in enumerate(report['summary'].items()):
        ws.cell(row=14+i, column=1, value=key)
        ws.cell(row=14+i, column=2, value=val)

    # Sheet 2: 混凝土明细
    ws2 = wb.create_sheet("混凝土明细")
    headers = ['构件类型', '数量', '混凝土(m³)', '模板(m²)']
    for col, h in enumerate(headers, 1):
        ws2.cell(row=1, column=col, value=h)
    for i, (etype, data) in enumerate(
        report['concrete_quantities'].items(), 2):
        ws2.cell(row=i, column=1, value=etype)
        ws2.cell(row=i, column=2, value=data.get('count', 0))
        ws2.cell(row=i, column=3, value=data.get('concrete_volume_m3', 0))
        ws2.cell(row=i, column=4, value=data.get('formwork_area_m2', 0))

    # Sheet 3: 校核
    ws3 = wb.create_sheet("校核")
    ws3['A1'] = "校核结果"
    ws3['A1'].font = ws3['A1'].font.copy(bold=True, size=12)
    ws3['A3'] = "状态"; ws3['B3'] = report['audit']['status']
    ws3['A5'] = "问题"
    for i, issue in enumerate(report['audit']['issues']):
        ws3.cell(row=6+i, column=1, value=issue)
    ws3.cell(row=6+len(report['audit']['issues'])+1, column=1, value="警告")
    for i, warn in enumerate(report['audit']['warnings']):
        ws3.cell(row=7+len(report['audit']['issues'])+i, column=1, value=warn)

    wb.save(output_path)
```

---

### 15.9 各专业图纸算量适配

```python
def auto_quantity_by_discipline(
    filepath: str,
    discipline: str,  # 'civil'/'municipal'/'highway'/'curtain_wall'/'steel'/'tunnel'
    params: dict = None,
) -> dict:
    """
    按专业类型自动算量
    """
    params = params or {}
    drawing = parse_cad_drawing(filepath)

    if discipline == 'civil':
        # 土建: 使用标准管线
        return auto_quantity_from_drawing(filepath, **params)

    elif discipline == 'municipal':
        # 市政: 管道/道路/桥梁
        elements = extract_municipal_elements(drawing)
        return calculate_municipal_full({
            'pipes': elements.get('pipes', []),
            'roads': elements.get('roads', []),
            'manholes': elements.get('manholes', []),
            **params,
        })

    elif discipline == 'highway':
        # 公路: 路线/断面
        alignment = extract_alignment_from_drawing(drawing)
        cross_sections = extract_cross_sections(drawing)
        return calculate_highway_full(alignment, cross_sections, params)

    elif discipline == 'curtain_wall':
        # 幕墙
        elements = extract_curtain_wall_elements(drawing)
        return calculate_curtain_wall_full({
            'panels': elements,
            **params,
        })

    elif discipline == 'steel':
        # 钢结构
        elements = extract_steel_elements(drawing)
        return calculate_steel_full(elements)

    elif discipline == 'tunnel':
        # 隧道
        elements = extract_tunnel_elements(drawing)
        return calculate_tunnel_full({
            'cross_section': elements.get('cross_section', {}),
            'length': elements.get('length', 0),
            **params,
        })

    else:
        return auto_quantity_from_drawing(filepath, **params)


def extract_municipal_elements(drawing: dict) -> dict:
    """从图纸中提取市政构件(管道/道路/井)"""
    elements = {'pipes': [], 'roads': [], 'manholes': []}
    layer_map = classify_layers(drawing.get('layers', []))

    # 管道: 从线段(管道图层)中提取
    pipe_layers = [l for l in drawing.get('layers', [])
                   if any(kw in l.upper() for kw in ['PIPE', '管道', 'G-', 'PS-', 'GS-', 'YS-', 'WS-'])]
    for line in drawing['entities']['lines']:
        if _layer_match(line['layer'], pipe_layers):
            elements['pipes'].append({
                'start': line['start'],
                'end': line['end'],
                'length': line['length'],
                'diameter': 0.3,  # 默认管径,从文字标注获取
                'material': 'HDPE',
            })

    # 井: 从图块参照中提取
    for insert in drawing['entities']['inserts']:
        name = insert['block_name'].upper()
        if 'WELL' in name or 'JIN' in name or '井' in name or 'MANHOLE' in name:
            elements['manholes'].append({
                'position': insert['position'],
                'type': 'manhole',
                'depth': 1.5,
            })

    # 道路: 从闭合多段线中提取
    road_layers = [l for l in drawing.get('layers', [])
                   if any(kw in l.upper() for kw in ['ROAD', '道路', 'DL-', 'LM-'])]
    for poly in drawing['entities']['polylines']:
        if poly['closed'] and _layer_match(poly['layer'], road_layers):
            elements['roads'].append({
                'outline': poly['points'],
                'area': poly.get('area', 0),
            })

    return elements


def extract_alignment_from_drawing(drawing: dict) -> dict:
    """从公路图纸中提取路线数据"""
    alignment = {'horizontal': [], 'vertical': [], 'stations': []}
    # 从文字标注中提取交点(JD)信息
    for text in drawing['entities']['texts']:
        if 'JD' in text['content'].upper():
            alignment['horizontal'].append({
                'position': text['position'],
                'label': text['content'],
            })
    return alignment


def extract_cross_sections(drawing: dict) -> list:
    """从图纸中提取横断面数据"""
    sections = []
    for poly in drawing['entities']['polylines']:
        if poly['closed'] and len(poly['points']) >= 4:
            sections.append({
                'outline': poly['points'],
                'area': poly.get('area', 0),
            })
    return sections


def extract_curtain_wall_elements(drawing: dict) -> list:
    """从图纸中提取幕墙构件"""
    panels = []
    layer_map = classify_layers(drawing.get('layers', []))
    cw_layers = layer_map.get('wall', [])  # 幕墙通常在wall类图层

    for poly in drawing['entities']['polylines']:
        if poly['closed'] and _layer_match(poly['layer'], cw_layers):
            panels.append({
                'outline': poly['points'],
                'area': poly.get('area', 0),
                'perimeter': _perimeter(poly['points']),
                'type': 'glass',
            })
    return panels


def extract_steel_elements(drawing: dict) -> list:
    """从图纸中提取钢构件"""
    components = []
    layer_map = classify_layers(drawing.get('layers', []))
    steel_layers = [l for l in drawing.get('layers', [])
                    if any(kw in l.upper() for kw in ['STEEL', '钢结构', 'GJG-', 'ST-', 'GL-'])]

    # 从文字标注中提取钢构件截面
    for text in drawing['entities']['texts']:
        section = _parse_steel_section(text['content'])
        if section:
            components.append({
                'section': section,
                'position': text['position'],
                'type': 'beam',  # 默认
            })

    return components


def _parse_steel_section(text: str) -> dict:
    """解析型钢截面标注: H400x200x8x12, I25a, [20a"""
    # H型钢: H400x200x8x12
    h_match = re.match(r'H\s*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)\s*[x×]\s*(\d+)', text, re.I)
    if h_match:
        return {'type': 'H', 'h': int(h_match.group(1)), 'b': int(h_match.group(2)),
                'tw': int(h_match.group(3)), 'tf': int(h_match.group(4))}

    # 工字钢: I25a
    i_match = re.match(r'I\s*(\d+)([a-c])?', text, re.I)
    if i_match:
        return {'type': 'I', 'h': int(i_match.group(1)), 'subclass': i_match.group(2) or 'a'}

    # 槽钢: [20a
    c_match = re.match(r'\[\s*(\d+)([a-c])?', text)
    if c_match:
        return {'type': 'C', 'h': int(c_match.group(1)), 'subclass': c_match.group(2) or 'a'}

    return None


def extract_tunnel_elements(drawing: dict) -> dict:
    """从图纸中提取隧道构件"""
    elements = {'cross_section': {}, 'length': 0}

    # 从闭合多段线中提取隧道断面
    for poly in drawing['entities']['polylines']:
        if poly['closed'] and len(poly['points']) >= 4:
            area = poly.get('area', 0)
            if area > 10:  # 隧道断面通常>10m²
                elements['cross_section'] = {
                    'outline': poly['points'],
                    'area': area,
                    'perimeter': _perimeter(poly['points']),
                }
                break

    # 从文字标注中提取隧道长度
    for text in drawing['entities']['texts']:
        length_match = re.search(r'L\s*[=＝:]\s*(\d+\.?\d*)', text['content'])
        if length_match:
            elements['length'] = float(length_match.group(1))
            break

    return elements
```

---