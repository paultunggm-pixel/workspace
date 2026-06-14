import SwiftUI

struct SidebarView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var providerManager: ProviderManager

    var body: some View {
        ScrollView {
            VStack(spacing: AppTheme.cardMargin) {
                ModelEngineCard()
                    .padding(.horizontal, AppTheme.cardMargin)

                ProjectListCard()
                    .padding(.horizontal, AppTheme.cardMargin)
            }
            .padding(.top, AppTheme.cardMargin)
            .padding(.bottom, AppTheme.cardMargin)
        }
        .background(Color(nsColor: .controlBackgroundColor))
    }
}

struct ModelEngineCard: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var providerManager: ProviderManager

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text("🧠 模型引擎")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(AppTheme.textPrimary)
                Spacer()
                if providerManager.activeProvider != nil {
                    Circle()
                        .fill(Color.green)
                        .frame(width: 6, height: 6)
                }
            }

            if providerManager.hasProviders {
                VStack(spacing: 6) {
                    ModelSelector()
                    if let active = providerManager.activeProvider,
                       active.connectionStatus != .connected {
                        InlineKeyInput(provider: active)
                    }
                    QuickSwitchButtons()
                    if providerManager.activeProvider?.connectionStatus == .connected {
                        BalanceCard()
                    }
                }
                .padding(10)
                .background(RoundedRectangle(cornerRadius: AppTheme.cardRadius).fill(AppTheme.cardBackground)
                    .overlay(RoundedRectangle(cornerRadius: AppTheme.cardRadius).stroke(AppTheme.cardBorder, lineWidth: 1)))
            } else {
                VStack(spacing: 10) {
                    Text("🧠")
                        .font(.system(size: 28))
                    Text("尚未配置模型")
                        .font(.system(size: 11))
                        .foregroundColor(AppTheme.textPrimary)
                    Text("点击下方按钮添加模型提供商")
                        .font(.system(size: 9))
                        .foregroundColor(AppTheme.textSecondary)
                    Button(action: {
                        providerManager.addQuickProvider()
                    }) {
                        Label("添加提供商", systemImage: "plus.circle.fill")
                            .font(.system(size: 11))
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(AppTheme.accent)
                }
                .frame(maxWidth: .infinity)
                .padding(.vertical, 20)
                .background(
                    RoundedRectangle(cornerRadius: AppTheme.cardRadius)
                        .fill(AppTheme.cardBackground)
                        .overlay(
                            RoundedRectangle(cornerRadius: AppTheme.cardRadius)
                                .stroke(AppTheme.cardBorder, lineWidth: 1)
                        )
                )
            }
        }
    }
}

// ProjectListCard defined in ProjectTreeView.swift

struct InlineKeyInput: View {
    let provider: ProviderConfig
    @EnvironmentObject var providerManager: ProviderManager
    @State private var key = ""
    @State private var msg = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            TextField("粘贴 \(provider.label) API Key", text: $key)
                .textFieldStyle(.roundedBorder).font(.system(size: 9))
            HStack(spacing: 6) {
                Button("保存") {
                    let k = key.trimmingCharacters(in: .whitespaces)
                    guard !k.isEmpty else { return }
                    do {
                        try providerManager.saveKey(k, for: provider.id.uuidString)
                        providerManager.updateConnectionStatus(providerId: provider.id, status: .connected)
                        key = ""; msg = "已连接 " + provider.label
                    } catch { msg = error.localizedDescription }
                }
                .font(.system(size: 9, weight: .medium)).foregroundColor(.white)
                .padding(.horizontal, 10).padding(.vertical, 3)
                .background(RoundedRectangle(cornerRadius: 4).fill(AppTheme.accent))
                .buttonStyle(.plain)
                if !msg.isEmpty {
                    Text(msg).font(.system(size: 8)).foregroundColor(msg.contains("已连接") ? .green : .red)
                }
            }
        }
}
