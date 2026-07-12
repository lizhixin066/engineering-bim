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