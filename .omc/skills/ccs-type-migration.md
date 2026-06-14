---
name: ccs-type-migration
description: 在 ClaudeCodeStudio Swift 代码库中系统性地迁移某个类型的定义（如 String?→UUID?），确保所有引用点更新、零残留、编译通过、通知链路类型一致。
triggers:
  - 类型迁移
  - 改类型
  - String 改 UUID
  - 类型重构
  - type migration
  - 统一类型
  - 消除 String/UUID 转换
---

# ClaudeCodeStudio 类型迁移操作清单

## 适用场景

修改 `AppState` 或其他核心模型中的某个 `@Published` 属性类型（如 `String?` → `UUID?`），需要级联修改所有引用点。

## 前置条件

- 目标类型与源类型的语义对应关系明确（如 `String?` ↔ `UUID?` 通过 `.uuidString` / `UUID.init` 互转）
- 确认新类型是否能直接用 `==` 比较、是否能直接赋值

## 执行步骤

### 1. 确定类型源头

在 `Models/AppState.swift` 或模型定义文件中修改类型声明。

### 2. 搜索所有引用

```bash
grep -rn "<属性名>" ClaudeCodeStudio/ --include="*.swift"
```

记录每个引用位置的文件和行号。

### 3. 逐文件修改

对每个引用点按以下规则修改：

| 旧模式 | 新模式 | 场景 |
|--------|--------|------|
| `prop.flatMap(UUID.init)` | 直接 `prop` | 解包 String? 转 UUID? |
| `prop == obj.id.uuidString` | `prop == obj.id` | 比较，UUID? == UUID |
| `obj.id.uuidString` 赋值给 prop | `obj.id` 直接赋值 | 赋值，UUID → UUID? |
| 示例/文档中的旧类型 | 新类型 | 保持文档同步 |

### 4. 残留检测

```bash
# 检查 .uuidString 残留（只关注与目标属性相关的）
grep -rn "\.uuidString" ClaudeCodeStudio/ --include="*.swift"

# 检查 flatMap(UUID.init) 残留
grep -rn "flatMap(UUID.init)" ClaudeCodeStudio/ --include="*.swift"

# 检查旧类型字面量
grep -rn ": String?" ClaudeCodeStudio/ --include="*.swift" | grep -i "<属性名>"
```

### 5. 通知链路验证

如果属性变更涉及 `NotificationCenter` 通知传递：

```bash
# 搜索通知的发送端 object 类型
grep -rn "post.*<通知名>" ClaudeCodeStudio/ --include="*.swift"

# 搜索通知的接收端 cast 类型
grep -rn "notif.object as?" ClaudeCodeStudio/ --include="*.swift"

# 确认发送端的 object 类型 == 接收端 cast 类型
```

### 6. 验证表

| 检查项 | 命令/方法 |
|--------|----------|
| 所有引用已更新 | `grep` 搜索旧模式，结果应为 0 |
| 通知链路一致 | 发送 object 类型 == 接收 `as?` 类型 |
| 比较操作正确 | UUID? == UUID 编译通过 |
| 无死代码残留 | 删除旧转换/桥接函数 |
| 构建编译 | `xcodebuild -project ClaudeCodeStudio.xcodeproj -scheme ClaudeCodeStudio -destination 'platform=macOS' build` |

## 常见陷阱

| 陷阱 | 对策 |
|------|------|
| **忘记 UserDefaults 持久化** | 如果属性需要跨启动保持，检查是否有 `UserDefaults.standard.set(prop, forKey:)` 调用点 |
| **String? 和 UUID? 的 `==` 行为不同** | `String? == String` 和 `UUID? == UUID` 都编译通过，但确保比较值语义一致 |
| **通知 object 类型遗漏** | `NotificationCenter.default.post(name:object:)` 的 object 参数是 `Any?`，编译器不检查类型，必须手动验证 |
| **仅更新定义未更新使用者** | Swift 编译器的类型检查会捕获多数遗漏，但通知 object 和强制转换不会 |
| **struct 和 class 的 weak self 混淆** | 类型迁移期间顺手做其他重构时，确认 `[weak self]` 只用于 class，struct 直接用值捕获 |

## 经验教训（来自 2026-06-14 迁移）

- `PublishTabView` 是 struct，Timer 闭包中 `[weak self]` 是编译错误
- 通知 `switchToProject` 的 object 类型从 `String` 变为 `UUID`，接收端的 `as? UUID` 必须匹配
- `ChatManager.swift` 中 `.uuidString` 用于 UserDefaults/Keychain 存储（`String` 键），是正确用法，不要误删
- 代码审查员应独立验证用户关于"预存错误"的说法——用 `git diff` 确认问题归属
