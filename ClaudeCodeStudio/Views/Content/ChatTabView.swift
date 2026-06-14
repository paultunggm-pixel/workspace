import SwiftUI
import Combine

// MARK: - Chat Tab (replaces placeholder in ContentArea)

struct ChatTabView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var chatManager: ChatManager
    @State private var inputText = ""
    @FocusState private var isInputFocused: Bool

    var body: some View {
        VStack(spacing: 0) {
            // Sub-tab bar for multiple conversations
            ConversationTabs()

            // Message list with auto-scroll
            ChatMessageList()
                .frame(maxHeight: .infinity)

            // Quick action buttons
            QuickActionButtons()
                .padding(.horizontal, 24)
                .padding(.top, 8)

            // Input bar
            ChatInputBar(inputText: $inputText, isFocused: $isInputFocused) {
                sendMessage()
            }
        }
    }

    private func sendMessage() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }

        // Ensure session exists
        if chatManager.activeSession == nil {
            if let pid = appState.selectedProjectId.flatMap(UUID.init) {
                chatManager.openSession(for: pid)
            }
        }

        chatManager.sendMessage(text)
        inputText = ""
    }
}

// MARK: - Conversation Tabs (sub-tab bar)

struct ConversationTabs: View {
    @EnvironmentObject var chatManager: ChatManager

    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 4) {
                if let activeSession = chatManager.activeSession {
                    ForEach(chatManager.sessions.filter { $0.isActive }) { session in
                        HStack(spacing: 4) {
                            Text(session.title)
                                .font(.system(size: 10, weight: session.id == activeSession.id ? .semibold : .regular))
                                .foregroundColor(session.id == activeSession.id ? AppTheme.textPrimary : AppTheme.textSecondary)
                                .lineLimit(1)
                                .frame(maxWidth: 120)

                            if chatManager.sessions.count > 1 {
                                Button(action: { chatManager.closeSession(session.id) }) {
                                    Image(systemName: "xmark")
                                        .font(.system(size: 7, weight: .medium))
                                        .foregroundColor(AppTheme.textTertiary)
                                }
                                .buttonStyle(.plain)
                            }
                        }
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                        .background(
                            RoundedRectangle(cornerRadius: 6)
                                .fill(session.id == activeSession.id
                                      ? Color.white
                                      : Color.black.opacity(0.03))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 6)
                                .stroke(
                                    session.id == activeSession.id
                                        ? AppTheme.dividerGray
                                        : Color.clear,
                                    lineWidth: 1
                                )
                        )
                        .onTapGesture { chatManager.openSession(session.id) }
                    }
                }

                // New session button
                Button(action: {
                    if let pid = chatManager.activeSession?.projectId {
                        chatManager.openSession(for: pid)
                    }
                }) {
                    Image(systemName: "plus")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundColor(AppTheme.textSecondary)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 5)
                }
                .buttonStyle(.plain)
            }
            .padding(.horizontal, 18)
        }
        .padding(.vertical, 8)
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
}

// MARK: - Message Row

struct MessageRow: View {
    let message: ChatMessage

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            if message.role == .assistant {
                // Claude avatar
                Circle()
                    .fill(Color.white)
                    .frame(width: 28, height: 28)
                    .overlay(
                        Circle()
                            .stroke(AppTheme.claudeAmber, lineWidth: 1.5)
                    )
                    .overlay(
                        Image(systemName: "brain.head.profile")
                            .font(.system(size: 12))
                            .foregroundColor(AppTheme.claudeAmber)
                    )
            } else {
                Spacer().frame(width: 28, height: 28)
            }

            VStack(alignment: message.role == .user ? .trailing : .leading, spacing: 4) {
                // Role label
                Text(message.role == .user ? "我" : "Claude")
                    .font(.system(size: 9, weight: .medium))
                    .foregroundColor(AppTheme.textTertiary)

                // Content bubble
                VStack(alignment: .leading, spacing: 4) {
                    if message.isStreaming {
                        HStack(spacing: 2) {
                            Text(message.content)
                                .font(.system(size: 12))
                                .foregroundColor(AppTheme.textPrimary)
                            if message.isStreaming {
                                Rectangle()
                                    .fill(AppTheme.accent)
                                    .frame(width: 6, height: 13)
                                    .opacity(Date().timeIntervalSince1970.truncatingRemainder(dividingBy: 0.6) > 0.3 ? 1 : 0)
                            }
                        }
                    } else {
                        Text(message.content)
                            .font(.system(size: 12))
                            .foregroundColor(AppTheme.textPrimary)
                    }

                    // Artifact file references
                    if !message.artifactFiles.isEmpty {
                        HStack(spacing: 4) {
                            ForEach(message.artifactFiles, id: \.self) { file in
                                HStack(spacing: 3) {
                                    Image(systemName: "doc")
                                        .font(.system(size: 8))
                                    Text(file)
                                        .font(.system(size: 9))
                                }
                                .padding(.horizontal, 6)
                                .padding(.vertical, 3)
                                .background(
                                    RoundedRectangle(cornerRadius: 4)
                                        .fill(AppTheme.accentBackground)
                                )
                                .foregroundColor(AppTheme.accent)
                            }
                        }
                    }
                }
                .padding(10)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(message.role == .user
                              ? AppTheme.accentBackground
                              : Color.white)
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(
                            message.role == .user
                                ? AppTheme.accent.opacity(0.3)
                                : AppTheme.dividerGray,
                            lineWidth: 1
                        )
                )

                // Action bar (Claude messages only)
                if message.role == .assistant && !message.isStreaming {
                    HStack(spacing: 12) {
                        Button(action: {}) {
                            HStack(spacing: 2) {
                                Image(systemName: "hand.thumbsup")
                                Image(systemName: "hand.thumbsdown")
                            }
                            .font(.system(size: 9))
                        }
                        .buttonStyle(.plain)
                        .foregroundColor(AppTheme.textTertiary)

                        Button(action: {
                            NSPasteboard.general.clearContents()
                            NSPasteboard.general.setString(message.content, forType: .string)
                        }) {
                            Image(systemName: "doc.on.doc")
                                .font(.system(size: 9))
                        }
                        .buttonStyle(.plain)
                        .foregroundColor(AppTheme.textTertiary)

                        Button(action: {}) {
                            Image(systemName: "arrow.counterclockwise")
                                .font(.system(size: 9))
                        }
                        .buttonStyle(.plain)
                        .foregroundColor(AppTheme.textTertiary)
                    }
                }

                // Timestamp
                Text(message.timestamp, style: .time)
                    .font(.system(size: 8))
                    .foregroundColor(AppTheme.textTertiary.opacity(0.6))
            }
            .frame(maxWidth: 600, alignment: message.role == .user ? .trailing : .leading)

            if message.role == .user {
                // User avatar (purple gradient)
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [Color(red: 0.39, green: 0.38, blue: 0.95),
                                     Color(red: 0.55, green: 0.36, blue: 0.96)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 28, height: 28)
                    .overlay(
                        Text("P")
                            .font(.system(size: 10, weight: .semibold))
                            .foregroundColor(.white)
                    )
            } else {
                Spacer().frame(width: 28, height: 28)
            }
        }
    }
}

// MARK: - Quick Action Buttons

struct QuickActionButtons: View {
    @EnvironmentObject var chatManager: ChatManager

    var body: some View {
        HStack(spacing: 6) {
            quickButton(
                icon: "📜",
                title: "沉淀到 CLAUDE.md",
                action: .claudeMd
            )
            quickButton(
                icon: "📋",
                title: "沉淀到本项目 Skills",
                action: .projectSkills
            )
            quickButton(
                icon: "🗜",
                title: "压缩上下文",
                action: .compress
            )
        }
    }

    private func quickButton(icon: String, title: String, action: ChatManager.QuickActionType) -> some View {
        Button(action: { chatManager.triggerQuickAction(action) }) {
            HStack(spacing: 4) {
                Text(icon)
                    .font(.system(size: 10))
                Text(title)
                    .font(.system(size: 10, weight: .medium))
            }
        }
        .buttonStyle(.plain)
        .foregroundColor(AppTheme.textSecondary)
        .padding(.horizontal, 10)
        .padding(.vertical, 5)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.white)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(AppTheme.dividerGray, lineWidth: 1)
                )
        )
    }
}

// MARK: - Chat Input Bar

struct ChatInputBar: View {
    @Binding var inputText: String
    @FocusState.Binding var isFocused: Bool
    var onSend: () -> Void

    var body: some View {
        HStack(spacing: 8) {
            TextField("输入消息...", text: $inputText)
                .textFieldStyle(.plain)
                .font(.system(size: 13))
                .focused($isFocused)
                .onSubmit { onSend() }

            Button("发送", action: onSend)
                .font(.system(size: 11, weight: .medium))
                .foregroundColor(.white)
                .padding(.horizontal, 12)
                .padding(.vertical, 5)
                .background(
                    RoundedRectangle(cornerRadius: 5)
                        .fill(inputText.trimmingCharacters(in: .whitespaces).isEmpty
                            ? Color.gray : AppTheme.accent)
                )
                .buttonStyle(.plain)
                .disabled(inputText.trimmingCharacters(in: .whitespaces).isEmpty)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .stroke(AppTheme.dividerGray, lineWidth: 1)
        )
        .padding(.horizontal, 24)
        .padding(.vertical, 12)
    }
}

// MARK: - Chat Message List (auto-scroll)

struct ChatMessageList: View {
    @EnvironmentObject var chatManager: ChatManager

    var body: some View {
        ScrollViewReader { proxy in
            ScrollView {
                Group {
                    if let session = chatManager.activeSession {
                        if session.messages.isEmpty {
                            emptyChat
                        } else {
                            messageListContent(session: session)
                        }
                    } else {
                        noSession
                    }
                }
                .padding(.horizontal, 24)
                .padding(.vertical, 16)
            }
        }
        .onReceive(chatManager.$isStreaming) { _ in }
    }

    @ViewBuilder
    private func messageListContent(session: ChatSession) -> some View {
        ForEach(session.messages) { msg in
            MessageRow(message: msg).id(msg.id)
        }
        if chatManager.isStreaming, !chatManager.streamingContent.isEmpty {
            MessageRow(
                message: ChatMessage(
                    role: .assistant,
                    content: chatManager.streamingContent,
                    isStreaming: true
                )
            )
            .id("streaming")
        }
    }

    private var emptyChat: some View {
        VStack(spacing: 16) {
            Image(systemName: "brain.head.profile")
                .font(.system(size: 40))
                .foregroundColor(AppTheme.claudeAmber.opacity(0.5))
            Text("开始与 Claude 对话")
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(AppTheme.textSecondary)
            Text("输入你的需求，Claude 会帮你完成")
                .font(.system(size: 11))
                .foregroundColor(AppTheme.textTertiary)
        }
        .frame(maxWidth: .infinity, minHeight: 300)
    }

    private var noSession: some View {
        VStack(spacing: 16) {
            Image(systemName: "bubble.left.and.bubble.right")
                .font(.system(size: 40))
                .foregroundColor(AppTheme.textTertiary.opacity(0.4))
            Text("选择一个项目开始对话")
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(AppTheme.textSecondary)
            Text("在左侧项目列表中选择或新建项目")
                .font(.system(size: 11))
                .foregroundColor(AppTheme.textTertiary)
        }
        .frame(maxWidth: .infinity, minHeight: 300)
    }
}
