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
