import SwiftUI

extension Notification.Name {
    static let switchToProject = Notification.Name("switchToProject")
}

// MARK: - Project List Card (container)

struct ProjectListCard: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var projectManager: ProjectManager
    @State private var newName = ""
    @State private var showNewProject = false

    var body: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("📁 项目")
                    .font(.system(size: 11, weight: .semibold)).foregroundColor(.primary)
                Spacer()
                Button(action: { showNewProject = true }) {
                    Image(systemName: "plus").font(.system(size: 10, weight: .semibold)).foregroundColor(AppTheme.textSecondary)
                }.buttonStyle(.plain)
            }

            if projectManager.store.categories.isEmpty && projectManager.store.projects.isEmpty {
                emptyState
            } else {
                treeContent
            }
        }
        .padding(10)
        .background { RoundedRectangle(cornerRadius: AppTheme.cardRadius).fill(AppTheme.cardBackground) }
        .overlay { RoundedRectangle(cornerRadius: AppTheme.cardRadius).stroke(AppTheme.cardBorder, lineWidth: 1) }
        .sheet(isPresented: $showNewProject) {
            VStack(spacing: 16) {
                Text("📁 新建项目").font(.headline)
                TextField("项目名称", text: $newName).textFieldStyle(.roundedBorder).frame(width: 200)
                HStack(spacing: 12) {
                    Button("取消") { newName = ""; showNewProject = false }.keyboardShortcut(.escape)
                    Button("创建") {
                        let n = newName.trimmingCharacters(in: .whitespaces)
                        if !n.isEmpty { projectManager.addProject(name: n) }
                        newName = ""; showNewProject = false
                    }.disabled(newName.trimmingCharacters(in: .whitespaces).isEmpty)
                }
            }.padding(30).frame(width: 280, height: 180)
        }
    }

    private var emptyState: some View {
        VStack(spacing: 6) {
            Text("📁").font(.system(size: 20))
            Text("暂无项目").font(.system(size: 10)).foregroundColor(AppTheme.textTertiary)
            Button(action: { showNewProject = true }) {
                Label("新建项目", systemImage: "plus.circle.fill").font(.system(size: 10))
            }.buttonStyle(.plain).foregroundColor(AppTheme.accent)
        }.frame(maxWidth: .infinity).padding(.vertical, 12)
    }

    private var treeContent: some View {
        ScrollView {
            LazyVStack(spacing: 2, pinnedViews: []) {
                ForEach(projectManager.store.categories) { category in
                    CategoryRow(category: category)
                }

                let categorizedIds = projectManager.store.categories.flatMap { $0.projectIds }
                let orphans = projectManager.store.projects.filter { !categorizedIds.contains($0.id) }
                if !orphans.isEmpty {
                    Divider().padding(.vertical, 2)
                    ForEach(orphans) { project in
                        ProjectRow(project: project)
                    }
                }
            }
        }
        .frame(maxHeight: 220)
    }

    private func newItemSheet(title: String, icon: String, onCreate: @escaping (String) -> Void) -> some View {
        VStack(spacing: 16) {
            Text(icon).font(.system(size: 32))
            Text(title).font(.headline)
            TextField("名称", text: $newName)
                .textFieldStyle(.roundedBorder)
                .frame(width: 200)
            HStack(spacing: 12) {
                Button("取消") {
                    newName = ""
                    showSheet = nil
                }
                .keyboardShortcut(.escape)
                Button("创建") {
                    let name = newName.trimmingCharacters(in: .whitespaces)
                    if !name.isEmpty {
                        onCreate(name)
                    }
                    newName = ""
                    showSheet = nil
                }
                .keyboardShortcut(.return)
                .disabled(newName.trimmingCharacters(in: .whitespaces).isEmpty)
            }
        }
        .padding(30)
        .frame(width: 280, height: 200)
    }
}

// MARK: - Category Row

struct CategoryRow: View {
    let category: Category
    @EnvironmentObject var projectManager: ProjectManager

    var body: some View {
        VStack(spacing: 0) {
            Button(action: { projectManager.toggleCategory(category.id) }) {
                HStack(spacing: 4) {
                    Image(systemName: category.isExpanded ? "chevron.down" : "chevron.right")
                        .font(.system(size: 8, weight: .medium)).foregroundColor(AppTheme.textTertiary)
                    Text(category.icon + " " + category.name)
                        .font(.system(size: 11, weight: .semibold)).foregroundColor(.primary)
                    Spacer()
                    Text("\(projectManager.store.projects(in: category).count)")
                        .font(.system(size: 9)).foregroundColor(AppTheme.textTertiary)
                }
                .padding(.horizontal, 4).padding(.vertical, 3).contentShape(Rectangle())
            }
            .buttonStyle(.plain)

            if category.isExpanded {
                ForEach(projectManager.store.projects(in: category)) { project in
                    ProjectRow(project: project).padding(.leading, 12)
                }
            }
        }
    }
}

// MARK: - Project Row

struct ProjectRow: View {
    let project: Project
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var projectManager: ProjectManager
    @State private var isExpanded = false

    var body: some View {
        VStack(spacing: 0) {
            HStack(spacing: 0) {
                // Expand/collapse chevron
                Button(action: { isExpanded.toggle() }) {
                    Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                        .font(.system(size: 8, weight: .medium))
                        .foregroundColor(AppTheme.textTertiary)
                        .frame(width: 14, height: 24)
                        .contentShape(Rectangle())
                }.buttonStyle(.plain)

                // Project name (click to switch session)
                Button(action: {
                    appState.selectedProjectId = project.id.uuidString
                    NotificationCenter.default.post(name: .switchToProject, object: project.id)
                }) {
                    HStack(spacing: 4) {
                        Text(project.icon).font(.system(size: 12))
                        Text(project.name)
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(appState.selectedProjectId == project.id.uuidString ? AppTheme.accent : .primary)
                            .lineLimit(1)
                        Spacer()
                    }
                    .contentShape(Rectangle())
                }.buttonStyle(.plain)
            }
            .padding(.horizontal, 6).padding(.vertical, 5)
            .background(appState.selectedProjectId == project.id.uuidString ? AppTheme.accentBackground : Color.clear)
            .background(appState.selectedProjectId == project.id.uuidString ? AppTheme.accentBackground : Color.clear)

            if isExpanded {
                ForEach(projectManager.store.conversations(in: project)) { conv in
                    ConversationRow(conversation: conv)
                        .padding(.leading, 16)
                }
            }
        }
    }
}

// MARK: - Conversation Row

struct ConversationRow: View {
    let conversation: Conversation
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var projectManager: ProjectManager

    var body: some View {
        HStack(spacing: 4) {
            Circle().fill(statusColor).frame(width: 5, height: 5)
            Text(conversation.title)
                .font(.system(size: 10))
                .foregroundColor(.primary)
                .lineLimit(1)
            Spacer()
        }
        .padding(.horizontal, 4).padding(.vertical, 3)
        .contentShape(Rectangle())
        .contentShape(Rectangle())
    }

    private var statusColor: Color {
        switch conversation.status {
        case .active: return .green
        case .paused: return .yellow
        case .completed: return .gray
        }
    }
}
// ProjectListCard+CategoryRow+ProjectRow+ConversationRow defined above
