# weire-design-review

面向微热（Weire/Wira/Laboo）的证据化移动端设计评审 Skill。

它把产品目标、现网基线、微热品牌标准、既有设计系统与设计稿证据放在同一套流程中，输出可追溯的问题、评分和验证假设，而不是只给笼统的审美意见。

## 核心能力

- 支持截图、录屏、设计系统导出文件及 Figma 设计稿链接
- 对比新版与线上版本，明确 `better / same / worse / unknown`
- 从流程、页面、区域、组件、元素与状态六个层级检查设计
- 覆盖整体印象、易用性、视觉层级、一致性、无障碍性、亮点及优先建议
- 使用 `F-001` 形式输出“证据—影响—建议—验证”详细问题卡
- 针对微热检查品牌调性、颜色感知、视觉语言和设计系统一致性
- 按需编排 Codex Product Design 或 Claude Design 专家能力，并统一去重、归因和评分
- 通过脚本校验报告结构并生成确定性评分

## 使用方式

在 Codex 中提供设计稿及评审目标，然后调用：

```text
使用 $weire-design-review 评审这张微热设计稿。
```

进行改版对比时，建议同时提供：

- 本轮唯一核心目标及主指标
- 护栏指标
- 线上版本截图或录屏
- 新版设计稿
- 本轮主要变量与保持不变的部分

## 目录结构

```text
weire-design-review/
├── SKILL.md
├── agents/openai.yaml
├── references/
└── scripts/review_score.py
```

`references/` 包含微热品牌标准、产品上下文、评审框架、颜色感知审计、多层级审查和报告规范。仓库不包含用户上传的截图、录屏或本机设计系统源文件。

## 报告校验与评分

```bash
python3 scripts/review_score.py path/to/review.json --write
```

报告 JSON 需符合 `references/result-schema.md`。评分仅汇总有证据支持且适用的维度；缺少证据的维度使用 `N/A`，不会被当作零分。
