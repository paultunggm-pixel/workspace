import Foundation

/// Top-level category grouping projects
struct Category: Identifiable, Codable, Equatable {
    var id: UUID
    var name: String
    var icon: String
    var isExpanded: Bool
    var projectIds: [UUID]

    init(id: UUID = UUID(), name: String, icon: String = "📂", isExpanded: Bool = true, projectIds: [UUID] = []) {
        self.id = id
        self.name = name
        self.icon = icon
        self.isExpanded = isExpanded
        self.projectIds = projectIds
    }

    static let uncategorized = UUID(uuidString: "00000000-0000-0000-0000-000000000001")! // sentinel for "未分类"
}

/// A project containing conversations and artifacts
struct Project: Identifiable, Codable, Equatable {
    var id: UUID
    var name: String
    var icon: String
    var description: String
    var categoryId: UUID
    var conversationIds: [UUID]
    var createdAt: Date
    var updatedAt: Date

    init(
        id: UUID = UUID(),
        name: String,
        icon: String = "📁",
        description: String = "",
        categoryId: UUID = Category.uncategorized,
        conversationIds: [UUID] = [],
        createdAt: Date = Date(),
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.name = name
        self.icon = icon
        self.description = description
        self.categoryId = categoryId
        self.conversationIds = conversationIds
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

/// A conversation within a project
struct Conversation: Identifiable, Codable, Equatable {
    var id: UUID
    var title: String
    var projectId: UUID
    var status: ConversationStatus
    var messageCount: Int
    var createdAt: Date
    var updatedAt: Date

    init(
        id: UUID = UUID(),
        title: String = "新会话",
        projectId: UUID,
        status: ConversationStatus = .active,
        messageCount: Int = 0,
        createdAt: Date = Date(),
        updatedAt: Date = Date()
    ) {
        self.id = id
        self.title = title
        self.projectId = projectId
        self.status = status
        self.messageCount = messageCount
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }

    enum ConversationStatus: String, Codable {
        case active = "活跃"
        case paused = "暂停"
        case completed = "完成"
    }

    /// Group label for time-based grouping
    var timeGroup: String {
        let calendar = Calendar.current
        if calendar.isDateInToday(createdAt) { return "今天" }
        if calendar.isDateInYesterday(createdAt) { return "昨天" }
        let formatter = DateFormatter()
        formatter.dateFormat = "M月d日"
        return formatter.string(from: createdAt)
    }
}

/// Thread-safe store for all project data
struct ProjectStore: Codable {
    var categories: [Category] = [Category(name: "未分类", isExpanded: true)]
    var projects: [Project] = []
    var conversations: [Conversation] = []

    /// Ensure uncategorized exists
    mutating func ensureUncategorized() {
        if !categories.contains(where: { $0.id == Category.uncategorized }) {
            categories.insert(Category(id: Category.uncategorized, name: "未分类", isExpanded: true), at: 0)
        }
    }

    func projects(in category: Category) -> [Project] {
        projects.filter { $0.categoryId == category.id }
    }

    func conversations(in project: Project) -> [Conversation] {
        conversations.filter { $0.projectId == project.id }
            .sorted { $0.createdAt > $1.createdAt }
    }
}
