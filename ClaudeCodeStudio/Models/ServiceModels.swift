import Foundation

/// A connected service (MCP or otherwise)
struct ServiceConfig: Identifiable, Codable, Equatable {
    var id: UUID
    var name: String
    var category: ServiceCategory
    var description: String
    var status: ServiceStatus
    var endpoint: String
    var authMethod: AuthMethod
    var dailyCalls: Int
    var tools: [String]

    init(
        id: UUID = UUID(),
        name: String,
        category: ServiceCategory,
        description: String = "",
        status: ServiceStatus = .disconnected,
        endpoint: String = "",
        authMethod: AuthMethod = .apiKey,
        dailyCalls: Int = 0,
        tools: [String] = []
    ) {
        self.id = id
        self.name = name
        self.category = category
        self.description = description
        self.status = status
        self.endpoint = endpoint
        self.authMethod = authMethod
        self.dailyCalls = dailyCalls
        self.tools = tools
    }

    enum ServiceStatus: String, Codable {
        case connected = "已连接"
        case disconnected = "未连接"
        case error = "异常"
        case rateLimited = "限流"
        case pendingAuth = "待授权"
    }

    enum AuthMethod: String, Codable {
        case apiKey = "API Key"
        case oauth = "OAuth"
        case token = "Token"
        case none = "无"
    }

    var statusColor: String {
        switch status {
        case .connected: return "🟢"
        case .disconnected: return "⚪"
        case .error: return "🔴"
        case .rateLimited: return "🟡"
        case .pendingAuth: return "⚪"
        }
    }
}

/// Service categories for the catalog
enum ServiceCategory: String, CaseIterable, Codable {
    case devTools = "🛠 开发工具"
    case dataStorage = "🗄 数据存储"
    case aiSearch = "🤖 AI & 搜索"
    case contentMedia = "🎨 内容 & 媒体"
    case deployOps = "🚀 部署 & 运维"
    case custom = "🔌 自定义"

    var icon: String {
        switch self {
        case .devTools: return "🛠"
        case .dataStorage: return "🗄"
        case .aiSearch: return "🤖"
        case .contentMedia: return "🎨"
        case .deployOps: return "🚀"
        case .custom: return "🔌"
        }
    }

    var defaultServices: [String] {
        switch self {
        case .devTools: return ["GitHub", "Docker", "GitLab"]
        case .dataStorage: return ["阿里云 OSS", "PostgreSQL", "Redis"]
        case .aiSearch: return ["DeepSeek", "Exa", "Firecrawl"]
        case .contentMedia: return ["Runway", "Adobe Creative", "Notion"]
        case .deployOps: return ["GitHub Pages", "Vercel", "Cloudflare"]
        case .custom: return ["MCP 协议", "HTTP API", "本地脚本"]
        }
    }
}
