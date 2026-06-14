import SwiftUI
import WebKit

// Sample data (must precede struct to avoid forward references)
private let sampleHTML = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Preview</title></head>
<body style="font-family: -apple-system; padding: 20px; background: #f5f5f5;">
  <h1 style="color: #333;">预览示例</h1>
  <p>对话中生成的 HTML 将在此实时渲染。</p>
  <div style="background: white; padding: 16px; border-radius: 8px;">
    <h2 style="margin: 0 0 8px;">卡片组件</h2>
    <p style="color: #666; margin: 0;">这是一个演示卡片。</p>
  </div>
</body>
</html>
"""

private let sampleMarkdown = """
# 示例 Markdown

对话中生成的 .md 文件将在此预览。

## 功能列表

- 实时预览
- 文件切换
- 视口调整
"""

/// Multi-type file preview: HTML (WebView), Images, Markdown.
/// Bottom file tab bar switches between artifact files.
struct PreviewTabView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var chatManager: ChatManager
    @State private var selectedFile: PreviewFile? = nil
    @State private var selectedViewport: ViewportMode = .desktop

    private var dynamicFiles: [PreviewFile] {
        var files: [PreviewFile] = []
        if let session = chatManager.activeSession {
            for (i, msg) in session.messages.filter({ !$0.isStreaming }).enumerated() {
                if msg.content.contains("```html") {
                    let html = extractCodeBlock(from: msg.content, language: "html")
                    if !html.isEmpty {
                        files.append(PreviewFile(name: "response_\(i).html", type: .html, content: html))
                    }
                }
            }
        }
        if files.isEmpty {
            files = [PreviewFile(name: "sample_index.html", type: .html, content: sampleHTML),
                     PreviewFile(name: "sample_README.md", type: .markdown, content: sampleMarkdown)]
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
                Text("🎨 预览")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(AppTheme.textPrimary)
                Spacer()
                Picker("视口", selection: $selectedViewport) {
                    Text("桌面").tag(ViewportMode.desktop)
                    Text("平板").tag(ViewportMode.tablet)
                    Text("手机").tag(ViewportMode.mobile)
                }
                .pickerStyle(.segmented)
                .frame(width: 200)
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

            // Preview area
            ZStack {
                if let file = selectedFile {
                    previewContent(for: file)
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
            if selectedFile == nil { selectedFile = dynamicFiles.last }
        }
        .onReceive(chatManager.$streamingContent) { _ in
            selectedFile = dynamicFiles.last
        }
    }

    private var emptyState: some View {
        VStack(spacing: 12) {
            Image(systemName: "eye")
                .font(.system(size: 36))
                .foregroundColor(AppTheme.textTertiary.opacity(0.4))
            Text("选择文件进行预览")
                .font(.system(size: 12))
                .foregroundColor(AppTheme.textSecondary)
            Text("对话中生成的文件将自动出现在下方")
                .font(.system(size: 10))
                .foregroundColor(AppTheme.textTertiary)
        }
    }

    @ViewBuilder
    private func previewContent(for file: PreviewFile) -> some View {
        switch file.type {
        case .html:
            HTMLWebView(html: file.content)
                .frame(width: viewportWidth, height: viewportHeight)
                .clipShape(RoundedRectangle(cornerRadius: 8))
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(AppTheme.dividerGray, lineWidth: 1)
                )
                .shadow(color: .black.opacity(0.06), radius: 8)
        case .image:
            Image(systemName: "photo")
                .font(.system(size: 60))
                .foregroundColor(AppTheme.textTertiary.opacity(0.3))
        case .markdown:
            ScrollView {
                Text(file.content)
                    .font(.system(size: 12))
                    .padding(24)
                    .frame(maxWidth: 700, alignment: .leading)
            }
        }
    }

    private var fileTabBar: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 0) {
                ForEach(dynamicFiles) { file in
                    Button(action: { selectedFile = file }) {
                        HStack(spacing: 4) {
                            Image(systemName: file.type.icon)
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

    // Viewport sizing
    private var viewportWidth: CGFloat {
        switch selectedViewport {
        case .desktop: return 800
        case .tablet: return 500
        case .mobile: return 320
        }
    }

    private var viewportHeight: CGFloat {
        switch selectedViewport {
        case .desktop: return 500
        case .tablet: return 600
        case .mobile: return 500
        }
    }

    enum ViewportMode: Hashable {
        case desktop, tablet, mobile
    }
}

/// Simple file model for preview
struct PreviewFile: Identifiable {
    let id = UUID()
    let name: String
    let type: PreviewFileType
    let content: String

    enum PreviewFileType {
        case html, image, markdown

        var icon: String {
            switch self {
            case .html: return "chevron.left.forwardslash.chevron.right"
            case .image: return "photo"
            case .markdown: return "doc.richtext"
            }
        }
    }
}

// MARK: - HTML WebView wrapper

struct HTMLWebView: NSViewRepresentable {
    let html: String

    func makeNSView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        let webView = WKWebView(frame: .zero, configuration: config)
        webView.loadHTMLString(html, baseURL: nil)
        return webView
    }

    func updateNSView(_ nsView: WKWebView, context: Context) {}
}
