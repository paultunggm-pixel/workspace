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
            Button(action: {
                isExpanded.toggle()
                appState.selectedProjectId = project.id.uuidString
                NotificationCenter.default.post(name: .switchToProject, object: project.id)
            }) {
                HStack(spacing: 4) {
                    if !projectManager.store.conversations(in: project).isEmpty {
                        Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                            .font(.system(size: 8, weight: .medium))
                            .foregroundColor(AppTheme.textTertiary)
                    } else {
                        Spacer().frame(width: 10)
                    }
                    Text(project.icon).font(.system(size: 12))
                    Text(project.name)
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(appState.selectedProjectId == project.id.uuidString ? AppTheme.accent : .primary)
                        .lineLimit(1)
                    Spacer()
                }
                .padding(.horizontal, 6).padding(.vertical, 5)
                .contentShape(Rectangle())
            }
            .buttonStyle(.plain)
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

// MARK: - Delete Project Dialog (3-step)

struct DeleteProjectDialog: View {
    let project: Project
    @EnvironmentObject var projectManager: ProjectManager
    @Environment(\.dismiss) private var dismiss

    @State private var step = 0
    @State private var confirmName = ""
    @State private var countdown = 5
    @State private var timer: Timer?

    private var conversationCount: Int {
        projectManager.store.conversations(in: project).count
    }

    var body: some View {
        VStack(spacing: 20) {
            Text("🗑️ 删除项目")
                .font(.headline)

            switch step {
            case 0:
                Text("请输入项目名称「\(project.name)」确认删除")
                    .font(.system(size: 12))
                    .foregroundColor(AppTheme.textSecondary)
                TextField("项目名称", text: $confirmName)
                    .textFieldStyle(.roundedBorder)
                    .frame(width: 220)
                HStack(spacing: 12) {
                    Button("取消", action: { dismiss() })
                    Button("下一步") {
                        if confirmName == project.name { step = 1 }
                    }
                    .disabled(confirmName != project.name)
                }
            case 1:
                VStack(spacing: 8) {
                    Text("⚠️ 该项目包含 \(conversationCount) 个会话")
                        .font(.system(size: 12))
                        .foregroundColor(.red)
                    Text("删除后不可恢复")
                        .font(.system(size: 11))
                        .foregroundColor(AppTheme.textTertiary)
                }
                HStack(spacing: 12) {
                    Button("取消", action: { dismiss() })
                    Button("确认删除", role: .destructive) {
                        step = 2
                        startCountdown()
                    }
                }
            case 2:
                Text("确认删除 (\(countdown)秒)")
                    .font(.system(size: 12))
                    .foregroundColor(AppTheme.textSecondary)
                HStack(spacing: 12) {
                    Button("取消") {
                        timer?.invalidate()
                        dismiss()
                    }
                    Button("确认删除", role: .destructive) {
                        timer?.invalidate()
                        projectManager.removeProject(project)
                        dismiss()
                    }
                    .disabled(countdown > 0)
                }
            default: EmptyView()
            }
        }
        .padding(30)
        .frame(width: 320, height: 240)
        .onDisappear { timer?.invalidate() }
    }

    private func startCountdown() {
        countdown = 5
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { t in
            if countdown > 0 {
                countdown -= 1
            } else {
                t.invalidate()
            }
        }
    }
}
