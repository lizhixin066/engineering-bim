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