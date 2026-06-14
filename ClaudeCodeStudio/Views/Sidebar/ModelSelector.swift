import SwiftUI

struct ModelSelector: View {
    @EnvironmentObject var providerManager: ProviderManager

    private var availableProviders: [ProviderConfig] {
        providerManager.store.providers
    }

    var body: some View {
        HStack(spacing: 6) {
            if let active = providerManager.activeProvider {
                Text(active.type.icon).font(.system(size: 13))
                Picker("", selection: Binding(
                    get: { providerManager.store.activeProviderId ?? UUID() },
                    set: { providerManager.setActiveProvider($0) }
                )) {
                    ForEach(availableProviders) { provider in
                        Text(provider.label).tag(provider.id)
                    }
                }
                .labelsHidden()
                Spacer()
                Text(active.connectionStatus.rawValue)
                    .font(.system(size: 9))
                    .foregroundColor(statusColor(active.connectionStatus))
            } else {
                Text("选择模型")
                    .font(.system(size: 11))
                    .foregroundColor(AppTheme.textSecondary)
                Spacer()
            }
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 5)
        .background(
            RoundedRectangle(cornerRadius: 6)
                .fill(Color.black.opacity(0.04))
        )
    }

    private func statusColor(_ status: ProviderConfig.ConnectionStatus) -> Color {
        switch status {
        case .connected: return .green
        case .disconnected: return AppTheme.textTertiary
        case .error: return .red
        case .rateLimited: return .yellow
        }
    }
}
