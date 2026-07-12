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

#### 意图-10: 图纸智能分析与自动算量 (`drawing_to_quantity`)

| 关键字 (中文) | 关键字 (英文) | 触发函数 |
|--------------|-------------|---------|
| 根据图纸算量、图纸分析、自动算量 | auto quantity from drawing | `auto_quantity_from_drawing()` |
| 识别构件、提取构件、图纸识别 | extract elements, recognize | `extract_elements_from_drawing()` |
| 提取尺寸、标注提取、尺寸标注 | extract dimensions | `extract_dimensions_from_drawing()` |
| 提取钢筋、钢筋标注、钢筋信息 | extract rebar info | `extract_rebar_info()` |
| 图层分类、图层识别 | classify layers | `classify_layers()` |
| 多层算量、楼层汇总 | multi floor quantities | `assemble_multi_floor_quantities()` |
| 算量校核、结果校核、量复核 | audit quantity | `audit_quantity_result()` |
| 图纸算量报告、算量报告 | drawing quantity report | `generate_drawing_quantity_report()` |
| 按专业算量、专业图纸 | quantity by discipline | `auto_quantity_by_discipline()` |
| 柱编号、梁编号、KZ、KL | column label, beam label | `_parse_column_label()` / `_parse_beam_label()` |
| 板厚提取、h=120 | slab thickness | `_parse_slab_thickness()` |
| 门窗标注、M-1、C-1 | opening label | `_parse_opening_label()` |
| 钢筋标注、Φ10@200、C16@150 | rebar text | `_parse_rebar_text()` |
| 轴线编号、轴网、轴线 | axis grid, axis label | `extract_dimensions_from_drawing()` |

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