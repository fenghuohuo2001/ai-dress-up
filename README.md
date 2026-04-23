# AI 换装创作技能

## 功能
通过飞书机器人完成：角色形象确认 → 换装图生成 → 换装视频生成 → 抖音发布内容 的完整工作流。

## 文件结构

```
ai-dress-up/
├── SKILL.md                  # 主入口（总控规则、模板、错误处理）
├── config/
│   ├── workflow.md           # 步骤执行详情（A→B→C→D）
│   ├── prompt.md             # 提示词模板（换装图/视频/原始形象）
│   └── material_lib.yaml    # IP素材库（角色→风格映射）
└── api/
    ├── image_api.py          # 图片生成（generate_image / generate_dress_image / query_task_status）
    └── video_api.py          # 视频生成（generate_video / wait_for_video / query_task_status）
```

## 模型与收费
- 图片：qwen-image-2.0-pro，¥0.5/张
- 视频：wanx2.1-kf2v-plus，¥7.5/次（720P，5秒）

## API Key
环境变量 `MODELSTUDIO_API_KEY`，或写入 `~/.modelstudio_env`。
