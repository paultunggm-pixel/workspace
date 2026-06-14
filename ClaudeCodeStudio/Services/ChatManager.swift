import Foundation
import SwiftUI

/// Manages chat sessions, messages, and streaming state.
/// Sends messages through the active provider's API.
class ChatManager: ObservableObject {
    @Published var sessions: [ChatSession] = []
    @Published var activeSessionId: UUID?
    @Published var isStreaming = false
    @Published var streamingContent = ""

    // Quick-actions target for the three shortcut buttons
    @Published var pendingAction: QuickActionType?
    weak var providerManager: ProviderManager?

    init() {
        seedSampleData()
    }

    private func seedSampleData() {
        let projectId = UUID()
        let session = ChatSession(
            title: "欢迎使用 Claude Code Studio",
            projectId: projectId,
            messages: [
                ChatMessage(role: .system, content: "会话已创建"),
                ChatMessage(role: .assistant, content: "你好！我是 Claude。我可以帮你编写代码、分析数据、设计方案。\n\n左侧是项目面板，你可以创建项目来组织工作。下方输入框可以发送消息。\n\n试试选中侧栏中的项目，然后在这里开始对话吧。"),
                ChatMessage(role: .user, content: "帮我写一个 SwiftUI 按钮组件"),
                ChatMessage(role: .assistant, content: "好的，这是一个带渐变背景的 SwiftUI 按钮：\n\n```swift\nButton(action: { print(\"tapped\") }) {\n    Text(\"点击\")\n        .font(.headline)\n        .foregroundColor(.white)\n        .padding(.horizontal, 24)\n        .padding(.vertical, 12)\n        .background(\n            LinearGradient(\n                colors: [.blue, .purple],\n                startPoint: .leading,\n                endPoint: .trailing\n            )\n        )\n        .cornerRadius(10)\n}\n```\n\n可以调整颜色和圆角来匹配你的设计。"),
            ],
            totalTokens: 512
        )
        sessions = [session]
        activeSessionId = session.id
    }

    // MARK: - Session Management

    var activeSession: ChatSession? {
        sessions.first(where: { $0.id == activeSessionId })
    }

    func openSession(_ sessionId: UUID) {
        activeSessionId = sessionId
    }

    func openSession(for projectId: UUID, title: String = "新会话") {
        if let existing = sessions.first(where: { $0.projectId == projectId && $0.isActive }) {
            activeSessionId = existing.id
        } else {
            let session = ChatSession(title: title, projectId: projectId)
            sessions.append(session)
            activeSessionId = session.id
        }
    }

    func closeSession(_ sessionId: UUID) {
        sessions.removeAll { $0.id == sessionId }
        if activeSessionId == sessionId {
            activeSessionId = sessions.last?.id
        }
    }

    func renameSession(_ sessionId: UUID, to title: String) {
        if let idx = sessions.firstIndex(where: { $0.id == sessionId }) {
            sessions[idx].title = title
            sessions[idx].updatedAt = Date()
        }
    }

    // MARK: - Message Handling

    func sendMessage(_ content: String, attachments: [ChatAttachment] = []) {
        guard let idx = sessions.firstIndex(where: { $0.id == activeSessionId }) else {
            return
        }

        let userMsg = ChatMessage(role: .user, content: content, attachments: attachments)
        sessions[idx].messages.append(userMsg)
        sessions[idx].updatedAt = Date()

        if sessions[idx].title == "新会话" {
            sessions[idx].title = String(content.prefix(40)).trimmingCharacters(in: .whitespaces)
        }

        let assistantMsg = ChatMessage(role: .assistant, content: "", isStreaming: true)
        sessions[idx].messages.append(assistantMsg)
        sessions[idx].updatedAt = Date()

        // Force @Published to fire for internal array mutation
        objectWillChange.send()

        if let pm = providerManager,
           let provider = pm.activeProvider,
           provider.connectionStatus == .connected,
           let apiKey = try? pm.readKey(for: provider.id.uuidString) {
            callRealAPI(provider: provider, apiKey: apiKey, sessionId: sessions[idx].id, messageId: assistantMsg.id)
        } else {
            simulateStream(for: sessions[idx].id, messageId: assistantMsg.id)
        }
    }

    private func callRealAPI(provider: ProviderConfig, apiKey: String, sessionId: UUID, messageId: UUID) {
        isStreaming = true
        streamingContent = ""

        let messages = buildMessageHistory(for: sessionId)

        APIService.sendMessage(
            provider: provider,
            apiKey: apiKey,
            model: provider.defaultModel,
            messages: messages,
            onChunk: { [weak self] chunk in
                DispatchQueue.main.async {
                    self?.streamingContent += chunk
                }
            },
            onComplete: { [weak self] result in
                DispatchQueue.main.async {
                    guard let self = self else { return }
                    self.isStreaming = false
                    switch result {
                    case .success(let content):
                        if let sIdx = self.sessions.firstIndex(where: { $0.id == sessionId }),
                           let mIdx = self.sessions[sIdx].messages.firstIndex(where: { $0.id == messageId }) {
                            self.sessions[sIdx].messages[mIdx].content = content
                            self.sessions[sIdx].messages[mIdx].isStreaming = false
                            self.sessions[sIdx].totalTokens += content.count / 4
                            self.sessions[sIdx].updatedAt = Date()
                            self.objectWillChange.send()
                        }
                    case .failure:
                        if let sIdx = self.sessions.firstIndex(where: { $0.id == sessionId }),
                           let mIdx = self.sessions[sIdx].messages.firstIndex(where: { $0.id == messageId }) {
                            self.sessions[sIdx].messages[mIdx].content = "API 调用失败"
                            self.sessions[sIdx].messages[mIdx].isStreaming = false
                            self.objectWillChange.send()
                        }
                    }
                    self.streamingContent = ""
                }
            }
        )
    }

    private func buildMessageHistory(for sessionId: UUID) -> [APIService.Message] {
        guard let session = sessions.first(where: { $0.id == sessionId }) else { return [] }
        return session.messages
            .filter { $0.role != .system && !$0.isStreaming }
            .prefix(20)
            .map { APIService.Message(role: $0.role == .assistant ? "assistant" : "user", content: $0.content) }
    }

    private func simulateStream(for sessionId: UUID, messageId: UUID) {
        let demoResponse = "[模拟响应]\n好的，我来帮你完成这个任务。\n\n```swift\nstruct ExampleView: View {\n    var body: some View {\n        Text(\"Hello\")\n            .font(.title)\n    }\n}\n```\n\n这是模拟响应。请在侧栏配置API Key以使用真实AI。"

        isStreaming = true
        streamingContent = ""
        let chars = Array(demoResponse)
        var index = 0
        Timer.scheduledTimer(withTimeInterval: 0.003, repeats: true) { [weak self] timer in
            guard let self = self else { timer.invalidate(); return }
            if index < chars.count {
                self.streamingContent += String(chars[index])
                index += 1
            } else {
                timer.invalidate(); self.isStreaming = false
                if let sIdx = self.sessions.firstIndex(where: { $0.id == sessionId }),
                   let mIdx = self.sessions[sIdx].messages.firstIndex(where: { $0.id == messageId }) {
                    self.sessions[sIdx].messages[mIdx].content = self.streamingContent
                    self.sessions[sIdx].messages[mIdx].isStreaming = false
                    self.sessions[sIdx].totalTokens += self.streamingContent.count / 4
                    self.sessions[sIdx].updatedAt = Date()
                    self.objectWillChange.send()
                }
                self.streamingContent = ""
            }
        }
    }

    func regenerateLastMessage() {
        guard let session = activeSession,
              let lastUser = session.messages.last(where: { $0.role == .user }) else { return }
        // Remove last assistant message, resend
        if let sIdx = sessions.firstIndex(where: { $0.id == session.id }),
           let lastAssistantIdx = sessions[sIdx].messages.lastIndex(where: { $0.role == .assistant }) {
            sessions[sIdx].messages.remove(at: lastAssistantIdx)
        }
        sendMessage(lastUser.content, attachments: lastUser.attachments)
    }

    // MARK: - Quick Actions

    enum QuickActionType: String {
        case claudeMd = "沉淀到 CLAUDE.md"
        case projectSkills = "沉淀到本项目 Skills"
        case compress = "压缩上下文"
    }

    func triggerQuickAction(_ action: QuickActionType) {
        pendingAction = action
    }
}
