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