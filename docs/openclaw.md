要在飞书（Feishu/Lark）中通过 OpenClaw 与 Claude 进行代码交互，你主要需要利用 OpenClaw 作为一个“连接中枢”，将飞书的聊天界面与 Claude 的推理能力以及你本地或云端的代码操作工具（如执行环境、Git 管理等）打通。


---

## 2. 配置飞书通道 (Feishu Channel)
你需要创建一个飞书自建应用，并将其与 OpenClaw 关联。
1. **创建飞书应用：** 前往 [飞书开放平台](https://open.feishu.cn/)，创建一个自建应用，启用“机器人”功能。
2. **获取凭证：** 记录下 `App ID` 和 `App Secret`。
3. **配置 `openclaw.json`：** 编辑 `~/.openclaw/openclaw.json` 文件，添加飞书配置：
   ```json
   {
     "channels": {
       "feishu": {
         "enabled": true,
         "appId": "你的AppID",
         "appSecret": "你的AppSecret",
         "connectionMode": "websocket" // 推荐使用 WebSocket，无需公网 IP 即可接收消息
       }
     }
   }
   ```

---

## 3. 设置 Claude 为核心模型
将 Claude（推荐使用 Claude 3.5 Sonnet 或更高版本，因其代码能力最强）设为默认 Agent 的模型。
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-3-5-sonnet",
        "models": {
          "anthropic/claude-3-5-sonnet": { "alias": "Claude" }
        }
      }
    }
  }
}
```

---

## 4. 开启代码技能 (Coding Skills)
为了让 Claude 能够真正“处理代码”，你需要开启 OpenClaw 提供的代码相关技能。
* **常用技能推荐：**
    * `file-read/write`：读写本地文件。
    * `exec`：在沙盒或本地执行代码/终端命令。
    * `git-manager`：处理 Git 提交和分支。
* **配置示例：**
  ```json
  {
    "agents": {
      "defaults": {
        "skills": ["file-read", "file-write", "exec", "git-manager"]
      }
    }
  }
  ```

---

## 5. 在飞书中交互
完成配置并运行 `openclaw start` 后，你就可以在飞书中与机器人对话了：

* **代码生成与修改：** > “帮我写一个 Python 脚本来处理 `data.csv`，并保存到当前目录下。”
* **代码解释与调试：** > “读取 `src/main.ts` 这个文件，看看为什么第 42 行会报错。”
* **执行任务：** > “帮我执行 `npm run test`，并将结果总结给我。”

### 💡 进阶技巧：
* **流式消息卡片：** OpenClaw 支持飞书的交互式卡片。当 Claude 正在思考或生成长代码时，飞书界面会实时更新代码块，体验接近于 IDE 的 Inline 补全。
* **多模型切换：** 如果遇到复杂的架构设计，可以在飞书输入 `/model anthropic/claude-3-opus` 切换到更高推理能力的模型；如果只是简单的格式调整，可以切回 Sonnet 以节省成本。
* **安全提醒：** 由于 `exec` 技能允许 AI 执行系统命令，建议在 `openclaw.json` 中配置 `allowlist` 限制哪些人可以触发该机器人，防止误操作。

如果你在使用 `hosts8.com` 相关域名进行 Webhook 配置时遇到解析问题，建议优先使用 **WebSocket 模式**，这样可以绕过防火墙和域名配置带来的复杂性。

在 OpenClaw 中配置项目路径（Project Path）至关重要，因为这决定了 Claude 能够访问、读取和修改你本地哪些文件夹中的代码。

要让 Claude 正确识别并操作你的项目，可以通过以下几种方式进行配置：

## 1. 动态工作空间配置（推荐）
在飞书中，你不需要修改全局配置文件，直接通过指令即可切换当前机器人关注的目录。
* **指令：** `/workspace set <绝对路径>`
* **示例：** `/workspace set /Users/lin/projects/math-monster`
* **效果：** 设置后，Claude 调用的所有文件读取（`file-read`）或代码执行（`exec`）技能都将以该路径为根目录。

---

## 2. 在 `openclaw.json` 中配置初始路径
如果你希望机器人启动时默认就进入某个项目，可以在配置文件中定义环境路径：

```json
{
  "agents": {
    "defaults": {
      "env": {
        "PROJECT_ROOT": "/home/ubuntu/projects/quant-bot",
        "PYTHONPATH": "${PROJECT_ROOT}/src"
      },
      "skills_config": {
        "file-manager": {
          "base_dir": "/home/ubuntu/projects/quant-bot",
          "allow_out_of_bounds": false 
        }
      }
    }
  }
}
```
> **注意：** 将 `allow_out_of_bounds` 设置为 `false` 是一项安全措施，可以防止 AI 意外访问到项目目录之外的系统敏感文件。

---

## 3. 环境变量自动识别
OpenClaw 能够识别你运行 `openclaw start` 时的当前 Shell 环境。
* 如果你在项目根目录下启动服务：
  ```bash
  cd /your/project/path
  openclaw start
  ```
* 此时，Claude 会默认将该目录视为其执行命令的 **CWD (Current Working Directory)**。

---

## 4. 针对特定技能的路径限制
如果你使用了特定的 IDE 辅助工具或插件（例如针对代码库索引的 `code-index` 技能），你需要在该技能的配置项中指定扫描路径：

```json
{
  "skills_config": {
    "code-index": {
      "paths": ["/home/ubuntu/projects/my-app"],
      "exclude": ["**/node_modules/**", "**/.git/**", "**/dist/**"]
    }
  }
}
```

---

## 5. 验证配置是否生效
配置完成后，你可以在飞书里问 Claude 一句：
> “你现在的工作目录在哪里？请列出当前目录下的前 5 个文件。”

如果它能正确列出你项目中的 `package.json`、`main.py` 或 `go.mod` 等文件，说明路径配置成功。

### 💡 小贴士：
* **绝对路径：** 在配置文件中，务必使用绝对路径（如 `/home/user/...`），避免使用 `~/` 等相对路径符号，以防不同权限运行服务时解析出错。
* **权限检查：** 确保运行 OpenClaw 的用户对该项目路径拥有读写权限（`chmod -R 755`），否则 Claude 在尝试修复代码并写入文件时会报错。