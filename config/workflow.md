# 换装创作执行流程

启动时读取本文件，按当前步骤执行。每步完成后回到 SKILL.md 执行「结果处理」和「自查」。

---

## 步骤 A：生成原始形象（可选，仅当用户无原图时执行）

### 触发条件
用户没有角色原图，且 `config/material_lib.yaml` 中也没有该角色的参考图。

### 执行流程
1. **收费确认**（必须先发，等用户确认）：
   ```
   原始形象将使用 qwen-image-2.0-pro 模型生成，¥0.5/张。确认生成？
   ```

2. **构造提示词**：读取 `config/prompt.md` 第三节「原始形象生成提示词」模板，根据角色名、风格、外貌填写

3. **展示提示词给用户确认**：
   ```
   原始形象提示词如下，请确认或修改：
   ---
   {提示词}
   ---
   模型：qwen-image-2.0-pro | 费用：¥0.5
   ```

4. **调用 API**（同步，约60-90秒）：
   ```python
   # sys.path 已在 SKILL.md 第七节设置
   from image_api import generate_image
   result = generate_image(prompt)
   # result["status"] == "success" → result["image_url"]
   # result["status"] == "failed" → result["error"]，走错误处理
   ```

5. **结果处理** → 回 SKILL.md 第四节
6. **自查** → 回 SKILL.md 第二节
7. **等用户确认原始形象满意后**，继续下一步

---

## 步骤 B：生成换装图

### 前置条件
- 角色原图已确认（用户提供 或 步骤A生成）
- 用户已提供衣物参考图
- 两张图都已下载到 /tmp

### 执行流程
1. **收费确认**（必须先发，等用户确认）：
   ```
   换装图将使用 qwen-image-2.0-pro 模型生成，¥0.5/张。确认生成？
   ```

2. **读取提示词**：读取 `config/prompt.md` 第一节「换装图片提示词」，原样使用固定正向提示词（不要修改）

3. **展示提示词给用户**：
   ```
   换装图提示词如下：
   ---
   {提示词}
   ---
   模型：qwen-image-2.0-pro | 费用：¥0.5
   注意：图1=角色原图，图2=衣物参考图
   ```

4. **调用 API**（同步，约60-90秒，直接等待结果，不需要 cron）：
   ```python
   # sys.path 已在 SKILL.md 第七节设置
   from image_api import generate_dress_image
   result = generate_dress_image(
       char_image_path="/tmp/角色原图路径.png",
       cloth_image_path="/tmp/衣物图路径.jpg",
       prompt="读取的固定提示词"
   )
   # result["status"] == "success" → result["image_url"]
   # result["status"] == "failed" → result["error"]，走错误处理
   ```
   **重要**：图片API是同步接口，调用后直接等结果返回，不要回复"稍后推送"。

5. **结果处理** → 回 SKILL.md 第四节
6. **自查** → 回 SKILL.md 第二节
7. **等用户确认换装图满意后**，继续下一步

---

## 步骤 C：生成视频

### 前置条件
- 角色原图（作为首帧）
- 换装结果图（作为尾帧）
- 两张图都已下载到 /tmp

### 执行流程
1. **收费确认**（必须先发，等用户确认）：
   ```
   视频将使用 wanx2.1-kf2v-plus 模型生成，720P，5秒，¥7.5/次。确认生成？
   ```

2. **构造提示词**（严格按照模板填写提示词！）：
读取 `config/prompt.md` 第二节「视频转场提示词」模板，根据原始参考图和换装结果图的实际内容填写 {} 部分：
   - 观察原图：描述服装、背景、画风
   - 观察换装图：描述新服装
   - 填入模板

3. **展示提示词给用户确认**（严格遵守必须等用户说"可以"才生成）：
   ```
   视频提示词如下，请确认或修改：
   ---
   {填写后的提示词}
   ---
   模型：wanx2.1-kf2v-plus | 费用：¥7.5 | 720P | 5秒
   确认请回复"可以"，需修改请直接说明。
   ```

4. **调用 API**（异步，需要轮询等待）：
   ```python
   # sys.path 已在 SKILL.md 第七节设置
   from video_api import generate_video, wait_for_video

   result = generate_video(
       first_frame_path="/tmp/角色原图.png",
       last_frame_path="/tmp/换装图.png",
       prompt="用户确认后的提示词"
   )
   if result["status"] == "failed":
       # 走错误处理
       pass
   else:
       # 轮询等待，每30秒查一次，最多10分钟
       final = wait_for_video(result["task_id"])
       # final["status"]: "success" → final["video_url"]
       #                  "failed"  → final["error"]，走错误处理
       #                  "timeout" → 走错误处理（超时）
   ```

5. **结果处理** → 回 SKILL.md 第四节
6. **自查** → 回 SKILL.md 第二节
7. **等用户确认视频满意后**，继续下一步

---

## 步骤 D：抖音发布内容

### 执行流程
1. 根据角色、衣物风格、换装前后对比，在云文档「4. 抖音发布内容」章节填写：
   - **标题**：抖音风格，15字以内，带话题标签
   - **简介**：50-100字，包含 #AI换装 #角色名 等标签
   - **置顶评论**：互动引导语，如"你们想看XX穿什么？评论区告诉我"

2. 将该章节状态改为"已完成"，将顶部「创作状态」改为"已完成"

3. 发送完成消息：
   ```
   全部完成！云文档已包含：原始形象、换装图、视频、抖音发布内容。
   云文档链接：{链接}
   是否继续下一个角色？
   ```
