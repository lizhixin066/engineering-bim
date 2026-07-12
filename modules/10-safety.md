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