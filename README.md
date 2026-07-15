# weire-design-review

面向微热（Weire/Wira/Laboo）的证据化移动端设计评审 Plugin，同时支持 Codex 与 Claude。

它把产品目标、现网基线、微热品牌标准、既有设计系统与设计稿证据放在同一套流程中，输出可追溯的问题、评分和验证假设，而不是只给笼统的审美意见。

## 核心能力

- 支持截图、录屏、设计系统导出文件及 Figma 设计稿链接
- 对比新版与线上版本，明确 `better / same / worse / unknown`
- 从流程、页面、区域、组件、元素与状态六个层级检查设计
- 覆盖整体印象、易用性、视觉层级、一致性、无障碍性、亮点及优先建议
- 使用 `F-001` 形式输出“证据—影响—建议—验证”详细问题卡
- 针对微热检查品牌调性、颜色感知、视觉语言和设计系统一致性
- 按需编排 Codex Product Design 或 Claude Design 专家能力
- 将专家结论按“已采纳 / 待验证 / 未采纳”统一汇总、去重和追溯
- 通过脚本校验报告结构并生成确定性评分

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

### Claude Code

```bash
claude plugin marketplace add bluebone-ai/weire-design-review
claude plugin install weire-design-review@bluebone-ai
```

调用方式：

```text
/weire-design-review:weire-design-review 评审这张微热设计稿。
```

本地开发时也可以使用 `claude --plugin-dir ./plugins/weire-design-review`。

## 可选专家插件

本 Plugin 自身可独立完成微热评审。若当前宿主还提供设计专家能力，会把专家结论作为候选材料汇总进同一份报告，而不是另发一份互不关联的分析：

- Codex：Product Design 的 `audit` 等能力
- Claude：官方 Design Plugin 的 `design-critique`、`accessibility-review`、`design-system`、`ux-copy` 等能力

Claude Design 可单独安装：

```bash
claude plugin marketplace add anthropics/knowledge-work-plugins
claude plugin install design@knowledge-work-plugins
```

Design 保持可选依赖：未安装时核心评审继续运行，并在能力调用记录中标记 `unavailable`；安装后，已验证的专家结论写入 `specialist_synthesis`，再归并到最终问题卡或亮点。外部插件评分不会覆盖本 Plugin 的确定性评分。

## 推荐输入

进行改版对比时，建议同时提供：

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
