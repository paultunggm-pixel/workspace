import Foundation
import SwiftUI

/// Central manager for provider configurations, persistence, and keychain operations.
/// Owns the ProviderStore and exposes it as published state.
class ProviderManager: ObservableObject {
    @Published var store = ProviderStore()

    private let configDir: URL
    private let providersFile: URL

    init() {
        let appSupport = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".claude-code-studio")
        configDir = appSupport
        providersFile = appSupport.appendingPathComponent("providers.json")
        loadFromDisk()
        if store.providers.isEmpty { seedSampleData() }
    }

    // MARK: - Persistence

    private func loadFromDisk() {
        guard let data = try? Data(contentsOf: providersFile) else { return }
        let decoder = JSONDecoder()
        if let loaded = try? decoder.decode(ProviderStore.self, from: data) {
            store = loaded
        }
    }

    private func seedSampleData() {
        let dp = ProviderConfig(
            type: .deepseek,
            label: "DeepSeek Pro",
            defaultModel: "deepseek-chat",
            models: ["deepseek-chat", "deepseek-reasoner"],
            lastBalance: 86.50,
            lastBalanceDate: Date(),
            connectionStatus: .connected
        )
        let qw = ProviderConfig(
            type: .qwen,
            label: "Qwen Turbo",
            defaultModel: "qwen-turbo",
            models: ["qwen-turbo", "qwen-plus", "qwen-max"],
            lastBalance: 42.00,
            lastBalanceDate: Date(),
            connectionStatus: .connected
        )
        store.providers = [dp, qw]
        store.activeProviderId = dp.id
        store.activeModelTier = .pro
        saveToDisk()
    }

    func saveToDisk() {
        try? FileManager.default.createDirectory(at: configDir,
                                                  withIntermediateDirectories: true)
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        if let data = try? encoder.encode(store) {
            try? data.write(to: providersFile, options: .atomic)
        }
    }

    // MARK: - Provider CRUD

    func addProvider(type: ProviderType, label: String? = nil, endpoint: String? = nil, apiKey: String) throws {
        let provider = ProviderConfig(type: type, label: label, endpoint: endpoint)
        store.providers.append(provider)
        if store.activeProviderId == nil {
            store.activeProviderId = provider.id
        }
        try saveKey(apiKey, for: provider.id.uuidString)
        saveToDisk()
    }

    func removeProvider(_ provider: ProviderConfig) {
        store.providers.removeAll { $0.id == provider.id }
        if store.activeProviderId == provider.id {
            store.activeProviderId = store.providers.first?.id
        }
        try? KeychainManager.delete(for: provider.id.uuidString)
        saveToDisk()
    }

    func setActiveProvider(_ id: UUID) {
        guard store.providers.contains(where: { $0.id == id }) else { return }
        store.activeProviderId = id
        saveToDisk()
    }

    func setModelTier(_ tier: ModelTier) {
        store.activeModelTier = tier
        saveToDisk()
    }

    func updateBalance(providerId: UUID, amount: Double) {
        guard let idx = store.providers.firstIndex(where: { $0.id == providerId }) else { return }
        store.providers[idx].lastBalance = amount
        store.providers[idx].lastBalanceDate = Date()
        saveToDisk()
    }

    func updateConnectionStatus(providerId: UUID, status: ProviderConfig.ConnectionStatus) {
        guard let idx = store.providers.firstIndex(where: { $0.id == providerId }) else { return }
        store.providers[idx].connectionStatus = status
        saveToDisk()
    }

    // MARK: - Keychain

    func saveKey(_ key: String, for providerId: String) throws {
        try KeychainManager.save(key: key, for: providerId)
    }

    func readKey(for providerId: String) throws -> String {
        try KeychainManager.read(for: providerId)
    }

    func hasKey(for providerId: String) -> Bool {
        KeychainManager.exists(for: providerId)
    }

    func deleteKey(for providerId: String) throws {
        try KeychainManager.delete(for: providerId)
    }

    // MARK: - Computed

    var activeProvider: ProviderConfig? {
        store.providers.first(where: { $0.id == store.activeProviderId })
    }

    var hasProviders: Bool {
        !store.providers.isEmpty
    }

    /// Balance as percentage (0.0-1.0), or nil if unknown
    var balancePercentage: Double? {
        // Default cap: assume ¥100 or $50
        guard let balance = activeProvider?.lastBalance else { return nil }
        let cap: Double = activeProvider?.type.currency == "$" ? 50.0 : 100.0
        return min(balance / cap, 1.0)
    }

    var balanceColor: Color {
        guard let pct = balancePercentage else { return AppTheme.textTertiary }
        if pct > 0.5 { return .green }
        if pct > 0.1 { return .yellow }
        return .red
    }
}
