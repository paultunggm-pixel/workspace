import Foundation

/// Supported AI model providers
enum ProviderType: String, CaseIterable, Codable {
    case deepseek = "DeepSeek"
    case qwen = "Qwen"
    case anthropic = "Anthropic"
    case openAICompatible = "OpenAI 兼容"

    var icon: String {
        switch self {
        case .deepseek: return "🐋"
        case .qwen: return "☁️"
        case .anthropic: return "🧪"
        case .openAICompatible: return "⚙️"
        }
    }

    var currency: String {
        switch self {
        case .deepseek, .qwen: return "¥"
        case .anthropic, .openAICompatible: return "$"
        }
    }

    var defaultEndpoint: String {
        switch self {
        case .deepseek: return "https://api.deepseek.com/v1"
        case .qwen: return "https://dashscope.aliyuncs.com/compatible-mode/v1"
        case .anthropic: return "https://api.anthropic.com/v1"
        case .openAICompatible: return ""
        }
    }
}

/// Preset model speed tiers for quick switching
enum ModelTier: String, CaseIterable, Codable {
    case flash = "Flash"
    case pro = "Pro"
    case opus = "Opus"

    var icon: String {
        switch self {
        case .flash: return "⚡"
        case .pro: return "🧠"
        case .opus: return "🔮"
        }
    }
}

/// Individual provider configuration
struct ProviderConfig: Identifiable, Codable, Equatable {
    let id: UUID
    var type: ProviderType
    var label: String
    var endpoint: String
    var isEnabled: Bool
    var defaultModel: String
    var models: [String]
    var lastBalance: Double?
    var lastBalanceDate: Date?
    var connectionStatus: ConnectionStatus

    init(
        id: UUID = UUID(),
        type: ProviderType,
        label: String? = nil,
        endpoint: String? = nil,
        isEnabled: Bool = true,
        defaultModel: String = "",
        models: [String] = [],
        lastBalance: Double? = nil,
        lastBalanceDate: Date? = nil,
        connectionStatus: ConnectionStatus = .disconnected
    ) {
        self.id = id
        self.type = type
        self.label = label ?? type.rawValue
        self.endpoint = endpoint ?? type.defaultEndpoint
        self.isEnabled = isEnabled
        self.defaultModel = defaultModel
        self.models = models
        self.lastBalance = lastBalance
        self.lastBalanceDate = lastBalanceDate
        self.connectionStatus = connectionStatus
    }

    var keySummary: String {
        "sk-●●●●●●●●●●●●"
    }

    enum ConnectionStatus: String, Codable {
        case connected = "已连接"
        case disconnected = "未连接"
        case error = "异常"
        case rateLimited = "限流"
    }
}

/// Stores all provider configurations
struct ProviderStore: Codable {
    var providers: [ProviderConfig] = []
    var activeProviderId: UUID? = nil
    var activeModelTier: ModelTier = .pro
}
