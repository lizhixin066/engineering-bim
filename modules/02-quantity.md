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