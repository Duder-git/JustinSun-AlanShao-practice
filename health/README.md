# 观点 01：把生活 AI 化 —— 健康数据自动导入

> 方案来源：飞书文档《健康数据自动导入说明（HealthExport 方案）》。
> 核心思路（对谈原话）：饭前饭后拍照、训练录视频、睡眠数据，全部交给 AI，每天出一份报告；**资料都存成文件，换工具也不丢**。

## 数据链路

```
iPhone 健康 App（Apple Watch 记录）
  → HealthExport 每天后台自动导出 JSON
  → iCloud 云盘：iCloud~HealthExport/Health/health-YYYY-MM-DD_HHMMSS.json
  → Windows iCloud 同步：C:\Users\2024\iCloudDrive\iCloud~HealthExport\Health\
  → parse_healthexport.py 解析（自动取最新文件）
  → 生成「健康数据汇总_YYYY-MM-DD.md」
  → 交给 AI 生成每日健康日报（见 ai-daily-prompt.md）
```

## 覆盖指标

| 指标 | 内容 |
|---|---|
| 睡眠 | 每天一条：入睡/醒来时间 + 深睡/核心/REM/清醒 分钟数 |
| 运动 Workouts | 类型（步行/力量等）、时长、距离、消耗、来源设备 |
| 步数 | 每日步数 |
| 活跃能量 | 每日千卡 |
| 心率 | 平均 / 最高 / 静息 |

## 快速开始

```bash
# 1) 用脱敏示例数据跑通流程（无依赖，仅需 Python 3）
python health/parse_healthexport.py --sample

# 2) 解析你自己的 iCloud 健康数据（默认路径）
python health/parse_healthexport.py

# 3) 自定义输入 / 输出目录
python health/parse_healthexport.py --input "D:\HealthExport\Health" --output "D:\my-life\daily"
```

生成的 Markdown 在 `health/output/` 下（已 gitignore，不会提交个人数据）。

## 保活检查（数据中断时按此排查）

1. iPhone → 设置 → 通用 → **后台 App 刷新** → HealthExport 保持开启
2. 不要长期开启**低电量模式**（会暂停后台刷新）
3. 隔 2~3 天打开 HealthExport 看一眼「Last Export」时间；若太久没更新，点 **Export Now** 手动补一次
4. 首次导出为 30 天全量（sync_type: initial），之后每天增量一个新文件

## 说明

- 时间说明：HealthExport 后台刷新由 iOS 择机执行，导出时刻不固定属正常现象，数据按天完整、不丢失。
- 来源说明：所有数据来自 iPhone 健康 App 及 Apple Watch 记录，App 本地处理，无网络上传。
- 隐私说明：本仓库已通过 `.gitignore` 排除个人健康 JSON 与输出文件；`sample/` 中是脱敏示例，可直接删除。
- 本方案为个人健康记录与参考，不构成医疗建议。
