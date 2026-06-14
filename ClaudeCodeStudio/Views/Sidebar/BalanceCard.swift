import SwiftUI

/// Displays current provider balance, usage percentage, and status
struct BalanceCard: View {
    @EnvironmentObject var providerManager: ProviderManager

    var body: some View {
        VStack(spacing: 6) {
            if let provider = providerManager.activeProvider,
               let balance = provider.lastBalance {
                // Balance amount
                HStack(alignment: .firstTextBaseline, spacing: 2) {
                    Text(provider.type.currency)
                        .font(.system(size: 10))
                        .foregroundColor(AppTheme.textTertiary)
                    Text(String(format: "%.2f", balance))
                        .font(.system(size: 18, weight: .semibold, design: .monospaced))
                        .foregroundColor(providerManager.balanceColor)
                }

                // Usage bar
                if let pct = providerManager.balancePercentage {
                    GeometryReader { geo in
                        ZStack(alignment: .leading) {
                            RoundedRectangle(cornerRadius: 2)
                                .fill(Color.black.opacity(0.06))
                                .frame(height: 4)

                            RoundedRectangle(cornerRadius: 2)
                                .fill(providerManager.balanceColor)
                                .frame(width: geo.size.width * CGFloat(pct), height: 4)
                        }
                    }
                    .frame(height: 4)
                }

                // Usage link
                HStack {
                    Text(usageLabel(for: provider))
                        .font(.system(size: 9))
                        .foregroundColor(AppTheme.textTertiary)
                    Spacer()
                    if let usageURL = usageURL(for: provider.type) {
                        Link(destination: usageURL) {
                            Text("用量页面...")
                                .font(.system(size: 9))
                                .foregroundColor(AppTheme.accent)
                        }
                    }
                }
            } else if providerManager.hasProviders {
                // Has provider but no balance data
                HStack {
                    Text("暂无余额数据")
                        .font(.system(size: 10))
                        .foregroundColor(AppTheme.textTertiary)
                    Spacer()
                    Text("连接后自动获取")
                        .font(.system(size: 9))
                        .foregroundColor(AppTheme.textTertiary)
                }
            }
        }
    }

    private func usageLabel(for provider: ProviderConfig) -> String {
        provider.connectionStatus == .connected
            ? "余额正常"
            : provider.connectionStatus.rawValue
    }

    private func usageURL(for type: ProviderType) -> URL? {
        switch type {
        case .deepseek: return URL(string: "https://platform.deepseek.com/usage")
        case .qwen: return URL(string: "https://bailian.console.aliyun.com")
        case .anthropic: return URL(string: "https://console.anthropic.com")
        case .openAICompatible: return nil
        }
    }
}
