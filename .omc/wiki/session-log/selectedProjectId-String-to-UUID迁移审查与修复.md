# selectedProjectId: String? → UUID? 迁移审查与修复

## 时间
2026-06-14

## 任务
将 `AppState.selectedProjectId` 从 `String?` 迁移到 `UUID?`，消除项目中不必要的 String/UUID 互转。

## 涉及文件（7个）

| 文件 | 变更 |
|------|------|
| `Models/AppState.swift:4` | `String?` → `UUID?` |
| `Views/Content/ChatTabView.swift:91` | 移除 `.flatMap(UUID.init)`，直接解包 |
| `Views/Sidebar/ProjectTreeView.swift:143,150,158` | 移除 3 处 `.uuidString` |
| `Views/Content/CodeTabView.swift:23` | 示例字符串同步更新 |
| `Views/Content/ContentArea.swift` | 删除未使用的 `DebugTabView`（14行死代码） |
| `Services/ChatManager.swift` | 提取 `finalizeAssistantMessage` 复用方法；增强 API Key 缺失错误处理；`[weak self]` 修复 |
| `Views/Content/PublishTabView.swift:343` | 错误地添加了 `[weak self]`（对 struct 无效），后修复 |

## 审查发现的阻断项

### [HIGH] PublishTabView.swift:343 — `[weak self]` 用于 struct
- `PublishTabView` 是 struct（值类型），`weak` 无效，导致编译错误
- 本次提交为 Timer 闭包误加了 `[weak self] + guard let self`
- **修复**：撤回变更，恢复为 `{ t in ... }`

## 修复后提交

```
49a5f24 将 selectedProjectId 类型从 String? 迁移到 UUID?
```

## 合并与清理

- `phase1` → `main` 先快进推送远程，再真合并本地（冲突全部采用 origin/main）
- 合并提交：`7ee6bf5`
- 清理：phase1 worktree、phase1 本地分支、phase1 远程分支、agent-a3c5ce 遗留 worktree 均已删除

## 验证检查项

- `project.id.uuidString` 残留：0 处
- `flatMap(UUID.init)` on selectedProjectId：0 处
- `DebugTabView` 残留引用：0 处
- `switchToProject` 通知链路：send UUID / receive `as? UUID` 一致
- 保留的 `.uuidString` 用法均为正确场景：`provider.id.uuidString`（Keychain 键）、`activeSessionId?.uuidString`（UserDefaults 存储）

## 教训

- **struct vs class 区分**：`[weak self]` 只能用于 class，struct 的闭包直接捕获值拷贝即可
- **审查前确认 diff 归属**：用户称 PublishTabView 错误为「预存」，但 git diff 证明是本次提交引入
- **类型迁移后必须 grep 全项目残留**：`.uuidString`、`.flatMap(UUID.init)`、通知 object 类型三处必须一致
- **main 被 worktree 占用时用 `git push origin <branch>:main`** 从 worktree 直接推送远程合并
- **`git branch -f` 不能用于被 worktree 占用的分支** — 用远程快进 + 本地真合并替代
