# AI 换装创作技能

> 通过飞书机器人完成：角色形象确认 → 换装图生成 → 换装视频生成 → 抖音发布内容 的完整工作流。

---

## 一、快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API Key

**方式一：环境变量**
```bash
export MODELSTUDIO_API_KEY=你的阿里云百炼API_KEY
```

**方式二：写入配置文件**
```bash
echo "MODELSTUDIO_API_KEY=你的阿里云百炼API_KEY" > ~/.modelstudio_env
```

> ⚠️ API Key 获取地址：[阿里云百炼控制台](https://bailian.console.aliyun.com/)
> - 点击「API-KEY管理」→ 创建或查看已有 Key
> - 注意：免费额度用完后需关闭「仅使用免费额度」模式

### 3. 启动换装模式

在飞书机器人对话中发送：
```
启动换装创作模式
```

---

## 二、功能流程

```
素材确认 → 初始化（创建飞书云文档） → 生成换装图 → 生成换装视频 → 抖音发布内容
```

### 支持角色
| 角色 | 风格 | 适合衣物 |
|------|------|---------|
| 羲和 | 古风神话 | 汉服、唐装 |
| 常羲 | 国风神话/清冷仙女 | 仙女装、白裙 |
| 霓裳 | 仙侠飘逸 | 纱衣、道袍 |
| 星辰 | 赛博朋克 | 未来感服装 |
| 都市 | 现代简约 | 时装、休闲装 |

---

## 三、模型与收费

| 类型 | 模型 | 价格 |
|------|------|------|
| 换装图 | qwen-image-2.0-pro | ¥0.5/张 |
| 换装视频 | wanx2.1-kf2v-plus | ¥7.5/次（720P，5秒） |

> 💰 具体费用以[阿里云百炼控制台](https://bailian.console.aliyun.com/)实际扣费为准

---

## 四、文件结构

```
ai-dress-up/
├── SKILL.md                  # 主入口（总控规则、模板、错误处理）
├── README.md                 # 本文件
├── config/
│   ├── workflow.md           # 步骤执行详情
│   ├── prompt.md             # 提示词模板
│   └── material_lib.yaml     # IP素材库
└── api/
    ├── image_api.py          # 图片生成 API
    └── video_api.py          # 视频生成 API
```

---

## 五、API 调用示例

```python
import sys
sys.path.insert(0, '/path/to/ai-dress-up/api')

# 生成原始形象（纯文字）
from image_api import generate_image
result = generate_image(prompt="常羲，月神，银白长发...")

# 双参考图生成换装图
from image_api import generate_dress_image
result = generate_dress_image(char_image_path, cloth_image_path, prompt)

# 生成换装视频
from video_api import generate_video, wait_for_video
result = generate_video(first_frame_path, last_frame_path, prompt)
if result["status"] != "failed":
    final = wait_for_video(result["task_id"])
```

---

## 六、相关链接

- [阿里云百炼控制台](https://bailian.console.aliyun.com/) - API Key 管理与充值
- [OpenClaw 文档](https://docs.openclaw.ai/) - 飞书机器人配置
- [抖音创作者中心](https://creator.douyin.com/) - 内容发布

---

*本 Skill 配合飞书机器人使用，详见 SKILL.md*
