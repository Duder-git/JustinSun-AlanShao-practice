# JustinSun-AlanShao-practice

> 跟随《对话孙宇晨：年轻人如何抓住 AI 时代的机会》的落地实践项目
> 把 4 小时对谈里的观点，变成一个一个能跑起来的代码、流程和工具

## 项目简介

本项目素材来自孙宇晨（Justin Sun）与邵艾伦（Alan Shao）的一场 4 小时对谈（B 站 4h17m 完整版），由笔记仓库整理出 15 个核心观点。本仓库不重复讲故事，而是把观点逐个**实现为可运行的代码和可照做的流程**，每实现一个观点就沉淀一个可复用的实践模块。

**当前进度**：观点 01「把生活 AI 化」已实现（健康数据自动导入 → AI 日报）。

## 已实现：观点 01 把生活 AI 化

> 对谈原话（约 00:01:57）：饭前饭后拍照、训练录视频、睡眠数据，全部交给 AI，每天出一份报告。**资料都存成文件，换工具也不丢。**

方案参考飞书文档《健康数据自动导入说明（HealthExport 方案）》，落地为一条全自动链路：

```
iPhone 健康 App（Apple Watch 记录）
  → HealthExport 每天后台自动导出 JSON → iCloud 云盘
  → Windows iCloud 同步到本地目录
  → parse_healthexport.py 解析（自动取最新文件）
  → 生成「健康数据汇总_YYYY-MM-DD.md」
  → 交给 AI 生成每日健康日报（prompt 模板见 ai-daily-prompt.md）
```

**覆盖指标**：睡眠（阶段明细）、运动 Workouts、步数、活跃能量、心率（平均/最高/静息）。

### 快速开始

```bash
# 用脱敏示例数据跑通流程（仅需 Python 3，无第三方依赖）
python health/parse_healthexport.py --sample

# 解析自己的 iCloud 健康数据（默认读取 iCloud 同步目录）
python health/parse_healthexport.py

# 自定义输入 / 输出目录
python health/parse_healthexport.py --input "D:\HealthExport\Health" --output "D:\my-life\daily"
```

生成汇总后，把 Markdown 全文复制给任意 AI（模板见 `health/ai-daily-prompt.md`），即可得到今日健康日报。详细说明见 [`health/README.md`](health/README.md)。

### 仓库结构

```
├── health/                    # 观点 01：把生活 AI 化
│   ├── README.md              # 方案说明：数据链路、保活检查、快速开始
│   ├── parse_healthexport.py  # 解析脚本（HealthExport JSON → Markdown 汇总）
│   ├── ai-daily-prompt.md     # 交给 AI 生成每日健康日报的 prompt 模板
│   └── sample/                # 脱敏示例数据（用于跑通流程）
├── .gitignore                 # 排除个人健康数据，保护隐私
└── README.md
```

## 路线图（对谈 15 个观点，逐步实现）

| # | 观点 | 一句话做法 | 状态 |
| --- | --- | --- | --- |
| 01 | 把生活 AI 化 | 建文件夹，让 AI 每天写日报 | ✅ 已实现（health/） |
| 02 | 没钱也能开始 | 用免费额度，把重复的事交给 AI | ⏳ 待实现 |
| 03 | 先升级操作系统 | 写下看法，找资料验证 | ⏳ 待实现 |
| 04 | 百分之百相信 AI | 同一问题问多个模型，挑最好的做 | ⏳ 待实现 |
| 05 | 商机全球找 | 去海外论坛看你这行的人在抱怨什么 | ⏳ 待实现 |
| 06 | 先探路，再下注 | 多找候选，先小实验再投入 | ⏳ 待实现 |
| 07 | 身体是本钱 | 手环数据交给 AI 盯趋势 | ⏳ 待实现（可复用 health/） |
| 08 | 逐水草而居 | 搞清楚机会大多在哪个城市 | ⏳ 待实现 |
| 09 | 机器读得懂才值钱 | 常用资料转成 Markdown | ⏳ 待实现 |
| 10 | 内容和投资不用二选一 | 分两个文件夹各记各的 | ⏳ 待实现 |
| 11 | Small ego | 让 AI 站反对面反驳你 | ⏳ 待实现 |
| 12 | 先自由，后财富 | 翻账单，算出缓冲金 | ⏳ 待实现 |
| 13 | 游戏版本会更新 | 订阅一手信息源，让 AI 帮看变化 | ⏳ 待实现 |
| 14 | 缺啥补啥 | 给自己出目标岗位的模拟题 | ⏳ 待实现 |
| 15 | 多创造，少消费 | 把搞懂的东西写成教程发出去 | ⏳ 待实现 |

## 参考资料

| 资料 | 链接 | 用途 |
| --- | --- | --- |
| 对话视频（B 站，约 4h17m） | https://www.bilibili.com/video/BV1fcHD6cEw3/ | 看原话、定位讨论主题 |
| 对谈笔记仓库 | https://github.com/wousp112/justin-sun-alan-shao-ai-notes | 全文逐字稿、精华、15 篇教程、AGENT.md |
| 健康数据自动导入说明 | 飞书文档（HealthExport 方案） | 观点 01 的方案来源 |

## 说明与免责声明

- 本项目为个人学习 / 练习项目，观点整理自对谈视频与笔记仓库，引用请注明出处。
- 访谈内容版权归原作者（邵艾伦 / 孙宇晨）所有；笔记仓库内容按仓库 LICENSE 使用。
- 对话涉及投资、健康等内容为嘉宾个人观点分享；健康模块的数据与分析仅供参考，不构成医疗建议。
