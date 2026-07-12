## 九、工程造价计价 (Pricing & Cost Estimation)

> 依据: GB 50500-2013《建设工程工程量清单计价规范》、建办标〔2020〕38号
> 体系: 量价分离 — 工程量由算量模块计算，本模块负责计价

---

### 9.1 费用组成体系

```
工程造价 = 分部分项工程费 + 措施项目费 + 其他项目费 + 规费 + 税金
         └─ 人工费 + 材料费 + 机械费 + 管理费 + 利润
```

| 费用类别 | 编码前缀 | 说明 |
|---------|---------|------|
| 分部分项工程费 | 0101~0117 | 按清单编码对应实体项目 |
| 措施项目费 | 01S | 安全文明施工、夜间施工、二次搬运等 |
| 其他项目费 | 01Q | 暂列金额、暂估价、计日工、总承包服务费 |
| 规费 | 01G | 社保、公积金、工程排污费 |
| 税金 | 01T | 增值税（一般计税9% / 简易计税3%） |

### 9.2 综合单价计算

```
综合单价 = 人工费 + 材料费 + 机械费 + 管理费 + 利润
         + 一般风险费（不含规费和税金）

人工费 = ∑(工日消耗量 × 人工单价)
材料费 = ∑(材料消耗量 × 材料单价)
机械费 = ∑(机械台班消耗量 × 台班单价)
管理费 = (人工费 + 机械费) × 管理费费率
利  润 = (人工费 + 机械费) × 利润率
```

```python
def calculate_composite_unit_price(
    labor_days: float, labor_rate: float,
    materials: list,  # [(name, consumption, unit_price), ...]
    machinery: list,  # [(name, shifts, shift_price), ...]
    mgmt_rate: float = 0.15,
    profit_rate: float = 0.08,
    risk_rate: float = 0.02,
) -> dict:
    """
    计算综合单价
    依据: GB 50500-2013 第3.0.5条
    """
    labor_cost = labor_days * labor_rate

    material_cost = sum(consumption * price for _, consumption, price in materials)

    machinery_cost = sum(shifts * price for _, shifts, price in machinery)

    base = labor_cost + machinery_cost
    management_cost = base * mgmt_rate
    profit = base * profit_rate
    risk = base * risk_rate

    unit_price = (labor_cost + material_cost + machinery_cost
                  + management_cost + profit + risk)

    return {
        'labor_cost': round(labor_cost, 2),
        'material_cost': round(material_cost, 2),
        'machinery_cost': round(machinery_cost, 2),
        'management_cost': round(management_cost, 2),
        'profit': round(profit, 2),
        'risk_cost': round(risk, 2),
        'composite_unit_price': round(unit_price, 2),
        'analysis': {
            '人工费占比': f'{labor_cost/unit_price*100:.1f}%',
            '材料费占比': f'{material_cost/unit_price*100:.1f}%',
            '机械费占比': f'{machinery_cost/unit_price*100:.1f}%',
        }
    }
```

### 9.3 人工工日单价参考表

| 工种 | 工日单价(元) | 工种 | 工日单价(元) |
|------|:---:|------|:---:|
| 综合工日 | 120~150 | 木工 | 150~200 |
| 钢筋工 | 150~220 | 混凝土工 | 130~180 |
| 砌筑工 | 140~190 | 抹灰工 | 130~180 |
| 架子工 | 160~230 | 电焊工 | 180~280 |
| 起重工 | 160~240 | 电工 | 160~250 |
| 管工 | 150~220 | 油漆工 | 130~180 |
| 防水工 | 140~200 | 信号工 | 130~170 |

> 注: 以上为2024~2026年市场参考价，实际以当地造价信息为准

### 9.4 常用材料单价参考表

| 材料名称 | 规格 | 单位 | 单价(元) |
|---------|------|------|:---:|
| 商品混凝土 | C30 | m³ | 420~480 |
| 商品混凝土 | C35 | m³ | 460~520 |
| 商品混凝土 | C40 | m³ | 500~560 |
| 商品混凝土 | C50 | m³ | 560~640 |
| 水泥 | P.O 42.5 | t | 380~450 |
| 砂 | 中砂 | m³ | 120~180 |
| 碎石 | 5-31.5mm | m³ | 130~190 |
| 热轧带肋钢筋 | HRB400 Φ12-25 | t | 3800~4200 |
| 热轧光圆钢筋 | HPB300 Φ6-10 | t | 4000~4400 |
| 钢绞线 | Φ15.2 | t | 5500~6500 |
| 木模板 | 周转 | m² | 35~50 |
| 钢模板 | 周转 | kg | 4.5~6.0 |
| 脚手架钢管 | Φ48×3.5 | t | 3800~4500 |
| 标准砖 | 240×115×53 | 千块 | 400~550 |
| 加气混凝土砌块 | B06 A5.0 | m³ | 220~300 |
| 防水卷材 | SBS 3mm | m² | 25~38 |
| 沥青混凝土 | AC-13C | t | 550~700 |
| 水泥稳定碎石 | 5% | m³ | 180~240 |

### 9.5 机械台班单价参考表

| 机械名称 | 规格 | 台班单价(元) |
|---------|------|:---:|
| 履带式挖掘机 | 1.0m³ | 1800~2200 |
| 履带式挖掘机 | 0.6m³ | 1200~1600 |
| 轮式装载机 | 3.0m³ | 1000~1400 |
| 自卸汽车 | 15t | 600~900 |
| 混凝土泵车 | 56m | 2500~3500 |
| 混凝土搅拌车 | 12m³ | 800~1200 |
| 塔式起重机 | TC6010 | 1200~1800 |
| 施工电梯 | SC200/200 | 600~900 |
| 履带式起重机 | 50t | 2000~3000 |
| 振动压路机 | 18t | 800~1200 |

### 9.6 措施项目费计算

```python
def calculate_measure_cost(
    project_cost: float,
    project_type: str = 'building',
    area: float = 0,
) -> dict:
    """
    计算措施项目费
    依据: GB 50500-2013 第3.0.6条
    """
    # 安全文明施工费费率（按总造价百分比）
    safety_rates = {
        'building': 0.030,      # 房建 3.0%
        'municipal': 0.025,     # 市政 2.5%
        'highway': 0.020,       # 公路 2.0%
    }
    safety_rate = safety_rates.get(project_type, 0.025)

    safety_cost = project_cost * safety_rate  # 安全文明施工费

    # 夜间施工增加费
    night_cost = project_cost * 0.005 if project_type == 'building' else 0

    # 二次搬运费
    transport_cost = project_cost * 0.008

    # 冬雨季施工增加费
    seasonal_cost = project_cost * 0.010

    # 大型机械设备进出场及安拆费（按实际计列）
    equipment_mobilization = 0  # 按实际报价

    # 脚手架费（按建筑面积估算）
    scaffold_cost = area * 35 if area > 0 else project_cost * 0.015

    # 模板费（按混凝土量估算，一般在混凝土造价的15-25%）
    formwork_cost = project_cost * 0.020

    total = (safety_cost + night_cost + transport_cost +
             seasonal_cost + equipment_mobilization +
             scaffold_cost + formwork_cost)

    return {
        '安全文明施工费': round(safety_cost, 2),
        '夜间施工增加费': round(night_cost, 2),
        '二次搬运费': round(transport_cost, 2),
        '冬雨季施工增加费': round(seasonal_cost, 2),
        '大型机械进出场费': round(equipment_mobilization, 2),
        '脚手架费': round(scaffold_cost, 2),
        '模板费': round(formwork_cost, 2),
        '措施费合计': round(total, 2),
    }
```

### 9.7 规费与税金计算

```python
def calculate_regulation_and_tax(
    sub_project_cost: float,  # 分部分项工程费
    measure_cost: float,      # 措施项目费
    other_cost: float = 0,    # 其他项目费
    tax_method: str = 'general',  # 'general'(一般计税9%) / 'simple'(简易计税3%)
) -> dict:
    """
    计算规费和税金
    依据: GB 50500-2013 第3.0.7条、财税〔2018〕32号
    """
    base = sub_project_cost + measure_cost + other_cost

    # 规费费率
    regulation_rates = {
        '社保费': 0.032,       # 养老+医疗+失业+工伤+生育
        '住房公积金': 0.010,
        '工程排污费': 0.001,
    }

    regulation_cost = sum(base * rate for rate in regulation_rates.values())

    # 税前造价
    pre_tax = base + regulation_cost

    # 增值税率
    tax_rate = 0.09 if tax_method == 'general' else 0.03
    tax = pre_tax * tax_rate

    # 总造价
    total = pre_tax + tax

    return {
        '规费': {
            '社保费': round(base * regulation_rates['社保费'], 2),
            '住房公积金': round(base * regulation_rates['住房公积金'], 2),
            '工程排污费': round(base * regulation_rates['工程排污费'], 2),
            '规费合计': round(regulation_cost, 2),
        },
        '税金': {
            '计税方法': '一般计税' if tax_method == 'general' else '简易计税',
            '税率': f'{tax_rate*100:.0f}%',
            '税前造价': round(pre_tax, 2),
            '税金': round(tax, 2),
        },
        '工程总造价': round(total, 2),
    }
```

### 9.8 工程报价书生成

```python
def generate_bid_document(
    quantities: list,  # [(code, name, unit, qty, unit_price), ...]
    project_info: dict,
    output_path: str,
) -> str:
    """
    生成完整工程报价书（Excel）
    包含: 封面、分部分项清单、措施项目清单、规费税金汇总
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

    wb = Workbook()

    # === 封面 ===
    ws_cover = wb.active
    ws_cover.title = "封面"
    ws_cover['A1'] = "工程报价书"
    ws_cover['A1'].font = Font(name='宋体', size=24, bold=True)
    ws_cover.merge_cells('A1:F1')
    ws_cover['A3'] = f"工程名称: {project_info.get('name', '')}"
    ws_cover['A4'] = f"建设单位: {project_info.get('client', '')}"
    ws_cover['A5'] = f"施工单位: {project_info.get('contractor', '')}"
    ws_cover['A6'] = f"报价日期: {project_info.get('date', '')}"

    # === 分部分项工程量清单 ===
    ws_bq = wb.create_sheet("分部分项工程量清单")
    headers = ['序号', '清单编码', '项目名称', '项目特征', '计量单位',
               '工程量', '综合单价(元)', '合价(元)', '其中人工费', '备注']
    for col, h in enumerate(headers, 1):
        cell = ws_bq.cell(row=1, column=col, value=h)
        cell.font = Font(name='宋体', bold=True, size=10)
        cell.fill = PatternFill('solid', start_color='4472C4')
        cell.font = Font(name='宋体', bold=True, size=10, color='FFFFFF')
        cell.alignment = Alignment(horizontal='center')

    total_cost = 0
    for idx, (code, name, unit, qty, price) in enumerate(quantities, 1):
        subtotal = qty * price
        total_cost += subtotal
        row = idx + 1
        ws_bq.cell(row=row, column=1, value=idx)
        ws_bq.cell(row=row, column=2, value=code)
        ws_bq.cell(row=row, column=3, value=name)
        ws_bq.cell(row=row, column=6, value=unit)
        ws_bq.cell(row=row, column=7, value=qty)
        ws_bq.cell(row=row, column=8, value=price)
        ws_bq.cell(row=row, column=9, value=round(subtotal, 2))

    # 合计行
    sum_row = len(quantities) + 2
    ws_bq.cell(row=sum_row, column=3, value="合计").font = Font(bold=True)
    ws_bq.cell(row=sum_row, column=9, value=round(total_cost, 2)).font = Font(bold=True)

    # === 费用汇总表 ===
    ws_summary = wb.create_sheet("费用汇总表")
    measures = calculate_measure_cost(total_cost, project_info.get('type', 'building'),
                                       project_info.get('area', 0))
    reg_tax = calculate_regulation_and_tax(total_cost, measures['措施费合计'])

    summary_data = [
        ['1', '分部分项工程费', round(total_cost, 2)],
        ['2', '措施项目费', measures['措施费合计']],
        ['3', '其他项目费', 0],
        ['4', '规费', reg_tax['规费']['规费合计']],
        ['5', '税金', reg_tax['税金']['税金']],
        ['', '工程总造价', reg_tax['工程总造价']],
    ]
    for row_idx, (no, name, amount) in enumerate(summary_data, 1):
        ws_summary.cell(row=row_idx, column=1, value=no)
        ws_summary.cell(row=row_idx, column=2, value=name)
        ws_summary.cell(row=row_idx, column=3, value=amount)

    wb.save(output_path)
    return output_path
```

### 9.9 材料价差调整

```python
def calculate_material_price_adjustment(
    contract_prices: dict,  # {材料名: 合同单价}
    current_prices: dict,   # {材料名: 当前市场单价}
    quantities: dict,       # {材料名: 消耗量}
    adjustment_threshold: float = 0.05,  # ±5%以内不调整
) -> dict:
    """
    材料价差调整
    依据: 施工合同约定及工程造价信息
    """
    adjustments = []
    total_diff = 0

    for material, contract_price in contract_prices.items():
        current_price = current_prices.get(material, contract_price)
        qty = quantities.get(material, 0)
        diff_pct = (current_price - contract_price) / contract_price

        if abs(diff_pct) > adjustment_threshold:
            diff_amount = (current_price - contract_price) * qty
            adjustments.append({
                '材料名称': material,
                '合同单价': contract_price,
                '现行单价': current_price,
                '价差率': f'{diff_pct*100:.1f}%',
                '消耗量': qty,
                '价差金额': round(diff_amount, 2),
            })
            total_diff += diff_amount

    return {
        '调整明细': adjustments,
        '价差合计': round(total_diff, 2),
        '调整材料数': len(adjustments),
    }
```

---