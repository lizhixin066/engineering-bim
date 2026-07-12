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