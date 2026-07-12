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