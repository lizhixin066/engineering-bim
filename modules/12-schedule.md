## 十二、施工组织与进度计划 (Construction Schedule & CPM)

> 依据: GB/T 50502-2009《建筑施工组织设计规范》、JGJ/T 132-2009《居住建筑节能检测标准》
> 方法: 网络计划技术(CPM/PERT)、横道图、资源动态曲线

---

### 12.1 双代号网络计划

```python
def build_cpm_network(tasks: list) -> dict:
    """
    双代号网络计划计算（关键路径法 CPM）
    tasks: [(task_id, name, duration_days, predecessors: list), ...]
    返回: 各任务最早开始/最早完成/最迟开始/最迟完成/总时差/自由时差 + 关键路径
    """
    # 构建任务字典
    task_map = {}
    for tid, name, duration, preds in tasks:
        task_map[tid] = {
            'id': tid, 'name': name, 'duration': duration,
            'predecessors': preds, 'successors': [],
        }
    # 构建后继关系
    for tid, task in task_map.items():
        for pred in task['predecessors']:
            if pred in task_map:
                task_map[pred]['successors'].append(tid)

    # 正向计算: 最早开始(ES)和最早完成(EF)
    calculated = set()
    max_iterations = len(task_map) * 2 + 10
    for _ in range(max_iterations):
        progress = False
        for tid, task in task_map.items():
            if tid in calculated:
                continue
            if all(p in calculated for p in task['predecessors']):
                if not task['predecessors']:
                    task['ES'] = 0
                else:
                    task['ES'] = max(task_map[p]['EF'] for p in task['predecessors'])
                task['EF'] = task['ES'] + task['duration']
                calculated.add(tid)
                progress = True
        if not progress:
            break
        if len(calculated) == len(task_map):
            break

    # 项目总工期
    project_duration = max((t.get('EF', 0) for t in task_map.values()), default=0)

    # 逆向计算: 最迟开始(LS)和最迟完成(LF)
    late_calculated = set()
    for tid, task in task_map.items():
        if not task['successors']:
            task['LF'] = project_duration
            task['LS'] = task['LF'] - task['duration']
            late_calculated.add(tid)

    for _ in range(max_iterations):
        progress = False
        for tid, task in task_map.items():
            if tid in late_calculated:
                continue
            if all(s in late_calculated for s in task['successors']):
                if task['successors']:
                    task['LF'] = min(task_map[s]['LS'] for s in task['successors'])
                else:
                    task['LF'] = project_duration
                task['LS'] = task['LF'] - task['duration']
                late_calculated.add(tid)
                progress = True
        if not progress:
            break
        if len(late_calculated) == len(task_map):
            break

    # 计算时差
    for tid, task in task_map.items():
        task['TF'] = task.get('LF', 0) - task.get('EF', 0)  # 总时差
        # 自由时差 FF = min(ES_successors) - EF
        if task['successors']:
            min_es_succ = min(task_map[s]['ES'] for s in task['successors'])
            task['FF'] = min_es_succ - task['EF']
        else:
            task['FF'] = project_duration - task['EF']

    # 关键路径: TF=0 的任务
    critical_path = [tid for tid, task in task_map.items() if task.get('TF', 0) == 0]

    return {
        'tasks': {tid: {
            'name': t['name'],
            'duration': t['duration'],
            'ES': t.get('ES', 0), 'EF': t.get('EF', 0),
            'LS': t.get('LS', 0), 'LF': t.get('LF', 0),
            'TF': t.get('TF', 0), 'FF': t.get('FF', 0),
            'is_critical': t.get('TF', 0) == 0,
        } for tid, t in task_map.items()},
        'project_duration': project_duration,
        'critical_path': critical_path,
    }
```

### 12.2 横道图（甘特图）生成

```python
def generate_gantt_chart(
    cpm_result: dict,
    output_path: str = None,
    start_date: str = '2026-01-01',
) -> str:
    """
    生成横道图(甘特图) — 使用matplotlib
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, '%Y-%m-%d')
    tasks = cpm_result['tasks']

    # 按最早开始时间排序
    sorted_tasks = sorted(tasks.items(), key=lambda x: x[1]['ES'])

    fig, ax = plt.subplots(figsize=(16, max(6, len(sorted_tasks) * 0.4)))

    y_positions = []
    y_labels = []
    for i, (tid, task) in enumerate(sorted_tasks):
        y = len(sorted_tasks) - i - 1
        y_positions.append(y)
        y_labels.append(f"{tid} {task['name']}")

        start_day = start + timedelta(days=task['ES'])
        duration = task['duration']

        # 关键路径红色，非关键蓝色
        color = '#FF4444' if task['is_critical'] else '#4488CC'
        ax.barh(y, duration, left=task['ES'], height=0.6,
                color=color, alpha=0.8, edgecolor='black', linewidth=0.5)

        # 标注工期
        ax.text(task['ES'] + duration / 2, y, f"{task['duration']}d",
                ha='center', va='center', fontsize=7, color='white', fontweight='bold')

    ax.set_yticks(y_positions)
    ax.set_yticklabels(y_labels, fontsize=8)
    ax.set_xlabel('日期', fontsize=10)
    ax.set_title(f'施工进度横道图 (总工期: {cpm_result["project_duration"]}天)', fontsize=12)

    # X轴日期格式
    max_days = cpm_result['project_duration']
    ax.set_xlim(-1, max_days + 5)
    week_ticks = list(range(0, max_days + 7, 7))
    week_labels = [(start + timedelta(days=d)).strftime('%m-%d') for d in week_ticks]
    ax.set_xticks(week_ticks)
    ax.set_xticklabels(week_labels, fontsize=7, rotation=45)

    ax.grid(axis='x', alpha=0.3)
    ax.legend(['关键路径', '非关键路径'], loc='upper right', fontsize=8)

    plt.tight_layout()
    if output_path:
        plt.savefig(output_path, dpi=150)
        plt.close()
        return output_path
    else:
        plt.close()
        return None
```

### 12.3 资源动态曲线

```python
def calculate_resource_curve(
    cpm_result: dict,
    resources: dict,  # {task_id: (workers, cost_per_day)}, 每日人工/费用
    resource_type: str = 'workers',  # 'workers'/'cost'
) -> dict:
    """
    资源动态曲线计算
    返回每日资源需求量，用于绘制资源动态曲线和峰值分析
    """
    duration = cpm_result['project_duration']
    daily_resource = [0] * (duration + 1)

    for tid, task in cpm_result['tasks'].items():
        if tid in resources:
            r = resources[tid]
            daily_amount = r if isinstance(r, (int, float)) else r[0] if resource_type == 'workers' else r[1]
            for day in range(int(task['ES']), int(task['EF'])):
                if day < len(daily_resource):
                    daily_resource[day] += daily_amount

    peak = max(daily_resource)
    peak_day = daily_resource.index(peak)
    avg = sum(daily_resource) / max(duration, 1)

    # 不均衡系数
    imbalance = peak / avg if avg > 0 else 0

    return {
        'daily_resource': daily_resource,
        'peak_value': peak,
        'peak_day': peak_day,
        'average': round(avg, 1),
        'imbalance_factor': round(imbalance, 2),
        'duration': duration,
        '评价': '均衡' if imbalance < 1.5 else '不均衡，需优化',
    }
```

### 12.4 工期优化与资源均衡

```python
def optimize_resource_leveling(
    cpm_result: dict,
    resources: dict,
    max_iterations: int = 100,
) -> dict:
    """
    资源均衡优化（启发式方法）
    将非关键工作在时差范围内移动，使资源需求更均衡
    依据: 工期固定-资源均衡问题(RCPSP)
    """
    tasks = dict(cpm_result['tasks'])
    duration = cpm_result['project_duration']

    # 初始资源曲线
    initial = calculate_resource_curve(cpm_result, resources)

    best_schedule = {tid: {'ES': t['ES']} for tid, t in tasks.items()}
    best_variance = _resource_variance(initial['daily_resource'])

    # 尝试移动非关键任务
    for _ in range(max_iterations):
        improved = False
        non_critical = [(tid, t) for tid, t in tasks.items()
                        if not t['is_critical'] and t['TF'] > 0]

        for tid, task in non_critical:
            original_es = best_schedule[tid]['ES']
            best_shift = 0

            for shift in range(0, int(task['TF']) + 1):
                best_schedule[tid]['ES'] = original_es + shift
                temp_cpm = _rebuild_schedule(tasks, best_schedule, duration)
                temp_curve = calculate_resource_curve(temp_cpm, resources)
                v = _resource_variance(temp_curve['daily_resource'])
                if v < best_variance:
                    best_variance = v
                    best_shift = shift

            best_schedule[tid]['ES'] = original_es + best_shift
            if best_shift > 0:
                improved = True

        if not improved:
            break

    # 最终结果
    final_cpm = _rebuild_schedule(tasks, best_schedule, duration)
    final_curve = calculate_resource_curve(final_cpm, resources)

    return {
        '优化前峰值': initial['peak_value'],
        '优化后峰值': final_curve['peak_value'],
        '优化前不均衡系数': initial['imbalance_factor'],
        '优化后不均衡系数': final_curve['imbalance_factor'],
        '改善率': f'{(1 - best_variance / _resource_variance(initial["daily_resource"]))*100:.1f}%',
        '优化后日程': best_schedule,
        '评价': '优化效果显著' if initial['imbalance_factor'] - final_curve['imbalance_factor'] > 0.2 else '优化效果一般',
    }

def _resource_variance(daily: list) -> float:
    """计算资源方差的Σ(Ri - Ravg)²"""
    n = len(daily)
    avg = sum(daily) / max(n, 1)
    return sum((r - avg) ** 2 for r in daily)

def _rebuild_schedule(tasks: dict, schedule: dict, duration: int) -> dict:
    """根据新的ES重建CPM结果"""
    result_tasks = {}
    for tid, task in tasks.items():
        es = schedule[tid]['ES']
        result_tasks[tid] = {
            **task,
            'ES': es,
            'EF': es + task['duration'],
            'is_critical': task['is_critical'],
        }
    return {'tasks': result_tasks, 'project_duration': duration, 'critical_path': []}
```

### 12.5 标准施工工序模板

```python
# 常见工程类型的标准工序分解
STANDARD_SEQUENCES = {
    'building': [
        # (工序号, 名称, 工期(天), 紧前工序)
        ('A', '施工准备', 7, []),
        ('B', '土方开挖', 15, ['A']),
        ('C', '基坑支护', 20, ['B']),
        ('D', '基础垫层', 3, ['C']),
        ('E', '基础施工', 25, ['D']),
        ('F', '地下室外墙', 15, ['E']),
        ('G', '±0.000以下回填', 5, ['F']),
        ('H', '一层结构', 12, ['G']),
        ('I', '二层结构', 12, ['H']),
        ('J', '主体结构(标准层)', 10, ['I']),
        ('K', '屋面工程', 15, ['J']),
        ('L', '砌筑工程', 30, ['J']),
        ('M', '抹灰工程', 25, ['L']),
        ('N', '门窗安装', 20, ['M']),
        ('O', '外墙装饰', 20, ['K', 'N']),
        ('P', '室内精装', 40, ['M', 'N']),
        ('Q', '机电安装', 45, ['J']),
        ('R', '电梯安装', 20, ['Q']),
        ('S', '室外工程', 15, ['O', 'P']),
        ('T', '竣工验收', 7, ['Q', 'R', 'S']),
    ],
    'highway': [
        ('A', '施工准备', 10, []),
        ('B', '路基清表', 15, ['A']),
        ('C', '路基填筑', 60, ['B']),
        ('D', '涵洞施工', 30, ['B']),
        ('E', '路基排水', 20, ['C']),
        ('F', '底基层施工', 25, ['C', 'D']),
        ('G', '基层施工', 20, ['F']),
        ('H', '面层施工', 30, ['G']),
        ('I', '桥梁基础', 45, ['A']),
        ('J', '桥梁下部结构', 40, ['I']),
        ('K', '桥梁上部结构', 60, ['J']),
        ('L', '桥面系', 20, ['K', 'H']),
        ('M', '交通安全设施', 15, ['H', 'L']),
        ('N', '绿化工程', 20, ['E', 'H']),
        ('O', '交工验收', 7, ['M', 'N']),
    ],
    'tunnel': [
        ('A', '施工准备', 10, []),
        ('B', '洞口工程', 15, ['A']),
        ('C', '超前支护', 10, ['B']),
        ('D', '上台阶开挖', 180, ['C']),
        ('E', '下台阶开挖', 150, ['D']),
        ('F', '初期支护', 160, ['D']),
        ('G', '防水层', 140, ['F']),
        ('H', '二次衬砌', 150, ['G']),
        ('I', '仰拱填充', 130, ['E']),
        ('J', '水沟电缆槽', 60, ['H', 'I']),
        ('K', '路面工程', 30, ['J']),
        ('L', '机电安装', 40, ['J']),
        ('M', '装饰装修', 25, ['K']),
        ('N', '竣工验收', 7, ['L', 'M']),
    ],
}

def get_standard_sequence(project_type: str) -> list:
    """获取标准施工工序模板"""
    return STANDARD_SEQUENCES.get(project_type, STANDARD_SEQUENCES['building'])
```

### 12.6 进度跟踪与偏差分析

```python
def track_schedule_progress(
    cpm_result: dict,
    actual_progress: dict,  # {task_id: 实际完成百分比(0~1)}
    current_day: int,
) -> dict:
    """
    进度跟踪与偏差分析（挣值法 EVM）
    依据: GB/T 50502-2009 附录B
    """
    tasks = cpm_result['tasks']
    total_duration = cpm_result['project_duration']

    # 计划价值 PV (Plan Value) — 计划完成百分比
    pv = 0
    for tid, task in tasks.items():
        planned = min(max((current_day - task['ES']) / max(task['duration'], 1), 0), 1)
        pv += planned * task['duration']

    # 挣值 EV (Earned Value) — 实际完成百分比
    ev = 0
    for tid, task in tasks.items():
        actual = actual_progress.get(tid, 0)
        ev += actual * task['duration']

    # 实际成本 AC (Actual Cost) — 简化: 按天数计
    ac = current_day  # 简化: 实际消耗时间

    # 偏差分析
    sv = ev - pv  # 进度偏差 (正值=提前)
    cv = ev - ac  # 成本偏差 (正值=节约)

    # 绩效指数
    spi = ev / pv if pv > 0 else 0  # 进度绩效指数 (SPI>1=提前)
    cpi = ev / ac if ac > 0 else 0  # 成本绩效指数 (CPI>1=节约)

    # 预测完工工期
    estimated_total = total_duration / spi if spi > 0 else total_duration
    remaining_days = estimated_total - current_day

    # 偏差状态判断
    if spi >= 1.0:
        status = '进度正常或提前'
    elif spi >= 0.9:
        status = '进度轻微滞后'
    elif spi >= 0.8:
        status = '进度滞后，需关注'
    else:
        status = '进度严重滞后，需采取措施'

    return {
        '当前日期': f'第{current_day}天',
        '计划工期': f'{total_duration}天',
        '计划价值PV': f'{pv:.1f} 工日',
        '挣值EV': f'{ev:.1f} 工日',
        '实际成本AC': f'{ac} 工日',
        '进度偏差SV': f'{sv:.1f} 工日 ({"提前" if sv > 0 else "滞后"})',
        '成本偏差CV': f'{cv:.1f} 工日',
        '进度绩效指数SPI': f'{spi:.3f}',
        '成本绩效指数CPI': f'{cpi:.3f}',
        '预测完工工期': f'{estimated_total:.0f}天',
        '剩余工期': f'{remaining_days:.0f}天',
        '进度状态': status,
        '建议': _schedule_suggestion(spi, cpi),
    }

def _schedule_suggestion(spi: float, cpi: float) -> str:
    """进度建议"""
    suggestions = []
    if spi < 0.9:
        suggestions.append('增加人力/机械投入，优化关键路径工序')
    if spi < 0.8:
        suggestions.append('考虑平行施工或夜间加班')
    if cpi < 0.9:
        suggestions.append('成本超支，审查资源使用效率')
    if not suggestions:
        suggestions.append('进度正常，继续保持')
    return '；'.join(suggestions)
```

---