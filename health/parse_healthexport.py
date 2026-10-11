# -*- coding: utf-8 -*-
"""解析 HealthExport 导出的健康 JSON，生成 Markdown 汇总。

数据链路（详见 health/README.md）：
  iPhone 健康 App（Apple Watch）→ HealthExport 每日后台导出 JSON → iCloud 云盘
  → 本机同步目录 → 本脚本解析 → 「健康数据汇总_YYYY-MM-DD.md」

用法：
  python parse_healthexport.py                # 默认读 iCloud 同步目录，输出到 ./output
  python parse_healthexport.py --input <目录>  # 指定 JSON 所在目录
  python parse_healthexport.py --output <目录> # 指定输出目录
  python parse_healthexport.py --sample        # 用仓库内脱敏示例数据跑通流程

依赖：仅 Python 标准库（json / glob / argparse）。
"""
import argparse
import glob
import json
import os
from datetime import datetime, timezone, timedelta

DEFAULT_INPUT = r'C:\Users\2024\iCloudDrive\iCloud~HealthExport\Health'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTPUT = os.path.join(BASE_DIR, 'output')
SAMPLE_DIR = os.path.join(BASE_DIR, 'sample')

CN_TZ = timezone(timedelta(hours=8))


def latest_json(input_dir):
    """取目录中最新的 health-*.json。"""
    files = glob.glob(os.path.join(input_dir, 'health-*.json'))
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def fmt_cn(iso_str):
    """ISO8601 → 北京时间 'MM-DD HH:MM'，解析失败原样返回。"""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        return dt.astimezone(CN_TZ).strftime('%m-%d %H:%M')
    except Exception:
        return iso_str or '-'


def build_report(data):
    """把解析后的 JSON 转成 Markdown 汇总。"""
    m = data.get('metrics', {})
    out = []
    out.append('# 健康数据汇总（HealthExport 自动导出）')
    out.append('')
    out.append(f"- 导出时间：{data.get('export_date', '')}（UTC，北京时间 +8h）")
    dr = data.get('date_range', {})
    out.append(f"- 数据范围：{str(dr.get('start', ''))[:10]} 至 {str(dr.get('end', ''))[:10]}")
    out.append('- 来源：iPhone 健康 App（Apple Watch 记录）→ HealthExport 每日自动导出 → iCloud 云盘')
    out.append('')

    # 运动记录
    wk = m.get('workouts', [])
    out.append('## 运动记录（Workouts）')
    if wk:
        out.append('')
        out.append('| 日期 | 类型 | 时长(分) | 距离(km) | 消耗(kcal) | 来源 |')
        out.append('|---|---|---|---|---|---|')
        for w in wk:
            dist = w.get('distance_km')
            dist_txt = f"{dist:.1f}" if isinstance(dist, (int, float)) else '-'
            out.append(
                f"| {w.get('date')} | {w.get('type')} | {w.get('duration_min', 0):.0f} "
                f"| {dist_txt} | {w.get('calories', 0)} | {w.get('source', '')} |"
            )
        total_min = sum(w.get('duration_min', 0) for w in wk)
        total_kcal = sum(w.get('calories', 0) for w in wk)
        out.append('')
        out.append(f"共 {len(wk)} 次运动，累计 {total_min:.0f} 分钟（{total_min / 60:.1f} 小时），消耗 {total_kcal} 千卡。")
    else:
        out.append('')
        out.append('（暂无运动记录）')
    out.append('')

    # 最近 7 天步数 / 活跃能量 / 心率
    steps = {x['date']: x['value'] for x in m.get('steps', [])}
    kcal = {x['date']: x['value'] for x in m.get('active_calories', [])}
    hr = {x['date']: x for x in m.get('heart_rate', [])}
    dates = sorted(steps.keys())[-7:]
    out.append('## 最近 7 天活动概况')
    out.append('')
    out.append('| 日期 | 步数 | 活跃能量(kcal) | 平均心率 | 最高心率 | 静息心率 |')
    out.append('|---|---|---|---|---|---|')
    for d in dates:
        h = hr.get(d, {})
        out.append(
            f"| {d} | {steps.get(d, '-')} | {kcal.get(d, '-')} "
            f"| {h.get('average_bpm', '-')} | {h.get('max_bpm', '-')} | {h.get('resting_bpm', '-')} |"
        )
    out.append('')

    # 睡眠（最近 3 条，含阶段明细）
    slp = sorted(m.get('sleep', []), key=lambda x: x.get('date', ''))
    out.append('## 睡眠（最近 3 晚，含阶段明细）')
    out.append('')
    if slp:
        out.append('| 日期 | 入睡(北京时间) | 醒来(北京时间) | 深睡(分) | 核心(分) | REM(分) | 清醒(分) |')
        out.append('|---|---|---|---|---|---|---|')
        for s in slp[-3:]:
            st = s.get('stages', {})
            total = st.get('deep_min', 0) + st.get('core_min', 0) + st.get('rem_min', 0)
            out.append(
                f"| {s.get('date')} | {fmt_cn(s.get('bed_start', ''))} | {fmt_cn(s.get('bed_end', ''))} "
                f"| {st.get('deep_min', 0)} | {st.get('core_min', 0)} | {st.get('rem_min', 0)} "
                f"| {st.get('awake_min', 0)}（合计 {total // 60}h{total % 60:02d}m） |"
            )
    else:
        out.append('（暂无睡眠记录）')
    out.append('')

    # 简评
    out.append('## 简评')
    out.append('')
    if steps:
        d_today = dates[-1]
        avg_steps = sum(steps.get(d, 0) for d in dates) // max(len(dates), 1)
        out.append(f"- 今日（{d_today}）：步数 {steps.get(d_today, '-')}，活跃能量 {kcal.get(d_today, '-')} 千卡。")
        out.append(f"- 最近 7 天日均步数约 {avg_steps}。")
    if wk:
        out.append('- 近期运动以步行和力量训练为主，详见上表。')
    if slp:
        last = slp[-1]
        st = last.get('stages', {})
        total = st.get('deep_min', 0) + st.get('core_min', 0) + st.get('rem_min', 0)
        if total > 0:
            out.append(
                f"- 最近一晚睡眠合计 {total // 60}h{total % 60:02d}m，"
                f"深睡占比 {st.get('deep_min', 0) / total * 100:.0f}%，REM 占比 {st.get('rem_min', 0) / total * 100:.0f}%。"
            )
    out.append('')
    out.append('> 数据来自 iPhone 健康 App 及 Apple Watch 记录，App 本地处理，无网络上传。')
    out.append('> 本汇总仅作个人记录与参考，不构成医疗建议。')
    return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description='解析 HealthExport JSON，生成健康数据 Markdown 汇总')
    parser.add_argument('--input', default=DEFAULT_INPUT, help='健康 JSON 所在目录')
    parser.add_argument('--output', default=DEFAULT_OUTPUT, help='Markdown 输出目录')
    parser.add_argument('--sample', action='store_true', help='使用仓库内脱敏示例数据（忽略 --input）')
    args = parser.parse_args()

    input_dir = SAMPLE_DIR if args.sample else args.input
    path = latest_json(input_dir)
    if not path:
        print(f'NO_FILE: {input_dir} 下未找到 health-*.json')
        return

    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs(args.output, exist_ok=True)
    out_name = f"健康数据汇总_{datetime.now(CN_TZ).strftime('%Y-%m-%d')}.md"
    out_path = os.path.join(args.output, out_name)
    content = build_report(data)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'源文件：{os.path.basename(path)}')
    print(f'已生成：{out_path}')
    print('---')
    print(content)


if __name__ == '__main__':
    main()
