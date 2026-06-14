import SwiftUI

/// Three preset model speed-tier buttons: Flash / Pro / Opus
struct QuickSwitchButtons: View {
    @EnvironmentObject var providerManager: ProviderManager

    var body: some View {
        HStack(spacing: 4) {
            ForEach(ModelTier.allCases, id: \.self) { tier in
                Button(action: {
                    providerManager.setModelTier(tier)
                    if let idx = providerManager.store.providers.firstIndex(where: { $0.id == providerManager.store.activeProviderId }),
                       let model = providerManager.store.providers[idx].models.dropFirst(tier == .flash ? 0 : tier == .pro ? 1 : 2).first {
                        providerManager.store.providers[idx].defaultModel = model
                        providerManager.objectWillChange.send()
                        providerManager.saveToDisk()
                    }
                }) {
                    Text(tier.icon + " " + tier.rawValue)
                        .font(.system(size: 10, weight: providerManager.store.activeModelTier == tier ? .semibold : .regular))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 4)
                }
                .buttonStyle(.plain)
                .foregroundColor(
                    providerManager.store.activeModelTier == tier
                        ? AppTheme.accent
                        : AppTheme.textSecondary
                )
                .background(
                    RoundedRectangle(cornerRadius: 5)
                        .fill(
                            providerManager.store.activeModelTier == tier
                                ? AppTheme.accentBackground
                                : Color.clear
                        )
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 5)
                        .stroke(
                            providerManager.store.activeModelTier == tier
                                ? AppTheme.accent
                                : Color.clear,
                            lineWidth: 1
                        )
                )
            }
        }
    }
}
