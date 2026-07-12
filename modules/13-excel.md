## 十三、Excel计算表生成器 (Excel Calculation Sheet Generator)

> 多模板、公式联动、自动汇总的Excel计算表生成系统
> 依赖: openpyxl ≥ 3.1

---

### 13.1 样式系统

```python
from openpyxl import Workbook
from openpyxl.styles import (Font, Alignment, Border, Side, PatternFill,
                              Protection, NamedStyle)
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule

# ============ 统一样式系统 ============
STYLES = {
    'title': {
        'font': Font(name='宋体', size=16, bold=True, color='1F4E79'),
        'alignment': Alignment(horizontal='center', vertical='center'),
    },
    'subtitle': {
        'font': Font(name='宋体', size=12, bold=True, color='FFFFFF'),
        'fill': PatternFill('solid', start_color='2E75B6'),
        'alignment': Alignment(horizontal='center', vertical='center'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'header': {
        'font': Font(name='宋体', size=10, bold=True, color='FFFFFF'),
        'fill': PatternFill('solid', start_color='4472C4'),
        'alignment': Alignment(horizontal='center', vertical='center', wrap_text=True),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'data': {
        'font': Font(name='宋体', size=10),
        'alignment': Alignment(horizontal='center', vertical='center'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'data_left': {
        'font': Font(name='宋体', size=10),
        'alignment': Alignment(horizontal='left', vertical='center', wrap_text=True),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'subtotal': {
        'font': Font(name='宋体', size=10, bold=True),
        'fill': PatternFill('solid', start_color='D6E4F0'),
        'alignment': Alignment(horizontal='center'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='medium'), bottom=Side(style='thin')),
    },
    'total': {
        'font': Font(name='宋体', size=11, bold=True, color='1F4E79'),
        'fill': PatternFill('solid', start_color='B4C7E7'),
        'alignment': Alignment(horizontal='center'),
        'border': Border(
            left=Side(style='medium'), right=Side(style='medium'),
            top=Side(style='medium'), bottom=Side(style='double')),
    },
    'note': {
        'font': Font(name='宋体', size=9, italic=True, color='808080'),
        'alignment': Alignment(horizontal='left'),
    },
    'input': {
        'font': Font(name='宋体', size=10, color='0000CC'),
        'fill': PatternFill('solid', start_color='FFF2CC'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
    'formula': {
        'font': Font(name='宋体', size=10, color='0070C0'),
        'fill': PatternFill('solid', start_color='E2EFDA'),
        'border': Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')),
    },
}

def apply_style(cell, style_name: str):
    """快速应用预定义样式"""
    s = STYLES.get(style_name, STYLES['data'])
    if 'font' in s: cell.font = s['font']
    if 'fill' in s: cell.fill = s['fill']
    if 'alignment' in s: cell.alignment = s['alignment']
    if 'border' in s: cell.border = s['border']

def set_column_widths(ws, widths: dict):
    """批量设置列宽 {列字母: 宽度}"""
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
```

### 13.2 混凝土工程量计算表模板

```python
def generate_concrete_quantity_sheet(
    wb: Workbook,
    project_name: str = '',
    data: list = None,  # [(部位, 构件类型, 截面尺寸, 长度/高度, 数量, 备注), ...]
) -> str:
    """
    生成混凝土工程量计算表(含公式联动)
    黄色单元格=输入项, 绿色单元格=自动计算公式
    """
    ws = wb.create_sheet("混凝土工程量计算表")

    # === 标题区 ===
    ws.merge_cells('A1:H1')
    ws['A1'] = f"混凝土工程量计算表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:H2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # === 表头 ===
    headers = ['序号', '部位/楼层', '构件类型', '截面尺寸(mm)', '长度/高度(m)',
               '数量', '体积(m³)', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[4].height = 30

    # === 数据行(含Excel公式联动) ===
    if not data:
        # 提供空模板(15行)
        data = [('', '', '', '', '', '')] * 15

    start_row = 5
    for idx, (location, elem_type, section, length, count, note) in enumerate(data):
        r = start_row + idx
        # 序号
        ws.cell(row=r, column=1, value=idx + 1)
        apply_style(ws.cell(row=r, column=1), 'data')

        # 输入项(黄色)
        for col, val in [(2, location), (3, elem_type), (4, section),
                         (5, length), (6, count), (8, note)]:
            cell = ws.cell(row=r, column=col, value=val)
            apply_style(cell, 'input')

        # 公式项(绿色): G列 = D(截面解析) × E(长度) × F(数量)
        # 截面尺寸格式如"600×600"或"300×500(宽×高)"
        formula = f'=IFERROR(_parse_section(D{r})*E{r}*F{r},"")'
        cell = ws.cell(row=r, column=7, value=formula)
        apply_style(cell, 'formula')
        cell.number_format = '0.00'

    # === 合计行 ===
    end_row = start_row + len(data)
    ws.merge_cells(f'A{end_row}:F{end_row}')
    ws.cell(row=end_row, column=1, value="合计")
    apply_style(ws.cell(row=end_row, column=1), 'total')
    sum_formula = f'=SUM(G{start_row}:G{end_row-1})'
    cell = ws.cell(row=end_row, column=7, value=sum_formula)
    apply_style(cell, 'total')
    cell.number_format = '0.00'
    ws.cell(row=end_row, column=8, value="m³")
    apply_style(ws.cell(row=end_row, column=8), 'total')

    # === 说明区 ===
    note_row = end_row + 2
    ws.merge_cells(f'A{note_row}:H{note_row}')
    ws.cell(row=note_row, column=1,
            value="说明: 黄色单元格为输入项, 绿色单元格为自动计算公式。截面尺寸格式: 宽×高(如300×500)")
    apply_style(ws.cell(row=note_row, column=1), 'note')

    # 列宽
    set_column_widths(ws, {'A': 6, 'B': 16, 'C': 14, 'D': 18, 'E': 14, 'F': 8, 'G': 12, 'H': 20})

    return ws.title
```

### 13.3 钢筋工程量计算表模板

```python
def generate_rebar_quantity_sheet(
    wb: Workbook,
    project_name: str = '',
    data: list = None,
) -> str:
    """
    生成钢筋工程量计算表(含理论重量联动)
    计算: 重量 = 长度 × 数量 × 理论重量(kg/m)
    """
    ws = wb.create_sheet("钢筋工程量计算表")

    ws.merge_cells('A1:J1')
    ws['A1'] = "钢筋工程量计算表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:J2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # 钢筋理论重量参考表
    ws.merge_cells('A4:J4')
    ws['A4'] = "钢筋理论重量参考表(kg/m)"
    apply_style(ws['A4'], 'subtitle')

    rebar_ref = [['Φ6', 0.222], ['Φ8', 0.395], ['Φ10', 0.617], ['Φ12', 0.888],
                 ['Φ14', 1.21], ['Φ16', 1.58], ['Φ18', 2.0], ['Φ20', 2.47],
                 ['Φ22', 2.98], ['Φ25', 3.85], ['Φ28', 4.83], ['Φ32', 6.31]]
    for col, (spec, weight) in enumerate(rebar_ref):
        c1 = ws.cell(row=5, column=col*2+1, value=spec)
        c2 = ws.cell(row=5, column=col*2+2, value=weight)
        apply_style(c1, 'data')
        apply_style(c2, 'data')
        c2.number_format = '0.000'

    # 表头
    headers = ['序号', '部位', '钢筋编号', '规格', '简图', '单根长度(m)',
               '根数', '理论重量(kg/m)', '总重量(kg)', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=7, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[7].height = 30

    # 数据行
    if not data:
        data = [('', '', '', '', '', '', '')] * 15

    start_row = 8
    for idx, (location, rebar_id, spec, sketch, length, count, note) in enumerate(data):
        r = start_row + idx
        ws.cell(row=r, column=1, value=idx + 1)
        apply_style(ws.cell(row=r, column=1), 'data')

        for col, val in [(2, location), (3, rebar_id), (4, spec), (5, sketch),
                         (6, length), (7, count), (10, note)]:
            cell = ws.cell(row=r, column=col, value=val)
            apply_style(cell, 'input')

        # 理论重量(H列): VLOOKUP查表
        ws.cell(row=r, column=8,
                value=f'=IFERROR(VLOOKUP(D{r},$A$5:$X$5,2,FALSE),"")')
        apply_style(ws.cell(row=r, column=8), 'formula')
        ws.cell(row=r, column=8).number_format = '0.000'

        # 总重量(I列): F(长度) × G(根数) × H(理论重量)
        ws.cell(row=r, column=9,
                value=f'=IFERROR(F{r}*G{r}*H{r},"")')
        apply_style(ws.cell(row=r, column=9), 'formula')
        ws.cell(row=r, column=9).number_format = '0.0'

    # 合计
    end_row = start_row + len(data)
    ws.merge_cells(f'A{end_row}:H{end_row}')
    ws.cell(row=end_row, column=1, value="合计")
    apply_style(ws.cell(row=end_row, column=1), 'total')
    ws.cell(row=end_row, column=9, value=f'=SUM(I{start_row}:I{end_row-1})')
    apply_style(ws.cell(row=end_row, column=9), 'total')
    ws.cell(row=end_row, column=9).number_format = '0.0'
    ws.cell(row=end_row, column=10, value="kg")
    apply_style(ws.cell(row=end_row, column=10), 'total')

    set_column_widths(ws, {'A': 6, 'B': 14, 'C': 12, 'D': 10, 'E': 16, 'F': 14, 'G': 8, 'H': 14, 'I': 14, 'J': 18})

    return ws.title
```

### 13.4 综合工程量清单汇总表

```python
def generate_quantity_summary_sheet(wb: Workbook, project_name: str = '') -> str:
    """
    综合工程量清单汇总表(多专业、自动汇总)
    """
    ws = wb.create_sheet("工程量清单汇总表")

    ws.merge_cells('A1:G1')
    ws['A1'] = "工程量清单汇总表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:G2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # 表头
    headers = ['序号', '清单编码', '项目名称', '计量单位', '工程量', '专业类别', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=4, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[4].height = 30

    # 专业分类汇总区
    categories = [
        ('土建工程', '0101~0117', 20),
        ('市政工程', '0401~0413', 15),
        ('公路工程', 'JTG', 15),
        ('幕墙工程', '0110', 10),
        ('钢结构工程', '0106', 10),
        ('隧道工程', '0114', 10),
    ]

    start_row = 5
    current_row = start_row
    category_subtotals = {}

    for cat_name, code_range, num_rows in categories:
        # 专业小标题
        ws.merge_cells(f'A{current_row}:G{current_row}')
        ws.cell(row=current_row, column=1, value=f"  ▶ {cat_name} ({code_range})")
        apply_style(ws.cell(row=current_row, column=1), 'subtitle')
        current_row += 1

        # 空行供填写
        cat_start = current_row
        for i in range(num_rows):
            ws.cell(row=current_row, column=1, value=i + 1)
            apply_style(ws.cell(row=current_row, column=1), 'data')
            for col in range(2, 8):
                apply_style(ws.cell(row=current_row, column=col), 'input')
            current_row += 1

        # 专业小计
        ws.merge_cells(f'A{current_row}:D{current_row}')
        ws.cell(row=current_row, column=1, value=f"{cat_name} 小计")
        apply_style(ws.cell(row=current_row, column=1), 'subtotal')
        ws.cell(row=current_row, column=5, value=f'=COUNTA(B{cat_start}:B{current_row-1})')
        apply_style(ws.cell(row=current_row, column=5), 'subtotal')
        ws.cell(row=current_row, column=6, value=f'共{num_rows}项')
        apply_style(ws.cell(row=current_row, column=6), 'subtotal')

        category_subtotals[cat_name] = current_row
        current_row += 1

    # 总计行
    ws.merge_cells(f'A{current_row}:D{current_row}')
    ws.cell(row=current_row, column=1, value="工程总计")
    apply_style(ws.cell(row=current_row, column=1), 'total')
    total_rows = [r for r in category_subtotals.values()]
    count_formula = '=' + '+'.join([f'COUNTA(B{s+1}:B{r-1})' for s, r in
        zip([start_row] + total_rows, total_rows + [current_row])])
    ws.cell(row=current_row, column=5, value=f'=COUNTA(B5:B{current_row-1})')
    apply_style(ws.cell(row=current_row, column=5), 'total')

    set_column_widths(ws, {'A': 6, 'B': 16, 'C': 30, 'D': 10, 'E': 14, 'F': 14, 'G': 18})

    return ws.title
```

### 13.5 工程造价汇总表

```python
def generate_cost_summary_sheet(wb: Workbook, project_name: str = '') -> str:
    """
    工程造价汇总表(含公式联动、税率自动计算)
    """
    ws = wb.create_sheet("工程造价汇总表")

    ws.merge_cells('A1:E1')
    ws['A1'] = "工程造价汇总表"
    apply_style(ws['A1'], 'title')
    ws.row_dimensions[1].height = 30

    ws.merge_cells('A2:E2')
    ws['A2'] = f"工程名称: {project_name}"
    apply_style(ws['A2'], 'note')

    # 参数区
    ws['A4'] = "计税方式:"
    apply_style(ws['A4'], 'data_left')
    ws['B4'] = "一般计税"
    apply_style(ws['B4'], 'input')
    ws['C4'] = "税率:"
    apply_style(ws['C4'], 'data_left')
    ws['D4'] = 0.09
    apply_style(ws['D4'], 'input')
    ws['D4'].number_format = '0.00%'

    # 汇总表
    headers = ['序号', '费用项目', '计算基础', '费率(%)', '金额(元)']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=col, value=h)
        apply_style(cell, 'header')
    ws.row_dimensions[6].height = 30

    # 费用行(含公式联动)
    rows_data = [
        ('1', '分部分项工程费', '按清单合计', '', '=0'),  # 手动输入或引用
        ('2', '措施项目费', '人工+机械', '按实际', '=0'),
        ('2.1', '  安全文明施工费', '分部分项工程费', '3.00%', '=D7*0.03'),
        ('2.2', '  夜间施工增加费', '分部分项工程费', '0.50%', '=D7*0.005'),
        ('2.3', '  二次搬运费', '分部分项工程费', '0.80%', '=D7*0.008'),
        ('2.4', '  冬雨季施工增加费', '分部分项工程费', '1.00%', '=D7*0.01'),
        ('2.5', '  脚手架费', '按实际', '', '=0'),
        ('2.6', '  模板费', '按实际', '', '=0'),
        ('3', '其他项目费', '按实际', '', '=0'),
        ('4', '规费', '1+2+3', '4.30%', '=(D7+D8+D15)*0.043'),
        ('4.1', '  社保费', '1+2+3', '3.20%', '=(D7+D8+D15)*0.032'),
        ('4.2', '  住房公积金', '1+2+3', '1.00%', '=(D7+D8+D15)*0.01'),
        ('4.3', '  工程排污费', '1+2+3', '0.10%', '=(D7+D8+D15)*0.001'),
        ('5', '税金', '1+2+3+4', '=D4', '=(D7+D8+D15+D16)*D4'),
        ('', '工程总造价', '1+2+3+4+5', '', '=D7+D8+D15+D16+D20'),
    ]

    start_row = 7
    for idx, (no, name, base, rate, formula) in enumerate(rows_data):
        r = start_row + idx
        ws.cell(row=r, column=1, value=no)
        ws.cell(row=r, column=2, value=name)

        if no in ('', '5') or name == '工程总造价':
            # 总计行
            apply_style(ws.cell(row=r, column=1), 'total')
            apply_style(ws.cell(row=r, column=2), 'total')
            ws.cell(row=r, column=3, value=base)
            apply_style(ws.cell(row=r, column=3), 'total')
            ws.cell(row=r, column=4, value=rate)
            apply_style(ws.cell(row=r, column=4), 'total')
            ws.cell(row=r, column=5, value=formula)
            apply_style(ws.cell(row=r, column=5), 'total')
            ws.cell(row=r, column=5).number_format = '#,##0.00'
        elif '.' in str(no):
            # 子项行
            apply_style(ws.cell(row=r, column=1), 'data')
            apply_style(ws.cell(row=r, column=2), 'data_left')
            ws.cell(row=r, column=3, value=base)
            apply_style(ws.cell(row=r, column=3), 'data_left')
            ws.cell(row=r, column=4, value=rate)
            apply_style(ws.cell(row=r, column=4), 'data')
            ws.cell(row=r, column=5, value=formula)
            apply_style(ws.cell(row=r, column=5), 'formula')
            ws.cell(row=r, column=5).number_format = '#,##0.00'
        else:
            # 主项行
            apply_style(ws.cell(row=r, column=1), 'subtotal')
            apply_style(ws.cell(row=r, column=2), 'subtotal')
            ws.cell(row=r, column=3, value=base)
            apply_style(ws.cell(row=r, column=3), 'subtotal')
            ws.cell(row=r, column=4, value=rate)
            apply_style(ws.cell(row=r, column=4), 'subtotal')
            ws.cell(row=r, column=5, value=formula)
            apply_style(ws.cell(row=r, column=5), 'subtotal')
            ws.cell(row=r, column=5).number_format = '#,##0.00'

    # 更新措施项目费合计公式
    ws.cell(row=8, column=5, value='=D9+D10+D11+D12+D13+D14')
    # 更新规费合计公式
    ws.cell(row=16, column=5, value='=D17+D18+D19')

    # 说明
    note_row = start_row + len(rows_data) + 1
    ws.merge_cells(f'A{note_row}:E{note_row}')
    ws.cell(row=note_row, column=1,
            value="说明: 黄色=输入项, 绿色=公式自动计算。修改D4税率或D7分部分项工程费后,所有费用自动联动更新。")
    apply_style(ws.cell(row=note_row, column=1), 'note')

    set_column_widths(ws, {'A': 6, 'B': 24, 'C': 16, 'D': 12, 'E': 16})

    return ws.title
```

### 13.6 一键生成完整工程Excel工作簿

```python
def generate_full_project_workbook(
    project_name: str = '',
    output_path: str = '工程量计算表.xlsx',
    sheets: list = None,
) -> str:
    """
    一键生成完整工程Excel工作簿
    包含: 混凝土算量表 + 钢筋算量表 + 清单汇总表 + 造价汇总表
    """
    wb = Workbook()

    # 删除默认Sheet
    wb.remove(wb.active)

    # 默认生成全部Sheet
    if sheets is None:
        sheets = ['concrete', 'rebar', 'summary', 'cost']

    if 'concrete' in sheets:
        generate_concrete_quantity_sheet(wb, project_name)

    if 'rebar' in sheets:
        generate_rebar_quantity_sheet(wb, project_name)

    if 'summary' in sheets:
        generate_quantity_summary_sheet(wb, project_name)

    if 'cost' in sheets:
        generate_cost_summary_sheet(wb, project_name)

    # 设置封面
    ws_cover = wb.create_sheet("封面", 0)
    ws_cover.merge_cells('A1:H1')
    ws_cover['A1'] = project_name or "工程量计算表"
    apply_style(ws_cover['A1'], 'title')
    ws_cover.row_dimensions[1].height = 40

    ws_cover.merge_cells('A2:H2')
    ws_cover['A2'] = f"生成日期: {__import__('datetime').datetime.now().strftime('%Y-%m-%d')}"
    apply_style(ws_cover['A2'], 'note')

    # 目录
    ws_cover.merge_cells('A4:H4')
    ws_cover['A4'] = "目录"
    apply_style(ws_cover['A4'], 'subtitle')

    sheet_names = [ws.title for ws in wb.worksheets if ws.title != '封面']
    for i, name in enumerate(sheet_names):
        ws_cover.cell(row=5 + i, column=1, value=f"{i+1}. {name}")
        apply_style(ws_cover.cell(row=5 + i, column=1), 'data_left')

    wb.save(output_path)
    return output_path
```

### 13.7 条件格式与数据校验

```python
def add_conditional_formatting(ws, cell_range: str):
    """添加条件格式: 负值红色, 正值绿色"""
    from openpyxl.formatting.rule import CellIsRule
    red_font = Font(color='FF0000', bold=True)
    green_font = Font(color='008000')
    ws.conditional_formatting.add(cell_range,
        CellIsRule(operator='lessThan', formula=['0'], font=red_font))
    ws.conditional_formatting.add(cell_range,
        CellIsRule(operator='greaterThan', formula=['0'], font=green_font))

def add_data_validation(ws, cell_range: str, validation_type: str = 'list', formula: str = ''):
    """添加数据校验下拉列表"""
    from openpyxl.worksheet.datavalidation import DataValidation
    dv = DataValidation(type=validation_type, formula1=formula, allow_blank=True)
    dv.error = '输入值不在允许范围内'
    dv.errorTitle = '输入错误'
    ws.add_data_validation(dv)
    dv.add(cell_range)
```

---