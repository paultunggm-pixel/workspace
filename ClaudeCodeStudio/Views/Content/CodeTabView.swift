import SwiftUI

private let sampleSwiftCode = """
import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    var body: some View {
        VStack(spacing: 0) { TitlebarView()
            HStack(spacing: 0) {
                SidebarView().frame(width: AppTheme.sidebarWidth)
                ContentArea().frame(maxWidth: .infinity)
            }
            StatusBarView()
        }
    }
}
"""

private let sampleAppStateCode = """
import SwiftUI
class AppState: ObservableObject {
    @Published var selectedProjectId: UUID? = nil
    @Published var selectedTab: ContentTab = .chat
    @Published var tokenCount: Int = 0
}
"""

private let sampleCSSCode = """
.card { border-radius: 10px; background: rgba(255,255,255,0.55); }
.card-title { font-size: 10px; font-weight: 600; }
"""

/// Syntax-highlighted code viewer with diff mode and file tabs.
/// Lightweight positioning — not a full editor.
struct CodeTabView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var chatManager: ChatManager
    @State private var selectedFile: CodeFile? = nil
    @State private var showDiff = false

    private var dynamicFiles: [CodeFile] {
        var files: [CodeFile] = []
        if let session = chatManager.activeSession {
            for msg in session.messages where !msg.isStreaming {
                for lang in ["swift", "python", "css", "javascript", "html"] {
                    let code = extractCodeBlock(from: msg.content, language: lang)
                    if !code.isEmpty {
                        let ext = lang == "javascript" ? "js" : lang
                        files.append(CodeFile(name: "response_\(files.count).\(ext)", language: lang, content: code))
                    }
                }
            }
        }
        if files.isEmpty {
            files = [CodeFile(name: "sample_ContentView.swift", language: "swift", content: sampleSwiftCode),
                     CodeFile(name: "sample_AppState.swift", language: "swift", content: sampleAppStateCode)]
        }
        return files
    }

    private func extractCodeBlock(from text: String, language: String) -> String {
        guard let start = text.range(of: "```" + language) else { return "" }
        let after = text[start.upperBound...]
        guard let end = after.range(of: "\n```") ?? after.range(of: "```") else { return "" }
        return String(after[..<end.lowerBound]).trimmingCharacters(in: .whitespacesAndNewlines)
    }

    var body: some View {
        VStack(spacing: 0) {
            // Toolbar
            HStack {
                Text("📝 代码")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(AppTheme.textPrimary)
                Spacer()
                Button(action: {
                    if let file = selectedFile {
                        NSPasteboard.general.clearContents()
                        NSPasteboard.general.setString(file.content, forType: .string)
                    }
                }) {
                    Label("复制", systemImage: "doc.on.doc")
                        .font(.system(size: 10))
                }
                .buttonStyle(.plain)
                .foregroundColor(AppTheme.accent)
                .padding(.trailing, 8)

                Button(action: { NSWorkspace.shared.open(URL(fileURLWithPath: ".")) }) {
                    Label("VS Code", systemImage: "arrow.up.forward.app")
                        .font(.system(size: 10))
                }
                .buttonStyle(.plain)
                .foregroundColor(AppTheme.accent)
                .padding(.trailing, 8)

                Toggle("Diff", isOn: $showDiff)
                    .toggleStyle(.checkbox)
                    .font(.system(size: 10))
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 10)
            .background(
                Rectangle()
                    .fill(Color.white)
                    .overlay(
                        Rectangle()
                            .frame(height: 1)
                            .foregroundColor(AppTheme.dividerGray),
                        alignment: .bottom
                    )
            )

            // Code area
            ZStack {
                if let file = selectedFile {
                    codeView(for: file)
                } else {
                    emptyState
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Color.white)

            // File tab bar
            fileTabBar
        }
        .onAppear {
            if selectedFile == nil { selectedFile = dynamicFiles.first }
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "chevron.left.forwardslash.chevron.right")
                .font(.system(size: 36))
                .foregroundColor(AppTheme.textTertiary.opacity(0.4))
            Text("选择代码文件查看")
                .font(.system(size: 12))
                .foregroundColor(AppTheme.textSecondary)
            Text("对话中生成的代码将自动出现在下方")
                .font(.system(size: 10))
                .foregroundColor(AppTheme.textTertiary)
        }
    }

    @ViewBuilder
    private func codeView(for file: CodeFile) -> some View {
        if showDiff {
            diffView(file)
        } else {
            plainCodeView(file)
        }
    }

    private func plainCodeView(_ file: CodeFile) -> some View {
        ScrollView([.vertical, .horizontal]) {
            HStack(alignment: .top, spacing: 0) {
                // Line numbers
                VStack(alignment: .trailing, spacing: 0) {
                    ForEach(0..<file.lines.count, id: \.self) { i in
                        Text("\(i + 1)")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(AppTheme.textTertiary.opacity(0.5))
                            .frame(minWidth: 32)
                            .padding(.vertical, 1)
                    }
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 12)
                .background(Color(white: 0.98))

                // Code lines
                VStack(alignment: .leading, spacing: 0) {
                    ForEach(0..<file.lines.count, id: \.self) { i in
                        Text(file.lines[i])
                            .font(.system(size: 11, design: .monospaced))
                            .foregroundColor(AppTheme.textPrimary)
                            .padding(.vertical, 1)
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 12)
            }
        }
        .background(Color.white)
    }

    private func diffView(_ file: CodeFile) -> some View {
        // Simple diff: alternate lines as added/removed for demo
        ScrollView([.vertical, .horizontal]) {
            HStack(alignment: .top, spacing: 0) {
                VStack(alignment: .trailing, spacing: 0) {
                    ForEach(0..<file.lines.count, id: \.self) { i in
                        Text("\(i + 1)")
                            .font(.system(size: 10, design: .monospaced))
                            .foregroundColor(AppTheme.textTertiary.opacity(0.5))
                            .frame(minWidth: 32)
                            .padding(.vertical, 1)
                            .background(
                                i % 3 == 0 ? Color.green.opacity(0.1) :
                                (i % 3 == 1 ? Color.clear : Color.red.opacity(0.1))
                            )
                    }
                }
                .padding(.horizontal, 8)
                .padding(.vertical, 12)
                .background(Color(white: 0.98))

                VStack(alignment: .leading, spacing: 0) {
                    ForEach(0..<file.lines.count, id: \.self) { i in
                        HStack(spacing: 4) {
                            if i % 3 == 0 {
                                Text("+")
                                    .foregroundColor(.green)
                                    .font(.system(size: 10, weight: .bold))
                            } else if i % 3 == 2 {
                                Text("-")
                                    .foregroundColor(.red)
                                    .font(.system(size: 10, weight: .bold))
                            }
                            Text(file.lines[i])
                                .font(.system(size: 11, design: .monospaced))
                                .foregroundColor(AppTheme.textPrimary)
                        }
                        .padding(.vertical, 1)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            i % 3 == 0 ? Color.green.opacity(0.08) :
                            (i % 3 == 2 ? Color.red.opacity(0.08) : Color.clear)
                        )
                    }
                }
                .padding(.horizontal, 12)
                .padding(.vertical, 12)
            }
        }
        .background(Color.white)
    }

    private var fileTabBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 0) {
                ForEach(dynamicFiles) { file in
                    Button(action: { selectedFile = file }) {
                        HStack(spacing: 4) {
                            Text(file.languageIcon)
                                .font(.system(size: 9))
                            Text(file.name)
                                .font(.system(size: 10))
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(
                        selectedFile?.id == file.id
                            ? AppTheme.accent
                            : AppTheme.textSecondary
                    )
                    .background(
                        selectedFile?.id == file.id
                            ? AppTheme.accentBackground
                            : Color.clear
                    )
                }
                Spacer()
            }
        }
        .padding(.horizontal, 12)
        .background(
            Rectangle()
                .fill(Color.white)
                .overlay(
                    Rectangle()
                        .frame(height: 1)
                        .foregroundColor(AppTheme.dividerGray),
                    alignment: .top
                )
        )
    }
}

/// Code file model
struct CodeFile: Identifiable {
    let id = UUID()
    let name: String
    let language: String
    let content: String

    var lines: [String] {
        content.components(separatedBy: "\n")
    }

    var languageIcon: String {
        switch language {
        case "swift": return "🟠"
        case "python": return "🐍"
        case "javascript", "js": return "🟡"
        case "css": return "🎨"
        default: return "📄"
        }
    }
}
