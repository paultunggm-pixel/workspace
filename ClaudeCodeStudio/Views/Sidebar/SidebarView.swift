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
                       active.connectionStatus == .disconnected {
                        APIKeyInputCard(provider: active)
                    }
                    QuickSwitchButtons()
                    BalanceCard()
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

struct APIKeyInputCard: View {
    let provider: ProviderConfig
    @EnvironmentObject var providerManager: ProviderManager
    @State private var apiKey = ""
    @State private var isTesting = false
    @State private var statusText = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            Text("🔑 \(provider.type.icon) \(provider.label) API Key")
                .font(.system(size: 9, weight: .semibold))
                .foregroundColor(AppTheme.textSecondary)

            SecureField("sk-...", text: $apiKey)
                .textFieldStyle(.roundedBorder)
                .font(.system(size: 10))

            if !statusText.isEmpty {
                Text(statusText)
                    .font(.system(size: 9))
                    .foregroundColor(statusText.contains("成功") ? .green : .red)
            }

            HStack(spacing: 8) {
                Button(action: {
                    isTesting = true
                    statusText = "测试中..."
                    let key = apiKey.trimmingCharacters(in: .whitespaces)
                    Task {
                        do {
                            let ok = try await APIService.testConnection(provider: provider, apiKey: key)
                            if ok {
                                try providerManager.saveKey(key, for: provider.id.uuidString)
                                providerManager.updateConnectionStatus(providerId: provider.id, status: .connected)
                                statusText = "连接成功"
                                apiKey = ""
                            } else {
                                statusText = "Key 无效"
                            }
                        } catch {
                            statusText = "连接失败"
                        }
                        isTesting = false
                    }
                }) {
                    Text("保存并测试")
                        .font(.system(size: 10, weight: .medium))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 4)
                }
                .buttonStyle(.plain)
                .foregroundColor(.white)
                .background(RoundedRectangle(cornerRadius: 5).fill(AppTheme.accent))
                .disabled(apiKey.trimmingCharacters(in: .whitespaces).isEmpty || isTesting)
            }
        }
        .padding(8)
        .background(RoundedRectangle(cornerRadius: 6).fill(Color.yellow.opacity(0.08)))
    }
}
