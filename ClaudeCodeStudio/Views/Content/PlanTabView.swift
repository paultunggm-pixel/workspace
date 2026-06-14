import SwiftUI
import UniformTypeIdentifiers

/// AI-维护的活文档，随对话实时更新。
/// 展示当前项目的最新方案内容、导出、更新提示。
struct PlanTabView: View {
    @EnvironmentObject var appState: AppState
    @State private var planContent = """
    # 项目方案

    暂无方案内容。开始与 Claude 对话后，AI 将自动分析对话内容并更新此方案文档。

    ## 如何使用

    1. 在会话 Tab 中描述你的需求
    2. Claude 会理解你的意图并生方案
    3. 方案会随对话自动刷新

    ## 方案内容结构

    AI 会根据项目特点自行决定内容结构，非固定模板。
    """
    @State private var isExporting = false

    var body: some View {
        VStack(spacing: 0) {
            // Toolbar
            HStack {
                Text("📋 方案")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(AppTheme.textPrimary)
                Spacer()
                Button(action: { isExporting = true }) {
                    Label("导出 MD", systemImage: "square.and.arrow.down")
                        .font(.system(size: 10))
                }
                .buttonStyle(.plain)
                .foregroundColor(AppTheme.accent)
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

            // Content
            ScrollView {
                Text(planContent)
                    .font(.system(size: 12))
                    .foregroundColor(AppTheme.textPrimary)
                    .padding(24)
                    .frame(maxWidth: 700, alignment: .leading)
            }
            .background(Color.white)
        }
        .fileExporter(
            isPresented: $isExporting,
            document: MarkdownDocument(content: planContent),
            contentType: .plainText,
            defaultFilename: "方案.md"
        ) { _ in }
    }
}

/// Wrapper for Markdown file export
struct MarkdownDocument: FileDocument {
    static var readableContentTypes: [UTType] { [.plainText] }
    var content: String

    init(content: String) {
        self.content = content
    }

    init(configuration: ReadConfiguration) throws {
        if let data = configuration.file.regularFileContents {
            content = String(decoding: data, as: UTF8.self)
        } else {
            content = ""
        }
    }

    func fileWrapper(configuration: WriteConfiguration) throws -> FileWrapper {
        FileWrapper(regularFileWithContents: Data(content.utf8))
    }
}
