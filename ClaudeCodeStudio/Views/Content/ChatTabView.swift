import SwiftUI
import Combine

struct ChatTabView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var chatManager: ChatManager
    @State private var inputText = ""

    var body: some View {
        VStack(spacing: 0) {
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
                                Image(systemName: "brain.head.profile").font(.system(size: 40)).foregroundColor(AppTheme.claudeAmber.opacity(0.5))
                                Text("开始与 Claude 对话").font(.system(size: 14, weight: .medium)).foregroundColor(AppTheme.textSecondary)
                                Text("输入你的需求，Claude 会帮你完成").font(.system(size: 11)).foregroundColor(AppTheme.textTertiary)
                            }.frame(maxWidth: .infinity, minHeight: 300)
                        }
                    }
                    .padding(.horizontal, 24).padding(.vertical, 16)
                }
                .onReceive(chatManager.$isStreaming) { _ in
                    if let lastId = chatManager.activeSession?.messages.last?.id {
                        proxy.scrollTo(lastId, anchor: .bottom)
                    }
                }
            }

            // Quick actions
            QuickActionButtons().padding(.horizontal, 24).padding(.top, 8)

            // Input
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
            .overlay(RoundedRectangle(cornerRadius: 8).stroke(AppTheme.dividerGray, lineWidth: 1))
            .padding(.horizontal, 24).padding(.vertical, 12)
        }
    }

    private func send() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        if chatManager.activeSession == nil, let pid = appState.selectedProjectId.flatMap(UUID.init) {
            chatManager.openSession(for: pid)
        }
        chatManager.sendMessage(text)
        inputText = ""
    }
}

// MARK: - Message Row

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
                Text(message.role == .user ? "我" : "Claude").font(.system(size: 9, weight: .medium)).foregroundColor(AppTheme.textTertiary)
                Text(message.content).font(.system(size: 12)).foregroundColor(AppTheme.textPrimary)
                    .padding(10)
                    .background(RoundedRectangle(cornerRadius: 8).fill(message.role == .user ? AppTheme.accentBackground : Color.white))
                    .overlay(RoundedRectangle(cornerRadius: 8).stroke(message.role == .user ? AppTheme.accent.opacity(0.3) : AppTheme.dividerGray, lineWidth: 1))
                if message.role == .assistant && !message.isStreaming {
                    HStack(spacing: 12) {
                        Button(action: {}) { HStack(spacing: 2) { Image(systemName: "hand.thumbsup"); Image(systemName: "hand.thumbsdown") }.font(.system(size: 9)) }.buttonStyle(.plain).foregroundColor(AppTheme.textTertiary)
                        Button(action: { NSPasteboard.general.clearContents(); NSPasteboard.general.setString(message.content, forType: .string) }) { Image(systemName: "doc.on.doc").font(.system(size: 9)) }.buttonStyle(.plain).foregroundColor(AppTheme.textTertiary)
                    }
                }
            }.frame(maxWidth: 600, alignment: message.role == .user ? .trailing : .leading)

            if message.role == .user {
                Circle().fill(LinearGradient(colors: [Color(red: 0.39, green: 0.38, blue: 0.95), Color(red: 0.55, green: 0.36, blue: 0.96)], startPoint: .topLeading, endPoint: .bottomTrailing))
                    .frame(width: 28, height: 28).overlay(Text("P").font(.system(size: 10, weight: .semibold)).foregroundColor(.white))
            } else { Spacer().frame(width: 28, height: 28) }
        }
    }
}

// MARK: - Quick Action Buttons

struct QuickActionButtons: View {
    @EnvironmentObject var chatManager: ChatManager
    var body: some View {
        HStack(spacing: 6) {
            ForEach([("📜", "沉淀到 CLAUDE.md", ChatManager.QuickActionType.claudeMd),
                     ("📋", "沉淀到本项目 Skills", .projectSkills),
                     ("🗜", "压缩上下文", .compress)], id: \.0) { item in
                Button(action: { chatManager.triggerQuickAction(item.2) }) {
                    HStack(spacing: 4) { Text(item.0).font(.system(size: 10)); Text(item.1).font(.system(size: 10, weight: .medium)) }
                }.buttonStyle(.plain).foregroundColor(AppTheme.textSecondary)
                    .padding(.horizontal, 10).padding(.vertical, 5)
                    .background(RoundedRectangle(cornerRadius: 8).fill(Color.white).overlay(RoundedRectangle(cornerRadius: 8).stroke(AppTheme.dividerGray, lineWidth: 1)))
            }
        }
    }
}
