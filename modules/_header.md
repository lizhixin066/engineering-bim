---
name: "engineering-bim"
version: "3.0.0"
description: "企业级大型工程综合技能：工程识图、工程量计算、CAD转BIM、造价计价、施工安全、碳排放与绿色建筑、施工组织与进度、Excel计算表生成。覆盖土建/市政/公路/幕墙/钢结构/隧道六大专业。当用户需要识图、算量、BIM建模、计价、安全验算、碳排放、进度计划、Excel计算表或涉及上述工程专业时调用。"
capabilities:
  - id: "drawing"
    name: "工程识图"
    module: "01-drawing.md"
    keywords: ["识图","读图","解析CAD","解析图纸","看图","提取尺寸","图纸对比","图层","DWG","DXF","图块"]
  - id: "quantity"
    name: "工程量计算"
    module: "02-quantity.md"
    keywords: ["算量","工程量","混凝土量","钢筋量","土方量","模板","脚手架","砌体","防水","保温","清单编码"]
  - id: "bim"
    name: "CAD转BIM"
    module: "03-bim.md"
    keywords: ["BIM","IFC","三维模型","Revit","CAD转BIM","翻模","碰撞检测","4D","5D","LOD"]
  - id: "standards"
    name: "规范标准"
    module: "04-standards.md"
    keywords: ["规范","标准","GB","JGJ","JTG","CJJ","图集","22G101","验收"]
  - id: "pricing"
    name: "造价计价"
    module: "09-pricing.md"
    keywords: ["计价","造价","报价","单价","综合单价","措施费","规费","税金","报价书","价差"]
  - id: "safety"
    name: "施工安全计算"
    module: "10-safety.md"
    keywords: ["安全","脚手架验算","模板支撑","基坑支护","塔吊基础","临边防护","临时用电"]
  - id: "carbon"
    name: "碳排放与绿色建筑"
    module: "11-carbon.md"
    keywords: ["碳排放","碳足迹","装配率","绿色建筑","绿建","能耗","节能","碳中和"]
  - id: "schedule"
    name: "施工组织与进度"
    module: "12-schedule.md"
    keywords: ["进度","工期","网络计划","关键路径","CPM","横道图","甘特图","挣值","EVM","资源均衡"]
  - id: "excel"
    name: "Excel计算表生成"
    module: "13-excel.md"
    keywords: ["Excel","计算表","表格","导出","报表","工作簿","openpyxl"]
disciplines:
  - id: "civil"
    name: "土建工程"
    codes: ["0101","0102","0103","0104","0105","0106","0107","0108","0109","0110","0111"]
  - id: "municipal"
    name: "市政工程"
    codes: ["0401","0402","0403","0404","0405","0406","0407","0408","0409","0410","0411","0412","0413"]
  - id: "highway"
    name: "公路工程"
    codes: ["JTG"]
  - id: "curtain_wall"
    name: "幕墙工程"
    codes: ["0110"]
  - id: "steel"
    name: "钢结构工程"
    codes: ["0106"]
  - id: "tunnel"
    name: "隧道工程"
    codes: ["0114"]
standards_count: 120
function_count: 67
---

# 企业级大型工程综合技能 (Engineering & BIM)

> **版本**: v3.0.0 企业级 | **更新**: 2026-07-12
> **模块数**: 15 | **函数数**: 67 | **规范数**: 120+
> 编辑任意 `modules/*.md` 后运行 `python assemble.py` 重新生成 SKILL.md

本技能为企业级大型工程综合工具，覆盖工程全生命周期八大核心能力：

| # | 能力 | 模块 | 核心函数数 |
|---|------|------|:---:|
| 1 | 工程识图 | 01-drawing.md | 6 |
| 2 | 工程量计算 | 02-quantity.md | 20 |
| 3 | CAD转BIM | 03-bim.md | 15 |
| 4 | 规范标准 | 04-standards.md | - |
| 5 | 工程造价计价 | 09-pricing.md | 5 |
| 6 | 施工安全计算 | 10-safety.md | 6 |
| 7 | 碳排放与绿色建筑 | 11-carbon.md | 4 |
| 8 | 施工组织与进度 | 12-schedule.md | 5 |
| 9 | Excel计算表生成 | 13-excel.md | 6 |

支持六大专业：**土建 / 市政 / 公路 / 幕墙 / 钢结构 / 隧道**

---