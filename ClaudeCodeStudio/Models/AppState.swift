import SwiftUI

class AppState: ObservableObject {
    @Published var selectedProjectId: String? = nil
    @Published var selectedTab: ContentTab = .chat
    @Published var engineStatus: EngineStatus = .disconnected
    @Published var gitBranch: String = "main"
    @Published var gitLastCommit: String = ""
    @Published var gitIsClean: Bool = true
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
