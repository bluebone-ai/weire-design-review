# weire-design-review

面向微热（Weire/Wira/Laboo）的证据化移动端设计评审 Plugin，同时支持 Codex 与 Claude。

它把产品目标、现网基线、微热品牌标准、既有设计系统与设计稿证据放在同一套流程中，输出可追溯的问题、评分和验证假设，而不是只给笼统的审美意见。

## 核心能力

- 支持截图、录屏、设计系统导出文件及 Figma 设计稿链接
- 单独提交设计稿且未说明目标时，必须先确认设计目标与成功标准，再开始评审
- 对比新版与线上版本，明确 `better / same / worse / unknown`
- 从流程、页面、区域、组件、元素与状态六个层级检查设计
- 默认输出设计师简版：当前得分与开发准入、优先改稿清单、需要保留的设计和修改后复审条件
- 面向设计师的报告统一使用简体中文，不再显示中英双语标题或严重等级
- 使用 `F-001` 形式输出“位置—具体问题—影响—优化动作—完成标准”的可执行问题卡
- 完整审计仍保留整体印象、易用性、视觉层级、一致性、无障碍性、亮点、覆盖矩阵、专家结论及能力日志，并在明确要求时展开
- 针对微热检查品牌调性、颜色感知、视觉语言和设计系统一致性
- 每次评审强制运行当前宿主的设计专家基线：Codex Product Design `audit` 或 Claude Design `design-critique`
- 先让当前平台专家完整评审，再通过维度覆盖矩阵自适应补齐本次未充分检查的微热维度
- Codex 侧常见补齐色彩、品牌和视觉语言；Claude 侧常见补齐任务、入口理解、基线保留、状态与指标，实际路由以当轮覆盖缺口为准
- 将专家结论按“已采纳 / 待验证 / 未采纳”统一汇总、去重和追溯
- 通过脚本校验报告结构并生成确定性评分
- 自动输出开发准入结论：85 分为正常开发线，70–84 分有条件进入，低于 70 分先调整设计

## 安装

### Codex

```bash
codex plugin marketplace add bluebone-ai/weire-design-review
codex plugin add weire-design-review@bluebone-ai
```

调用方式：

```text
使用 $weire-design-review 评审这张微热设计稿。
```

默认返回设计师简版。需要完整评分维度、覆盖矩阵和能力调用记录时，可以说：

```text
使用 $weire-design-review 输出这张设计稿的完整审计报告。
```

### Claude Code

```bash
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin marketplace add bluebone-ai/weire-design-review
claude plugin install weire-design-review@bluebone-ai
```

调用方式：

```text
/weire-design-review:weire-design-review 评审这张微热设计稿。
```

默认同样返回设计师简版；明确要求“完整审计报告”时才展开全部维度与附录。

本地开发时也可以使用 `claude --plugin-dir ./plugins/weire-design-review`。

## 强制专家基线

本 Plugin 的微热规则负责证据、品牌、维度覆盖、问题归并与确定性评分；每轮评审还必须成功运行当前宿主的独立设计专家，并把专家结论汇总进同一份报告：

- Codex：每次运行 Product Design `audit`
- Claude：每次运行官方 Design Plugin `design-critique`
- Claude 的 `accessibility-review`、`design-system`、`ux-copy` 等仍按证据条件追加

原生专家先不受限制地完成本轮分析。随后 Plugin 将每个适用维度标记为 `full / partial / missing / unsupported`，仅对 `partial` 或 `missing` 维度运行 `Wira adaptive complement`。该补充是微热专属检查，不会伪装成另一平台的专家能力。

Claude 安装会声明对官方 Design Plugin 的跨 Marketplace 依赖。首次安装前需要先添加其 Marketplace：

```bash
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin install design@knowledge-work-plugins
```

宿主原生专家未安装、不可见或调用失败时，本轮报告不得输出最终评分；应先恢复依赖后重新评审。另一平台的专家能力受宿主隔离，记录为 `unavailable`，不视为漏调用。已验证的专家结论写入 `specialist_synthesis`，再归并到最终问题卡或亮点；外部插件评分不会覆盖本 Plugin 的确定性评分。

## 推荐输入

只提交截图、视频或 Figma 链接且未说明目标时，Plugin 会先询问：

> 本次设计希望让用户行为、使用体验或品牌感受发生什么变化？什么指标或可观察结果代表成功？

目标确认前不会运行设计专家、输出问题或评分。进行改版对比时，建议同时提供：

- 本轮唯一核心目标及主指标
- 护栏指标
- 线上版本截图或录屏
- 新版设计稿
- 本轮主要变量与保持不变的部分

## 目录结构

```text
weire-design-review/
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
└── plugins/weire-design-review/
    ├── .codex-plugin/plugin.json
    ├── .claude-plugin/plugin.json
    └── skills/weire-design-review/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/
        └── scripts/review_score.py
```

两端共用 `skills/weire-design-review/` 这一份评审逻辑。仓库不包含用户上传的截图、录屏或本机设计系统源文件。

## 报告校验与评分

```bash
python3 plugins/weire-design-review/skills/weire-design-review/scripts/review_score.py path/to/review.json --write
```

报告 JSON 需符合 `plugins/weire-design-review/skills/weire-design-review/references/result-schema.md`。评分仅汇总有证据支持且适用的维度；缺少证据的维度使用 `N/A`，不会被当作零分。

`review.output_mode` 支持两种呈现：

- `designer_summary`：默认。给设计师直接用于改稿和复审。
- `audit_full`：按需。包含完整证据、维度评分、覆盖矩阵、专家汇总与能力日志。

两种模式共用同一份底层评审 JSON 和确定性评分；简版只减少展示复杂度，不减少检查范围。在支持文件输出的环境中，Plugin 应同时保存简版 Markdown、完整审计 Markdown 和评分 JSON。

设计师可见报告固定使用 `zh-CN`。内部 JSON 字段、稳定 ID 和能力名称继续保留机器可读格式，不会出现在默认简版的双语标题中。

## 发布与更新

先用 dry run 检查下一版本，再执行正式发版：

```bash
./scripts/release.sh patch --dry-run
./scripts/release.sh patch
```

`patch`、`minor`、`major` 遵循语义化版本。正式发版会要求工作区干净，同步更新 Codex 与 Claude 版本，运行便携校验及本机可用的官方校验器，创建版本提交和 Git Tag，原子推送到 GitHub，并更新本机两端安装。

可选参数：

- `--no-push`：只创建本地发布提交和 Tag
- `--skip-local-update`：不更新本机 Codex 与 Claude 安装

每次 Push 和 Pull Request 还会通过 GitHub Actions 检查双平台版本一致性、Marketplace 路径、Skill 结构、本地 Markdown 引用和评分脚本语法。
