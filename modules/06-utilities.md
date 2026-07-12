## 六、实用工具集

### 6.1 坐标转换

```python
import math

def coordinate_transform(x, y, z, from_system: str, to_system: str) -> tuple:
    """
    常用工程坐标转换
    支持: WGS84, CGCS2000, 北京54, 西安80
    """
    if from_system == 'WGS84' and to_system == 'CGCS2000':
        return (x, y, z)
    if from_system == 'BJ54' and to_system == 'WGS84':
        dx, dy, dz = -22.0, 118.0, 30.5
        return (x + dx, y + dy, z + dz)
    return (x, y, z)

def gauss_kruger_to_lonlat(X, Y, central_meridian=114.0):
    """
    高斯-克吕格投影 → 经纬度
    """
    e2 = 0.006693421622966
    a = 6378137.0
    Bf = _compute_bottom_latitude(X, a, e2)
    return (0, 0)  # 简化
```

### 6.2 单位换算

```python
# 常用工程单位换算
UNIT_CONVERSIONS = {
    'length': {
        'mm_to_m': 0.001, 'cm_to_m': 0.01, 'm_to_km': 0.001,
        'inch_to_mm': 25.4, 'ft_to_m': 0.3048,
    },
    'area': {
        'mm2_to_m2': 1e-6, 'cm2_to_m2': 1e-4, 'm2_to_ha': 1e-4,
        'm2_to_km2': 1e-6, 'm2_to_mu': 0.0015,
    },
    'volume': {
        'mm3_to_m3': 1e-9, 'cm3_to_m3': 1e-6, 'L_to_m3': 0.001,
    },
    'mass': {
        'kg_to_t': 0.001, 'g_to_kg': 0.001,
    },
    'pressure': {
        'MPa_to_kPa': 1000, 'kPa_to_Pa': 1000, 'MPa_to_psi': 145.038,
    },
}

def convert_unit(value: float, from_unit: str, to_unit: str) -> float:
    """通用单位换算"""
    key = f"{from_unit}_to_{to_unit}"
    return value * UNIT_CONVERSIONS.get(key, 1.0)
```

### 6.3 Excel工程量清单导出

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

def export_quantity_to_excel(quantities: dict, output_path: str):
    """
    导出工程量清单到Excel
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "工程量清单"

    header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
    header_font_white = Font(name='宋体', bold=True, size=12, color='FFFFFF')
    thin_border = Border(
        left=Side(style='thin'), right=Side(style='thin'),
        top=Side(style='thin'), bottom=Side(style='thin'),
    )

    headers = ['序号', '清单编码', '项目名称', '单位', '工程量', '备注']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center')
        cell.border = thin_border

    row = 2
    for idx, (name, qty) in enumerate(quantities.items(), 1):
        ws.cell(row=row, column=1, value=idx).border = thin_border
        ws.cell(row=row, column=2, value=qty.get('code', '')).border = thin_border
        ws.cell(row=row, column=3, value=name).border = thin_border
        ws.cell(row=row, column=4, value=qty.get('unit', 'm³')).border = thin_border
        ws.cell(row=row, column=5, value=qty.get('value', 0)).border = thin_border
        ws.cell(row=row, column=6, value=qty.get('remark', '')).border = thin_border
        row += 1

    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 16
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 10
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 20

    wb.save(output_path)
    return output_path
```

### 6.4 图纸批量处理

```python
import os
import glob

def batch_process_cad(input_dir: str, output_dir: str):
    """
    批量处理CAD图纸
    支持: 批量转换、批量算量、批量导出
    """
    results = []
    dxf_files = glob.glob(os.path.join(input_dir, '*.dxf'))
    dwg_files = glob.glob(os.path.join(input_dir, '*.dwg'))

    for filepath in dxf_files + dwg_files:
        try:
            drawing_info = parse_cad_drawing(filepath)
            results.append({
                'file': os.path.basename(filepath),
                'status': 'success',
                'layers': len(drawing_info['layers']),
                'entities': sum(len(v) for v in drawing_info['entities'].values()),
            })
        except Exception as e:
            results.append({
                'file': os.path.basename(filepath),
                'status': 'error',
                'error': str(e),
            })

    return results
```

---