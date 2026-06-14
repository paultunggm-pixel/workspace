import SwiftUI

struct ChatTabView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var chatManager: ChatManager
    @State private var inputText = ""
    @State private var lastScrollTime = Date.distantPast

    var body: some View {
        VStack(spacing: 0) {
            // Session title bar
            if let session = chatManager.activeSession {
                Text(session.title)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(AppTheme.textPrimary)
                    .padding(.horizontal, 24).padding(.vertical, 6)
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .background(Color.white.overlay(
                        Rectangle().frame(height: 1).foregroundColor(AppTheme.dividerGray), alignment: .bottom))
            }

            // Messages
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(spacing: 12) {
                        if let session = chatManager.activeSession, !session.messages.isEmpty {
                            ForEach(session.messages) { msg in
                                MessageRow(message: msg).id(msg.id)
                            }
                        } else {
                            VStack(spacing: 16) {
                                Image(systemName: "brain.head.profile")
                                    .font(.system(size: 40))
                                    .foregroundColor(AppTheme.claudeAmber.opacity(0.5))
                                Text("开始与 Claude 对话")
                                    .font(.system(size: 14, weight: .medium))
                                    .foregroundColor(AppTheme.textSecondary)
                            }
                            .frame(maxWidth: .infinity, minHeight: 200)
                        }
                    }
                    .padding(.horizontal, 24).padding(.vertical, 16)
                }
                .onReceive(chatManager.$streamingContent) { _ in
                    let now = Date()
                    guard now.timeIntervalSince(lastScrollTime) > 0.1 else { return }
                    lastScrollTime = now
                    if let lastId = chatManager.activeSession?.messages.last?.id {
                        withAnimation { proxy.scrollTo(lastId, anchor: .bottom) }
                    }
                }
            }

            // Quick actions
            QuickActionButtons().padding(.horizontal, 24).padding(.top, 4)

            // Input bar
            HStack(spacing: 8) {
                TextField("输入消息...", text: $inputText)
                    .font(.system(size: 13))
                    .onSubmit { send() }
                Button("发送") { send() }
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(.white)
                    .padding(.horizontal, 12).padding(.vertical, 5)
                    .background(RoundedRectangle(cornerRadius: 5)
                        .fill(inputText.trimmingCharacters(in: .whitespaces).isEmpty ? Color.gray : AppTheme.accent))
                    .buttonStyle(.plain)
                    .disabled(inputText.trimmingCharacters(in: .whitespaces).isEmpty)
            }
            .padding(.horizontal, 12).padding(.vertical, 8)
            .background(Color.white.overlay(
                Rectangle().frame(height: 1).foregroundColor(AppTheme.dividerGray), alignment: .top))
            .padding(.horizontal, 24).padding(.bottom, 8)
        }
        .onReceive(NotificationCenter.default.publisher(for: .switchToProject)) { notif in
            if let projectId = notif.object as? UUID {
                chatManager.openSession(for: projectId)
            }
        }
        .onChange(of: chatManager.pendingAction) { action in
            guard let action = action else { return }
            handleQuickAction(action)
        }
    }

    private func send() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        if chatManager.activeSession == nil,
           let projectId = appState.selectedProjectId.flatMap(UUID.init) {
            chatManager.openSession(for: projectId)
        }
        chatManager.sendMessage(text)
        inputText = ""
    }

    private func handleQuickAction(_ action: ChatManager.QuickActionType) {
        defer { chatManager.pendingAction = nil }
        guard let sIdx = chatManager.sessions.firstIndex(where: { $0.id == chatManager.activeSessionId }) else { return }
        switch action {
        case .compress:
            let total = chatManager.sessions[sIdx].messages.count
            guard total > 12 else { return }
            let systemMsgs = chatManager.sessions[sIdx].messages.prefix(while: { $0.role == .system })
            let keep = Array(chatManager.sessions[sIdx].messages.suffix(10))
            chatManager.sessions[sIdx].messages = Array(systemMsgs) + keep
            let summary = ChatMessage(role: .system, content: "上下文已压缩 (" + String(total) + " -> " + String(chatManager.sessions[sIdx].messages.count) + " 条消息)")
            chatManager.sessions[sIdx].messages.insert(summary, at: systemMsgs.count)
        case .claudeMd:
            let summary = extractSummary()
            writeToClaudeMd(summary)
            let msg = ChatMessage(role: .system, content: "已从对话提取关键信息写入 CLAUDE.md")
            chatManager.sessions[sIdx].messages.append(msg)
        case .projectSkills:
            let summary = extractSummary()
            writeToProjectSkills(summary)
            let msg = ChatMessage(role: .system, content: "已从对话提取技能模式写入项目 Skills (.omc/skills/)")
            chatManager.sessions[sIdx].messages.append(msg)
        }
        chatManager.sessions[sIdx].updatedAt = Date()
        chatManager.objectWillChange.send()
    }

    private func extractSummary() -> String {
        guard let session = chatManager.activeSession else { return "" }
        let msgs = session.messages.filter { $0.role != .system }
        return msgs.map { ($0.role == .user ? "[用户] " : "[Claude] ") + $0.content }
            .suffix(10).joined(separator: "\n\n")
    }

    private func writeToClaudeMd(_ content: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let file = home.appendingPathComponent("Documents/Claude/CLAUDE.md")
        let entry = "\n\n## 从对话沉淀 (\(Date().formatted(date: .numeric, time: .shortened)))\n\n" + content + "\n"
        if let handle = try? FileHandle(forWritingTo: file) {
            handle.seekToEndOfFile()
            handle.write(entry.data(using: .utf8)!)
            try? handle.close()
        } else {
            try? entry.data(using: .utf8)?.write(to: file)
        }
    }

    private func writeToProjectSkills(_ content: String) {
        let home = FileManager.default.homeDirectoryForCurrentUser
        let dir = home.appendingPathComponent("Documents/Claude/.omc/skills")
        try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        let file = dir.appendingPathComponent("project-skill.md")
        let entry = "# 项目技能\n\n从 Claude Code Studio 对话提取\n\n" + content + "\n"
        try? entry.data(using: .utf8)?.write(to: file)
    }
}

// MARK: - Subviews

struct MessageRow: View {
    let message: ChatMessage
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            if message.role == .assistant {
                Circle().fill(Color.white).frame(width: 28, height: 28)
                    .overlay(Circle().stroke(AppTheme.claudeAmber, lineWidth: 1.5))
                    .overlay(Image(systemName: "brain.head.profile").font(.system(size: 12)).foregroundColor(AppTheme.claudeAmber))
            } else { Spacer().frame(width: 28, height: 28) }

            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 4) {
                Text(message.role == .user ? "我" : "Claude")
                    .font(.system(size: 9, weight: .medium))
                    .foregroundColor(AppTheme.textTertiary)
                Text(message.content)
                    .font(.system(size: 12))
                    .foregroundColor(AppTheme.textPrimary)
                    .padding(10)
                    .background(RoundedRectangle(cornerRadius: 8)
                        .fill(message.role == .user ? AppTheme.accentBackground : Color.white))
                    .overlay(RoundedRectangle(cornerRadius: 8)
                        .stroke(message.role == .user ? AppTheme.accent.opacity(0.3) : AppTheme.dividerGray, lineWidth: 1))
            }
            .frame(maxWidth: 600, alignment: message.role == .user ? .trailing : .leading)

            if message.role == .user {
                Circle().fill(LinearGradient(
                    colors: [Color(red: 0.39, green: 0.38, blue: 0.95),
                             Color(red: 0.55, green: 0.36, blue: 0.96)],
                    startPoint: .topLeading, endPoint: .bottomTrailing))
                    .frame(width: 28, height: 28)
                    .overlay(Text("P").font(.system(size: 10, weight: .semibold)).foregroundColor(.white))
            } else { Spacer().frame(width: 28, height: 28) }
        }
    }
}

struct QuickActionButtons: View {
    @EnvironmentObject var chatManager: ChatManager
    var body: some View {
        HStack(spacing: 6) {
            Button(action: { chatManager.triggerQuickAction(.claudeMd) }) {
                Text("📜 沉淀到 CLAUDE.md").font(.system(size: 10, weight: .medium))
            }
            .buttonStyle(.plain).foregroundColor(AppTheme.textSecondary)
            .padding(.horizontal, 10).padding(.vertical, 5)
            .background(RoundedRectangle(cornerRadius: 8).fill(Color.white)
                .overlay(RoundedRectangle(cornerRadius: 8).stroke(AppTheme.dividerGray, lineWidth: 1)))

            Button(action: { chatManager.triggerQuickAction(.projectSkills) }) {
                Text("📋 沉淀到本项目 Skills").font(.system(size: 10, weight: .medium))
            }
            .buttonStyle(.plain).foregroundColor(AppTheme.textSecondary)
            .padding(.horizontal, 10).padding(.vertical, 5)
            .background(RoundedRectangle(cornerRadius: 8).fill(Color.white)
                .overlay(RoundedRectangle(cornerRadius: 8).stroke(AppTheme.dividerGray, lineWidth: 1)))

            Button(action: { chatManager.triggerQuickAction(.compress) }) {
                Text("🗜 压缩上下文").font(.system(size: 10, weight: .medium))
            }
            .buttonStyle(.plain).foregroundColor(AppTheme.textSecondary)
            .padding(.horizontal, 10).padding(.vertical, 5)
            .background(RoundedRectangle(cornerRadius: 8).fill(Color.white)
                .overlay(RoundedRectangle(cornerRadius: 8).stroke(AppTheme.dividerGray, lineWidth: 1)))
        }
    }
}
