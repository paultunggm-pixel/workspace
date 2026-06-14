# Claude Code Studio — Phase 1: 项目骨架 & 窗口布局

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 macOS SwiftUI 项目骨架，实现三栏 Dashboard 布局（左侧栏 + 中央内容区），包含标题栏、状态栏、基本导航结构。

**Architecture:** SwiftUI App 生命周期，`NavigationSplitView` 替代方案改为自定义三栏 `HSplitView`。左侧栏 300px 固定宽度含模型引擎卡片和项目列表，中央区自适应宽度含 Tab 栏。配色使用 Apple 系统色系。

**Tech Stack:** Swift 5.10+, SwiftUI (macOS 14+), Xcode 16+, Swift Package Manager

**Spec Reference:** `docs/superpowers/specs/2026-06-12-claude-code-studio-design.md`

---

## 9-Phase Roadmap

| Phase | 内容 | 预估工作量 |
|------|------|------|
| **1** | 项目骨架 + 窗口布局 + 标题栏 + 状态栏 | 2-3 天 |
| **2** | 模型引擎：Provider 配置、Keychain、余额卡片 | 3-4 天 |
| **3** | 项目管理：分类/项目 CRUD + 侧栏树形 | 2-3 天 |
| **4** | 会话 Tab：Claude Code 引擎集成、消息、输入、快捷按钮 | 4-5 天 |
| **5** | 方案/预览/代码 Tab | 3-4 天 |
| **6** | 发布 Tab：三类型 + 连接闭环 | 3-4 天 |
| **7** | 服务 Tab：MCP 管理 + GitHub 集成 | 3-4 天 |
| **8** | 设置面板：CLAUDE.md + 项目概览 | 2-3 天 |
| **9** | 打磨：搜索、语言、头像、Claude Preview、Sparkle 更新 | 3-4 天 |

---

## File Structure for Phase 1

```
ClaudeCodeStudio/
├── ClaudeCodeStudioApp.swift          # App 入口
├── ContentView.swift                  # 根视图，三栏布局容器
├── Models/
│   └── AppState.swift                 # 全局状态 ObservableObject
├── Views/
│   ├── Titlebar/
│   │   └── TitlebarView.swift         # 标题栏：Logo + 标题 + 连接状态 + 用户按钮
│   ├── Sidebar/
│   │   ├── SidebarView.swift          # 左侧栏容器
│   │   ├── ModelEngineCard.swift      # 模型引擎卡片（占位）
│   │   └── ProjectListCard.swift      # 项目列表卡片（占位）
│   ├── Content/
│   │   ├── ContentArea.swift          # 中央区容器
│   │   └── TabBar.swift              # Tab 栏（会话/方案/预览/代码/发布/服务）
│   └── StatusBar/
│       └── StatusBarView.swift        # 底部状态栏
├── Theme/
│   └── AppTheme.swift                 # 颜色、字体、间距常量
├── Assets.xcassets/                   # 颜色、图标
└── ClaudeCodeStudio.xcodeproj
```

---

## Task 1: 创建 Xcode 项目

**Files:**
- Create: `ClaudeCodeStudio/ClaudeCodeStudioApp.swift`
- Create: `ClaudeCodeStudio/ContentView.swift`
- Create: `ClaudeCodeStudio.xcodeproj`

- [ ] **Step 1: 创建 Xcode 项目**

```bash
mkdir -p ~/Documents/Claude/ClaudeCodeStudio
cd ~/Documents/Claude/ClaudeCodeStudio
```

In Xcode: File → New → Project → macOS → App
- Product Name: `ClaudeCodeStudio`
- Interface: SwiftUI
- Language: Swift
- Minimum Deployment: macOS 14.0
- Save to: `~/Documents/Claude/ClaudeCodeStudio/`

- [ ] **Step 2: 编写 App 入口**

```swift
// ClaudeCodeStudioApp.swift
import SwiftUI

@main
struct ClaudeCodeStudioApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        Window("Claude Code Studio", id: "main") {
            ContentView()
                .environmentObject(appState)
                .frame(minWidth: 960, idealWidth: 1440, minHeight: 640, idealHeight: 900)
        }
        .windowStyle(.titleBar)
        .windowToolbarStyle(.unified)
    }
}
```

- [ ] **Step 3: 创建 AppState**

```swift
// Models/AppState.swift
import SwiftUI

class AppState: ObservableObject {
    // 当前选中的项目 ID
    @Published var selectedProjectId: String? = nil
    
    // 当前选中的 Tab
    @Published var selectedTab: ContentTab = .chat
    
    // 连接状态
    @Published var engineStatus: EngineStatus = .disconnected
    
    // GitHub 状态
    @Published var gitBranch: String = "main"
    @Published var gitLastCommit: String = ""
    @Published var gitIsClean: Bool = true
    
    // Token 用量
    @Published var tokenCount: Int = 0
    @Published var tokenLimit: Int = 200000
}

enum ContentTab: String, CaseIterable {
    case chat = "会话"
    case plan = "方案"
    case preview = "预览"
    case code = "代码"
    case publish = "发布"
    case service = "服务"
}

enum EngineStatus {
    case connected, disconnected, updating
}
```

- [ ] **Step 4: 创建 AppTheme**

```swift
// Theme/AppTheme.swift
import SwiftUI

enum AppTheme {
    // Sidebar
    static let sidebarWidth: CGFloat = 300
    static let sidebarBackground = Color(nsColor: .windowBackgroundColor)
    
    // Cards
    static let cardRadius: CGFloat = 10
    static let cardBorder = Color.black.opacity(0.07)
    static let cardBackground = Color.white.opacity(0.55)
    
    // Spacing
    static let cardMargin: CGFloat = 10
    static let cardPadding: CGFloat = 12
    static let rowPadding: CGFloat = 6
    static let contentMargin: CGFloat = 10
    
    // Typography
    static let titleSize: CGFloat = 12
    static let bodySize: CGFloat = 11
    static let captionSize: CGFloat = 9
    
    // Colors
    static let accent = Color.blue
    static let accentBackground = Color.blue.opacity(0.06)
    static let claudeAmber = Color(red: 0.85, green: 0.47, blue: 0.34)
    static let dividerGray = Color.black.opacity(0.07)
    static let textPrimary = Color(.labelColor)
    static let textSecondary = Color(.secondaryLabelColor)
    static let textTertiary = Color(.tertiaryLabelColor)
}
```

- [ ] **Step 5: Commit**

```bash
cd ~/Documents/Claude/ClaudeCodeStudio
git init
git add -A
git commit -m "Phase 1/Task 1: 创建 Xcode 项目骨架，AppState + AppTheme"
```

---

## Task 2: 实现三栏布局 + ContentView

**Files:**
- Modify: `ClaudeCodeStudio/ContentView.swift`
- Create: `ClaudeCodeStudio/Views/Sidebar/SidebarView.swift`
- Create: `ClaudeCodeStudio/Views/Content/ContentArea.swift`

- [ ] **Step 1: 实现 ContentView 三栏容器**

```swift
// ContentView.swift
import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        VStack(spacing: 0) {
            TitlebarView()
            
            HStack(spacing: 0) {
                // Left sidebar
                SidebarView()
                    .frame(width: AppTheme.sidebarWidth)
                
                // Center content
                ContentArea()
                    .frame(maxWidth: .infinity)
            }
            .frame(maxHeight: .infinity)
            
            StatusBarView()
        }
        .background(Color(nsColor: .windowBackgroundColor))
    }
}
```

- [ ] **Step 2: 实现 SidebarView 容器**

```swift
// Views/Sidebar/SidebarView.swift
import SwiftUI

struct SidebarView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        ScrollView {
            VStack(spacing: AppTheme.cardMargin) {
                // Model Engine Card (placeholder)
                ModelEngineCard()
                    .padding(.horizontal, AppTheme.cardMargin)
                
                // Project List Card (placeholder)
                ProjectListCard()
                    .padding(.horizontal, AppTheme.cardMargin)
            }
            .padding(.top, AppTheme.cardMargin)
        }
        .background(
            Color(nsColor: .windowBackgroundColor)
                .opacity(0.5)
        )
    }
}

// Placeholder cards (will be expanded in later phases)
struct ModelEngineCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("🧠 模型引擎")
                .font(.system(size: 10, weight: .semibold))
                .foregroundColor(AppTheme.textSecondary)
            
            RoundedRectangle(cornerRadius: AppTheme.cardRadius)
                .fill(AppTheme.cardBackground)
                .frame(height: 200)
        }
    }
}

struct ProjectListCard: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("📁 项目")
                .font(.system(size: 10, weight: .semibold))
                .foregroundColor(AppTheme.textSecondary)
            
            RoundedRectangle(cornerRadius: AppTheme.cardRadius)
                .fill(AppTheme.cardBackground)
                .frame(maxHeight: .infinity)
        }
    }
}
```

- [ ] **Step 3: 实现 ContentArea 容器**

```swift
// Views/Content/ContentArea.swift
import SwiftUI

struct ContentArea: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        VStack(spacing: 0) {
            // Tab bar
            TabBar(selectedTab: $appState.selectedTab)
            
            // Tab content area
            ZStack {
                switch appState.selectedTab {
                case .chat:    Text("会话")
                case .plan:    Text("方案")
                case .preview: Text("预览")
                case .code:    Text("代码")
                case .publish: Text("发布")
                case .service: Text("服务")
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(Color.white)
        .clipShape(RoundedRectangle(cornerRadius: AppTheme.cardRadius))
        .padding(.trailing, AppTheme.contentMargin)
        .padding(.bottom, AppTheme.contentMargin)
    }
}
```

- [ ] **Step 4: 实现 TabBar**

```swift
// Views/Content/TabBar.swift
import SwiftUI

struct TabBar: View {
    @Binding var selectedTab: ContentTab
    
    var body: some View {
        HStack(spacing: 0) {
            ForEach(ContentTab.allCases, id: \.self) { tab in
                Button(action: { selectedTab = tab }) {
                    Text(tabIcon(for: tab) + " " + tab.rawValue)
                        .font(.system(size: 11, weight: selectedTab == tab ? .semibold : .regular))
                        .padding(.horizontal, 13)
                        .padding(.vertical, 7)
                }
                .buttonStyle(.plain)
                .foregroundColor(selectedTab == tab ? AppTheme.accent : AppTheme.textSecondary)
                .background(
                    selectedTab == tab ?
                    AnyView(
                        Rectangle()
                            .fill(AppTheme.accent)
                            .frame(height: 2),
                        alignment: .bottom
                    ) : AnyView(EmptyView())
                )
            }
            
            Spacer()
        }
        .padding(.horizontal, 18)
        .padding(.top, 10)
        .background(
            Rectangle()
                .fill(Color.white)
                .overlay(
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(AppTheme.dividerGray),
                    alignment: .bottom
                )
        )
    }
    
    func tabIcon(for tab: ContentTab) -> String {
        switch tab {
        case .chat: return "💬"
        case .plan: return "📋"
        case .preview: return "🎨"
        case .code: return "📝"
        case .publish: return "🚀"
        case .service: return "🔌"
        }
    }
}
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "Phase 1/Task 2: 三栏布局 + Sidebar + ContentArea + TabBar 骨架"
```

---

## Task 3: 标题栏

**Files:**
- Create: `ClaudeCodeStudio/Views/Titlebar/TitlebarView.swift`

- [ ] **Step 1: 实现标题栏**

```swift
// Views/Titlebar/TitlebarView.swift
import SwiftUI

struct TitlebarView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        HStack(spacing: 0) {
            // Logo + Title
            HStack(spacing: 7) {
                Image(systemName: "brain.head.profile")
                    .font(.system(size: 14))
                    .foregroundColor(AppTheme.claudeAmber)
                
                Text("Claude Code Studio")
                    .font(.system(size: 12, weight: .semibold))
            }
            .frame(maxWidth: .infinity, alignment: .center)
            
            // User button
            Menu {
                Button("CLAUDE.md 长期记忆配置") {}
                Button("Claude 内核更新") {}
                Divider()
                Button("头像及昵称") {}
                Button("语言设置") {}
                Divider()
                Button("关于") {}
            } label: {
                HStack(spacing: 6) {
                    Circle()
                        .fill(
                            LinearGradient(
                                colors: [Color(red: 0.39, green: 0.38, blue: 0.95),
                                         Color(red: 0.55, green: 0.36, blue: 0.96)],
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .frame(width: 22, height: 22)
                        .overlay(
                            Text("P")
                                .font(.system(size: 10, weight: .semibold))
                                .foregroundColor(.white)
                        )
                    
                    Text("paultunggm-pixel")
                        .font(.system(size: 11))
                        .foregroundColor(AppTheme.textSecondary)
                }
                .padding(.horizontal, 10)
                .padding(.vertical, 4)
                .background(Color.black.opacity(0.03))
                .clipShape(Capsule())
            }
            .menuStyle(.borderlessButton)
            .fixedSize()
            .padding(.trailing, 8)
        }
        .frame(height: 48)
        .background(.ultraThinMaterial)
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "Phase 1/Task 3: 标题栏 — Logo + 标题 + 用户菜单"
```

---

## Task 4: 状态栏

**Files:**
- Create: `ClaudeCodeStudio/Views/StatusBar/StatusBarView.swift`

- [ ] **Step 1: 实现状态栏**

```swift
// Views/StatusBar/StatusBarView.swift
import SwiftUI

struct StatusBarView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        HStack {
            // GitHub status
            HStack(spacing: 6) {
                Text("🐙")
                Text(appState.gitBranch)
                    .font(.system(size: 9, design: .monospaced))
                Text("·")
                Text(appState.gitLastCommit)
            }
            .font(.system(size: 9))
            .foregroundColor(AppTheme.textTertiary)
            
            Spacer()
            
            // Engine & Token status
            HStack(spacing: 10) {
                Text("Engine v2.1.150")
                Text("Tokens \(appState.tokenCount)K/\(appState.tokenLimit/1000)K")
            }
            .font(.system(size: 9))
            .foregroundColor(AppTheme.textTertiary)
        }
        .padding(.horizontal, 14)
        .frame(height: 28)
        .background(.ultraThinMaterial)
        .overlay(
            Rectangle()
                .frame(height: 1)
                .foregroundColor(AppTheme.dividerGray),
            alignment: .top
        )
    }
}
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "Phase 1/Task 4: 状态栏 — GitHub 状态 + 引擎版本 + Token"
```

---

## Task 5: 集成测试 & 验证

- [ ] **Step 1: Build & Run**

```bash
cd ~/Documents/Claude/ClaudeCodeStudio
xcodebuild -project ClaudeCodeStudio.xcodeproj -scheme ClaudeCodeStudio build 2>&1 | tail -5
```
Expected: **BUILD SUCCEEDED**

- [ ] **Step 2: 手动验证清单**

| 验证项 | 预期 |
|------|------|
| 窗口出现，最小 960×640 | ✅ |
| 左侧栏 300px，右侧内容自适应 | ✅ |
| 标题栏有 Logo + 标题 + 用户按钮 | ✅ |
| 6 个 Tab 可点击切换 | ✅ |
| 状态栏显示默认信息 | ✅ |
| 缩放窗口时布局响应正确 | ✅ |

- [ ] **Step 3: Commit final**

```bash
git add -A
git commit -m "Phase 1 完成：项目骨架 + 窗口布局 + 标题栏 + 状态栏"
```

---

## Phase 1 Complete → Gate for Phase 2

Phase 1 完成后，应有：
- ✅ 可运行的 macOS 应用窗口
- ✅ 三栏布局（侧栏 300px + 中央自适应）
- ✅ 标题栏（Logo + 菜单）
- ✅ 状态栏
- ✅ 6 个 Tab 导航结构

**Gate check 通过后，开始 Phase 2: 模型引擎。**
