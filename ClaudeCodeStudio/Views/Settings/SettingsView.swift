import SwiftUI

/// Global settings panel — CLAUDE.md configuration, style, and project overview.
/// Apple Settings-style grouped list.
struct SettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var selectedSection: SettingsSection = .communication

    var body: some View {
        HStack(spacing: 0) {
            // Sidebar sections
            VStack(alignment: .leading, spacing: 0) {
                ForEach(SettingsSection.allCases, id: \.self) { section in
                    Button(action: { selectedSection = section }) {
                        HStack(spacing: 6) {
                            Text(section.icon)
                            Text(section.rawValue)
                                .font(.system(size: 11, weight: selectedSection == section ? .semibold : .regular))
                        }
                        .padding(.horizontal, 12)
                        .padding(.vertical, 8)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .background(
                            selectedSection == section
                                ? AppTheme.accentBackground
                                : Color.clear
                        )
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(
                        selectedSection == section
                            ? AppTheme.accent
                            : AppTheme.textSecondary
                    )
                }
                Spacer()
            }
            .frame(width: 180)
            .background(Color(white: 0.97))

            Divider()

            // Content area
            ScrollView {
                Group {
                    switch selectedSection {
                    case .communication: CommunicationSettings()
                    case .permissions: PermissionsSettings()
                    case .codingStyle: CodingStyleSettings()
                    case .customRules: CustomRulesSettings()
                    case .projectOverview: ProjectOverviewSettings()
                    }
                }
                .padding(24)
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .frame(width: 420)
            .background(Color.white)
        }
        .frame(width: 620, height: 480)
    }
}

enum SettingsSection: String, CaseIterable {
    case communication = "交流偏好"
    case permissions = "权限与安全"
    case codingStyle = "编码风格"
    case customRules = "自定义规则"
    case projectOverview = "项目概览"

    var icon: String {
        switch self {
        case .communication: return "💬"
        case .permissions: return "🔐"
        case .codingStyle: return "💻"
        case .customRules: return "📝"
        case .projectOverview: return "📋"
        }
    }
}

// MARK: - Communication Settings

struct CommunicationSettings: View {
    @AppStorage("settings.language") private var language = "简体中文"
    @AppStorage("settings.replyStyle") private var replyStyle = "简洁"
    let languages = ["简体中文", "繁體中文", "English"]
    let styles = ["简洁", "适度", "详尽"]

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            sectionHeader("交流偏好")

            settingGroup {
                settingRow("工作语言") {
                    HStack(spacing: 6) {
                        ForEach(languages, id: \.self) { lang in
                            Button(action: { language = lang }) {
                                Text(lang)
                                    .font(.system(size: 10, weight: language == lang ? .semibold : .regular))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 3)
                            }
                            .buttonStyle(.plain)
                            .foregroundColor(language == lang ? .white : AppTheme.textSecondary)
                            .background(
                                RoundedRectangle(cornerRadius: 5)
                                    .fill(language == lang ? AppTheme.accent : Color.black.opacity(0.04))
                            )
                        }
                    }
                }

                settingRow("回复风格") {
                    HStack(spacing: 6) {
                        ForEach(styles, id: \.self) { style in
                            Button(action: { replyStyle = style }) {
                                Text(style)
                                    .font(.system(size: 10, weight: replyStyle == style ? .semibold : .regular))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 3)
                            }
                            .buttonStyle(.plain)
                            .foregroundColor(replyStyle == style ? .white : AppTheme.textSecondary)
                            .background(
                                RoundedRectangle(cornerRadius: 5)
                                    .fill(replyStyle == style ? AppTheme.accent : Color.black.opacity(0.04))
                            )
                        }
                    }
                }
            }
        }
    }
}

// MARK: - Permissions Settings

struct PermissionsSettings: View {
    @AppStorage("settings.askFrequency") private var askFrequency = "关键确认"
    @AppStorage("settings.readWriteScope") private var readWriteScope = "指定目录"
    @AppStorage("settings.workDir") private var workDir = "~/Documents/Claude/"
    @AppStorage("settings.noStoreKeys") private var noStoreKeys = true
    @AppStorage("settings.confirmExport") private var confirmExport = true

    let frequencies = ["关键确认", "每步询问", "高度自主"]
    let scopes = ["指定目录", "全局授权"]

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            sectionHeader("权限与安全")

            settingGroup {
                settingRow("询问频率") {
                    Picker("", selection: $askFrequency) {
                        ForEach(frequencies, id: \.self) { Text($0).tag($0) }
                    }
                    .pickerStyle(.radioGroup)
                    .font(.system(size: 10))
                }
            }

            settingGroup {
                settingRow("读写权限") {
                    Picker("", selection: $readWriteScope) {
                        ForEach(scopes, id: \.self) { Text($0).tag($0) }
                    }
                    .pickerStyle(.radioGroup)
                    .font(.system(size: 10))
                }
                if readWriteScope == "指定目录" {
                    HStack(spacing: 4) {
                        TextField("工作目录", text: $workDir)
                            .textFieldStyle(.roundedBorder)
                            .font(.system(size: 10))
                            .frame(width: 200)
                        Button(action: {}) {
                            Image(systemName: "folder")
                                .font(.system(size: 11))
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.top, 4)
                }
            }

            settingGroup {
                ToggleRow(title: "不存储密钥", isOn: $noStoreKeys)
                Divider().opacity(0.5)
                ToggleRow(title: "外发前确认", isOn: $confirmExport)
            }
        }
    }
}

// MARK: - Coding Style

struct CodingStyleSettings: View {
    @AppStorage("settings.alignFirst") private var alignFirst = true
    @AppStorage("settings.simpleFirst") private var simpleFirst = true
    @AppStorage("settings.preciseEdit") private var preciseEdit = true
    @AppStorage("settings.autoReview") private var autoReview = true

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            sectionHeader("编码风格")

            settingGroup {
                ToggleRow(title: "动手前先对齐需求", isOn: $alignFirst)
                Divider().opacity(0.5)
                ToggleRow(title: "简单优先", isOn: $simpleFirst)
                Divider().opacity(0.5)
                ToggleRow(title: "精准修改", isOn: $preciseEdit)
                Divider().opacity(0.5)
                ToggleRow(title: "修改后自动代码审查", isOn: $autoReview)
            }
        }
    }
}

// MARK: - Custom Rules

struct CustomRulesSettings: View {
    @AppStorage("settings.customRules") private var rules = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            sectionHeader("自定义规则")
            Text("自然语言补充全局规则，所有会话生效")
                .font(.system(size: 9))
                .foregroundColor(AppTheme.textTertiary)
            TextEditor(text: $rules)
                .font(.system(size: 11))
                .frame(minHeight: 144)
                .overlay(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(AppTheme.dividerGray, lineWidth: 1)
                )
        }
    }
}

// MARK: - Project Overview

struct ProjectOverviewSettings: View {
    @AppStorage("settings.projectName") private var projectName = "Claude Code Studio"
    @AppStorage("settings.projectDescription") private var description = "macOS 原生 AI 编程助手"
    @State private var dataSources: [String] = ["GitHub", "本地文件"]
    @State private var techStack: [String] = ["SwiftUI", "Swift"]
    @State private var productType = "💻 桌面客户端"
    @State private var deployTarget = "GitHub Releases"
    @AppStorage("settings.projectRules") private var projectRules = ""

    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            sectionHeader("项目概览")

            settingGroup {
                VStack(alignment: .leading, spacing: 6) {
                    Text("项目名称").settingLabel()
                    TextField("", text: $projectName)
                        .textFieldStyle(.roundedBorder)
                        .font(.system(size: 11))
                }
                .padding(.vertical, 2)

                Divider().opacity(0.5)

                VStack(alignment: .leading, spacing: 6) {
                    Text("项目描述").settingLabel()
                    TextField("", text: $description)
                        .textFieldStyle(.roundedBorder)
                        .font(.system(size: 11))
                }
                .padding(.vertical, 2)
            }

            settingGroup {
                tagRow("数据源", items: $dataSources)
                Divider().opacity(0.5)
                tagRow("技术栈", items: $techStack)
                Divider().opacity(0.5)
                settingRow("产物类型") {
                    Text(productType).font(.system(size: 10)).foregroundColor(AppTheme.textPrimary)
                }
                Divider().opacity(0.5)
                settingRow("部署目标") {
                    Text(deployTarget).font(.system(size: 10)).foregroundColor(AppTheme.textPrimary)
                }
            }

            sectionHeader("项目规则")
            Text("仅在本项目内叠加生效的自然语言指令")
                .font(.system(size: 9))
                .foregroundColor(AppTheme.textTertiary)
            TextEditor(text: $projectRules)
                .font(.system(size: 11))
                .frame(minHeight: 100)
                .overlay(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(AppTheme.dividerGray, lineWidth: 1)
                )
        }
    }

    private func tagRow(_ label: String, items: Binding<[String]>) -> some View {
        HStack(alignment: .top) {
            Text(label).settingLabel().frame(width: 58, alignment: .leading)
            HStack(spacing: 4) {
                ForEach(items.wrappedValue, id: \.self) { item in
                    HStack(spacing: 2) {
                        Text(item).font(.system(size: 9))
                        Button(action: {
                            items.wrappedValue.removeAll { $0 == item }
                        }) {
                            Image(systemName: "xmark").font(.system(size: 7))
                        }
                        .buttonStyle(.plain)
                    }
                    .padding(.horizontal, 6).padding(.vertical, 2)
                    .background(RoundedRectangle(cornerRadius: 4).fill(AppTheme.accentBackground))
                    .foregroundColor(AppTheme.accent)
                }
                Button(action: { items.wrappedValue.append("新项目") }) {
                    Text("+ 添加").font(.system(size: 9))
                }
                .buttonStyle(.plain)
                .foregroundColor(AppTheme.accent)
            }
        }
    }
}

// MARK: - Helpers

private func sectionHeader(_ title: String) -> some View {
    Text(title)
        .font(.system(size: 11, weight: .semibold))
        .foregroundColor(AppTheme.textSecondary)
        .textCase(.uppercase)
}

private func settingGroup<Content: View>(@ViewBuilder content: () -> Content) -> some View {
    VStack(alignment: .leading, spacing: 0) {
        content()
    }
    .padding(12)
    .background(
        RoundedRectangle(cornerRadius: 10)
            .fill(Color.white)
            .overlay(
                RoundedRectangle(cornerRadius: 10)
                    .stroke(AppTheme.dividerGray, lineWidth: 1)
            )
    )
}

private func settingRow<Content: View>(_ label: String, @ViewBuilder content: () -> Content) -> some View {
    HStack {
        Text(label).settingLabel()
        Spacer()
        content()
    }
}

private struct ToggleRow: View {
    let title: String
    @Binding var isOn: Bool
    var body: some View {
        HStack {
            Text(title).settingLabel()
            Spacer()
            Toggle("", isOn: $isOn).toggleStyle(.switch)
        }
        .padding(.vertical, 2)
    }
}

private extension Text {
    func settingLabel() -> some View {
        self.font(.system(size: 11))
            .foregroundColor(AppTheme.textPrimary)
    }
}
