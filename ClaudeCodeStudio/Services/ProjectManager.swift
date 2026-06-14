import Foundation
import SwiftUI

/// Central manager for projects, categories, and conversations.
/// Persists to ~/.claude-code-studio/projects.json
class ProjectManager: ObservableObject {
    @Published var store = ProjectStore()

    private let configDir: URL
    private let projectsFile: URL

    init() {
        let appSupport = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent(".claude-code-studio")
        configDir = appSupport
        projectsFile = appSupport.appendingPathComponent("projects.json")
        loadFromDisk()
        cleanupStore()
        store.ensureUncategorized()
        if store.projects.isEmpty { seedSampleData() }
    }

    // MARK: - Persistence

    private func loadFromDisk() {
        guard let data = try? Data(contentsOf: projectsFile) else { return }
        if let loaded = try? JSONDecoder().decode(ProjectStore.self, from: data) {
            store = loaded
        }
    }

    private func cleanupStore() {
        // Remove duplicate Uncategorized categories (from old UUID() bug)
        var seen = Set<UUID>()
        store.categories.removeAll { cat in
            if cat.name == "未分类" {
                if seen.contains(cat.id) { return true }
                seen.insert(cat.id)
            }
            return false
        }
        // Fix orphaned projects to Uncategorized
        let validIds = Set(store.categories.map { $0.id })
        for i in store.projects.indices {
            if !validIds.contains(store.projects[i].categoryId) {
                store.projects[i].categoryId = Category.uncategorized
            }
        }
        // Remove conversations for deleted projects
        let projectIds = Set(store.projects.map { $0.id })
        store.conversations.removeAll { !projectIds.contains($0.projectId) }
    }

    private func seedSampleData() {
        let dataCat = addCategory(name: "数据分析")
        let devCat = addCategory(name: "产品开发")

        let proj1 = addProject(name: "2026世界杯", icon: "🏆", categoryId: dataCat.id)
        let proj2 = addProject(name: "解题一致性评测", icon: "📊", categoryId: dataCat.id)
        let proj3 = addProject(name: "Claude Code Studio", icon: "🔧", categoryId: devCat.id)

        addConversation(title: "小组赛预测模型优化", projectId: proj1.id)
        addConversation(title: "淘汰赛对阵分析", projectId: proj1.id)
        addConversation(title: "数据源调研", projectId: proj1.id)
        addConversation(title: "多模型对比评测", projectId: proj2.id)
        addConversation(title: "窗口布局设计", projectId: proj3.id)
        addConversation(title: "模型引擎架构", projectId: proj3.id)
    }

    func saveToDisk() {
        try? FileManager.default.createDirectory(at: configDir, withIntermediateDirectories: true)
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted
        if let data = try? encoder.encode(store) {
            try? data.write(to: projectsFile, options: .atomic)
        }
    }

    // MARK: - Category CRUD

    @discardableResult
    func addCategory(name: String, icon: String = "📂") -> Category {
        let cat = Category(name: name, icon: icon)
        store.categories.append(cat)
        objectWillChange.send()
        saveToDisk()
        return cat
    }

    func removeCategory(_ category: Category) throws {
        guard category.id != Category.uncategorized else {
            throw ProjectError.cannotDeleteUncategorized
        }
        guard store.projects(in: category).isEmpty else {
            throw ProjectError.categoryNotEmpty
        }
        store.categories.removeAll { $0.id == category.id }
        objectWillChange.send()
        saveToDisk()
    }

    func toggleCategory(_ categoryId: UUID) {
        if let idx = store.categories.firstIndex(where: { $0.id == categoryId }) {
            store.categories[idx].isExpanded.toggle()
            objectWillChange.send()
        saveToDisk()
        }
    }

    func moveProject(_ projectId: UUID, to categoryId: UUID) {
        guard let pidx = store.projects.firstIndex(where: { $0.id == projectId }),
              store.categories.contains(where: { $0.id == categoryId }) else { return }

        let oldCatId = store.projects[pidx].categoryId
        store.projects[pidx].categoryId = categoryId

        // Remove from old category's projectIds
        if let oci = store.categories.firstIndex(where: { $0.id == oldCatId }) {
            store.categories[oci].projectIds.removeAll { $0 == projectId }
        }
        // Add to new category's projectIds
        if let nci = store.categories.firstIndex(where: { $0.id == categoryId }) {
            store.categories[nci].projectIds.append(projectId)
        }
        objectWillChange.send()
        saveToDisk()
    }

    // MARK: - Project CRUD

    @discardableResult
    func addProject(name: String, icon: String = "📁", categoryId: UUID = Category.uncategorized) -> Project {
        let project = Project(name: name, icon: icon, categoryId: categoryId)
        store.projects.append(project)
        if let idx = store.categories.firstIndex(where: { $0.id == categoryId }) {
            store.categories[idx].projectIds.append(project.id)
        }
        objectWillChange.send()
        saveToDisk()
        return project
    }

    func removeProject(_ project: Project) {
        // Remove all conversations in this project
        store.conversations.removeAll { $0.projectId == project.id }
        // Remove project
        store.projects.removeAll { $0.id == project.id }
        // Remove from category
        if let idx = store.categories.firstIndex(where: { $0.id == project.categoryId }) {
            store.categories[idx].projectIds.removeAll { $0 == project.id }
        }
        objectWillChange.send()
        saveToDisk()
    }

    func renameProject(_ projectId: UUID, to name: String) {
        if let idx = store.projects.firstIndex(where: { $0.id == projectId }) {
            store.projects[idx].name = name
            store.projects[idx].updatedAt = Date()
            objectWillChange.send()
        saveToDisk()
        }
    }

    func updateProjectIcon(_ projectId: UUID, icon: String) {
        if let idx = store.projects.firstIndex(where: { $0.id == projectId }) {
            store.projects[idx].icon = icon
            objectWillChange.send()
        saveToDisk()
        }
    }

    // MARK: - Conversation CRUD

    @discardableResult
    func addConversation(title: String = "新会话", projectId: UUID) -> Conversation {
        let conv = Conversation(title: title, projectId: projectId)
        store.conversations.append(conv)
        if let idx = store.projects.firstIndex(where: { $0.id == projectId }) {
            store.projects[idx].conversationIds.append(conv.id)
            store.projects[idx].updatedAt = Date()
        }
        objectWillChange.send()
        saveToDisk()
        return conv
    }

    func removeConversation(_ conversation: Conversation) {
        let projectId = conversation.projectId
        store.conversations.removeAll { $0.id == conversation.id }
        if let idx = store.projects.firstIndex(where: { $0.id == projectId }) {
            store.projects[idx].conversationIds.removeAll { $0 == conversation.id }
        }
        objectWillChange.send()
        saveToDisk()
    }

    func updateConversationStatus(_ conversationId: UUID, status: Conversation.ConversationStatus) {
        if let idx = store.conversations.firstIndex(where: { $0.id == conversationId }) {
            store.conversations[idx].status = status
            store.conversations[idx].updatedAt = Date()
            objectWillChange.send()
        saveToDisk()
        }
    }

    // MARK: - Computed

    func project(for id: UUID) -> Project? {
        store.projects.first(where: { $0.id == id })
    }

    func category(for id: UUID) -> Category? {
        store.categories.first(where: { $0.id == id })
    }
}

enum ProjectError: LocalizedError {
    case cannotDeleteUncategorized
    case categoryNotEmpty

    var errorDescription: String? {
        switch self {
        case .cannotDeleteUncategorized: return "未分类是默认分类，不可删除"
        case .categoryNotEmpty: return "请先移走项目再删除此分类"
        }
    }
}
