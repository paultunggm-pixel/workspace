---
name: ccs-add-tab
description: 为 ClaudeCodeStudio macOS 应用添加新的内容标签页（Tab）。涉及 AppState 枚举、TabBar 按钮、ContentArea 路由、新 TabView 文件、AppTheme 样式引用 5 个修改点。
triggers:
  - 添加新标签
  - 新增 Tab
  - 加一个页面
  - 新功能标签
  - add tab
  - new tab
  - ccs 新页面
---

# 为 ClaudeCodeStudio 添加新的内容标签页

## 适用场景

在 ClaudeCodeStudio SwiftUI macOS 应用中添加一个新的功能标签页（如「会话」「方案」「预览」旁边的第 N 个标签）。

## 前置条件

- 工作目录为 `ClaudeCodeStudio/`（macOS SwiftUI 项目）
- 理解 `AppState`、`ContentTab` 枚举、`TabBar`、`ContentArea` 之间的关系

## 架构关系

```
AppState.selectedTab: ContentTab   ← 当前选中标签
       ↓
TabBar: ForEach(ContentTab.allCases) → 遍历枚举生成按钮
       ↓
ContentArea: switch selectedTab → 路由到对应 *TabView
```

## 执行步骤

### 1. 添加枚举 case

文件：`Models/AppState.swift`

```swift
enum ContentTab: String, CaseIterable {
    case chat = "会话"
    case plan = "方案"
    case preview = "预览"
    case code = "代码"
    case publish = "发布"
    case service = "服务"
    case newFeature = "新功能"  // ← 新增
}
```

- `CaseIterable` 自动生成 `allCases`，TabBar 无需额外修改
- rawValue 是中文字符串，显示在 TabBar 按钮上

### 2. 添加 TabBar 图标

文件：`Views/Content/TabBar.swift`

```swift
func tabIcon(for tab: ContentTab) -> String {
    switch tab {
    case .chat: return "💬"
    // ... 其他 case ...
    case .newFeature: return "🆕"  // ← 新增
    }
}
```

### 3. 添加 ContentArea 路由

文件：`Views/Content/ContentArea.swift`

```swift
ZStack {
    switch appState.selectedTab {
    case .chat:    ChatTabView()
    // ... 其他 case ...
    case .newFeature: NewFeatureTabView()  // ← 新增
    }
}
```

### 4. 创建新 TabView 文件

文件：`Views/Content/NewFeatureTabView.swift`（新建）

```swift
import SwiftUI

struct NewFeatureTabView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var chatManager: ChatManager  // 如需要

    var body: some View {
        VStack(spacing: 0) {
            // Header toolbar（参考其他 TabView 的 padding/background 模式）
            HStack {
                Text("🆕 新功能")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(AppTheme.textPrimary)
                Spacer()
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 10)
            .background(
                Rectangle()
                    .fill(Color.white)
                    .overlay(
                        Rectangle().frame(height: 1).foregroundColor(AppTheme.dividerGray),
                        alignment: .bottom
                    )
            )

            // Content body
            ScrollView {
                // 功能内容
            }
            .background(Color.white)
        }
    }
}
```

### 5. 验证检查

- [ ] `ContentTab.allCases` 包含新 case（TabBar 会自动出现新按钮）
- [ ] TabBar 上能看到新标签按钮，点击后高亮
- [ ] 切换到其他标签再切回来，状态保持
- [ ] 新 TabView 的 `@EnvironmentObject` 注入正确（通过 `ClaudeCodeStudioApp.swift` 确认）

## 关键约定

| 约定 | 说明 |
|------|------|
| **Header toolbar 样式** | 所有 TabView 使用统一模板：12pt semibold 标题 + padding(18,10) + divider 底边 |
| **背景色** | 始终用 `.background(Color.white)`，不要用系统默认背景 |
| **字体** | 正文 12pt / 辅助 11pt / 说明 9pt，参考 `AppTheme` |
| **颜色** | 主文字 `AppTheme.textPrimary`，次要 `AppTheme.textSecondary`，三级 `AppTheme.textTertiary` |
| **命名** | TabView 文件名 = `{英文名}TabView.swift`，放在 `Views/Content/` |
| **环境对象** | 通过 `@EnvironmentObject` 获取，在 `ClaudeCodeStudioApp.swift` 中注入 |

## 常见陷阱

| 陷阱 | 对策 |
|------|------|
| **只加了 case 忘了加路由** | `ContentArea.swift` 的 switch 必须穷尽，否则编译报错 |
| **TabBar 图标遗漏** | `tabIcon(for:)` 没有 `default` 分支，新 case 缺少 match 会编译报错 |
| **背景色用系统默认** | 各 Tab 之间切换可能出现视觉不一致，始终用 `.background(Color.white)` |
| **忘记 Xcode 项目文件** | 新建 .swift 文件后需通过 Xcode 添加到 target，或在 `Package.swift` 中声明 |
| **EnvironmentObject 未注入** | 新建的 TabView 如果用了 `@EnvironmentObject`，确认 `ClaudeCodeStudioApp.swift` 中已 `.environmentObject()` |
