import SwiftUI

private let sampleArtifacts: [DeployArtifact] = [
    DeployArtifact(fileName: "evaluation_report.html", fileSize: 47104, type: .web),
    DeployArtifact(fileName: "scraping_report.html", fileSize: 22725, type: .web)
]

/// Unified publish tab covering all three project types:
/// Web products / Mobile apps / Desktop clients
/// Two-phase flow: Build -> Distribute
struct PublishTabView: View {
    @EnvironmentObject var appState: AppState
    @State private var config = DeployConfig()
    @State private var artifacts: [DeployArtifact] = sampleArtifacts
    @State private var records: [DeployRecord] = []
    @State private var isBuilding = false
    @State private var isDeploying = false
    @State private var buildProgress = 0.0
    @State private var selectedChannels: Set<DistributionChannel> = [.oss, .githubPages]

    var body: some View {
        VStack(spacing: 0) {
            // Header toolbar
            HStack {
                Text("🚀 发布")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(AppTheme.textPrimary)
                Spacer()
                Picker("项目类型", selection: $config.projectType) {
                    ForEach(ProjectType.allCases, id: \.self) { type in
                        Text(type.rawValue).tag(type)
                    }
                }
                .pickerStyle(.segmented)
                .frame(width: 320)
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 10)
            .background(
                Rectangle()
                    .fill(Color.white)
                    .overlay(
                        Rectangle().frame(height: 1).foregroundColor(AppTheme.dividerGray),
                        alignment: .bottom
                    )
            )

            // Content
            ScrollView {
                VStack(alignment: .leading, spacing: 16) {
                    // Section: Build
                    buildSection

                    Divider().padding(.horizontal, 18)

                    // Section: Distribute
                    distributeSection

                    Divider().padding(.horizontal, 18)

                    // Section: Online URLs
                    onlineURLsSection

                    Divider().padding(.horizontal, 18)

                    // Section: Deploy history
                    historySection

                    if config.projectType != .web {
                        Divider().padding(.horizontal, 18)
                        localInstallSection
                    }
                }
                .padding(.vertical, 16)
            }
            .background(Color.white)
        }
    }

    // MARK: - Build Section

    private var buildSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader("🔨 构建")

            HStack(spacing: 12) {
                ForEach(BuildTarget.targets(for: config.projectType), id: \.self) { target in
                    Button(action: { config.buildTarget = target }) {
                        Text(target.rawValue)
                            .font(.system(size: 10, weight: config.buildTarget == target ? .semibold : .regular))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(config.buildTarget == target ? .white : AppTheme.textSecondary)
                    .background(
                        RoundedRectangle(cornerRadius: 6)
                            .fill(config.buildTarget == target ? AppTheme.accent : Color.black.opacity(0.04))
                    )
                }
            }

            if isBuilding {
                VStack(spacing: 6) {
                    ProgressView(value: buildProgress)
                        .progressViewStyle(.linear)
                    Text("正在构建... \(Int(buildProgress * 100))%")
                        .font(.system(size: 9))
                        .foregroundColor(AppTheme.textTertiary)
                }
            } else {
                HStack {
                    Button(action: simulateBuild) {
                        Label("构建", systemImage: "hammer")
                            .font(.system(size: 11))
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(AppTheme.accent)

                    if config.buildTarget != .none {
                        Text(buildTestText)
                            .font(.system(size: 9))
                            .foregroundColor(AppTheme.textSecondary)
                            .padding(.leading, 8)

                        if config.projectType != .web {
                            Button(action: { simulateBuild() }) {
                                Text(localTestLabel)
                                    .font(.system(size: 9))
                            }
                            .buttonStyle(.plain)
                            .foregroundColor(AppTheme.accent)
                        }
                    }
                }
            }
        }
        .padding(.horizontal, 18)
    }

    // MARK: - Distribute Section

    private var distributeSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader("📤 分发")

            HStack(spacing: 8) {
                ForEach(DistributionChannel.channels(for: config.projectType), id: \.self) { channel in
                    Button(action: {
                        if selectedChannels.contains(channel) {
                            selectedChannels.remove(channel)
                        } else {
                            selectedChannels.insert(channel)
                        }
                    }) {
                        Text(channel.rawValue)
                            .font(.system(size: 10, weight: selectedChannels.contains(channel) ? .semibold : .regular))
                            .padding(.horizontal, 10)
                            .padding(.vertical, 5)
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(selectedChannels.contains(channel) ? .white : AppTheme.textSecondary)
                    .background(
                        RoundedRectangle(cornerRadius: 6)
                            .fill(selectedChannels.contains(channel) ? Color.green : Color.black.opacity(0.04))
                    )
                }
            }

            // Deploy button
            HStack(spacing: 12) {
                Button(action: simulateDeploy) {
                    Label("一键发布", systemImage: "rocket")
                        .font(.system(size: 11, weight: .semibold))
                }
                .buttonStyle(.plain)
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(selectedChannels.isEmpty ? Color.gray : AppTheme.accent)
                )
                .disabled(selectedChannels.isEmpty || isDeploying)

                if isDeploying {
                    ProgressView().scaleEffect(0.6)
                    Text("发布中...")
                        .font(.system(size: 9))
                        .foregroundColor(AppTheme.textTertiary)
                }
            }
        }
        .padding(.horizontal, 18)
    }

    // MARK: - Online URLs

    private var onlineURLsSection: some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionHeader("🌐 线上地址")

            if !records.isEmpty, let latest = records.last {
                ForEach(latest.channels, id: \.self) { channel in
                    HStack(spacing: 6) {
                        Circle()
                            .fill(latest.successChannels.contains(channel) ? Color.green : Color.red)
                            .frame(width: 6, height: 6)
                        Text(channel.rawValue)
                            .font(.system(size: 10))
                            .foregroundColor(AppTheme.textSecondary)
                        Text("→ https://example.com/app")
                            .font(.system(size: 9))
                            .foregroundColor(AppTheme.accent)
                            .lineLimit(1)
                        Spacer()
                        Button(action: {}) {
                            Image(systemName: "doc.on.doc")
                                .font(.system(size: 9))
                        }
                        .buttonStyle(.plain)
                        .foregroundColor(AppTheme.textTertiary)
                    }
                }
            } else {
                Text("尚未发布 · 发布后将在此显示线上地址")
                    .font(.system(size: 9))
                    .foregroundColor(AppTheme.textTertiary)
            }
        }
        .padding(.horizontal, 18)
    }

    // MARK: - History

    private var historySection: some View {
        VStack(alignment: .leading, spacing: 8) {
            sectionHeader("📜 发布记录")

            if records.isEmpty {
                Text("暂无发布记录")
                    .font(.system(size: 9))
                    .foregroundColor(AppTheme.textTertiary)
            } else {
                ForEach(records) { record in
                    HStack(spacing: 6) {
                        Text("● \(record.date, style: .date) \(record.date, style: .time)")
                            .font(.system(size: 9))
                            .foregroundColor(AppTheme.textSecondary)
                        Text(record.artifactName)
                            .font(.system(size: 9))
                            .foregroundColor(AppTheme.textPrimary)
                        Spacer()
                        ForEach(record.successChannels, id: \.self) { _ in Text("✅").font(.system(size: 9)) }
                        ForEach(record.failedChannels, id: \.self) { _ in Text("❌").font(.system(size: 9)) }
                    }
                }
            }
        }
        .padding(.horizontal, 18)
    }

    // MARK: - Local Install (non-web only)

    private var localInstallSection: some View {
        VStack(alignment: .leading, spacing: 10) {
            sectionHeader(localInstallTitle)

            HStack(spacing: 12) {
                Button(action: simulateBuild) {
                    Label(localInstallLabel, systemImage: "arrow.down.app")
                        .font(.system(size: 11))
                }
                .buttonStyle(.plain)
                .foregroundColor(AppTheme.accent)

                if isBuilding {
                    ProgressView().scaleEffect(0.6)
                } else if config.lastBuildDate != nil {
                    Text("✅ 已安装")
                        .font(.system(size: 9))
                        .foregroundColor(.green)
                    Button(action: {}) {
                        Text("启动应用")
                            .font(.system(size: 9))
                    }
                    .buttonStyle(.plain)
                    .foregroundColor(AppTheme.accent)
                }
            }

            Text(localInstallSteps)
                .font(.system(size: 9))
                .foregroundColor(AppTheme.textTertiary)
        }
        .padding(.horizontal, 18)
    }

    // MARK: - Helpers

    private func sectionHeader(_ text: String) -> some View {
        Text(text)
            .font(.system(size: 11, weight: .semibold))
            .foregroundColor(AppTheme.textSecondary)
    }

    private var buildTestText: String {
        switch config.projectType {
        case .web: return "🔗 浏览器打开"
        case .mobile: return "📥 安装到本地手机"
        case .desktop: return "📥 本地安装运行"
        }
    }

    private var localTestLabel: String {
        config.projectType == .mobile ? "生成二维码安装" : "本地安装"
    }

    private var localInstallTitle: String {
        config.projectType == .mobile ? "📱 本地安装" : "💻 本地安装"
    }

    private var localInstallLabel: String {
        config.projectType == .mobile ? "安装到手机" : "安装运行"
    }

    private var localInstallSteps: String {
        switch config.projectType {
        case .mobile:
            return "① 点击按钮 → ② 构建 IPA/APK → ③ 生成二维码 → ④ 手机扫码安装"
        case .desktop:
            return "① 点击按钮 → ② 检测构建(版本不变则重用) → ③ .dmg 挂载拖拽 → ④ 已安装"
        case .web:
            return ""
        }
    }

    // MARK: - Simulated actions

    private func simulateBuild() {
        isBuilding = true
        buildProgress = 0
        Timer.scheduledTimer(withTimeInterval: 0.03, repeats: true) { t in
            buildProgress += 0.04
            if buildProgress >= 1.0 {
                buildProgress = 1.0
                t.invalidate()
                isBuilding = false
                config.lastBuildDate = Date()
                let name = config.projectType == .web ? "app-v1.0.\(artifacts.count).html" :
                           config.projectType == .mobile ? "app-v1.0.\(artifacts.count).ipa" : "app-v1.0.\(artifacts.count).dmg"
                artifacts.append(DeployArtifact(fileName: name, fileSize: Int64.random(in: 10000...5000000), type: config.projectType))
            }
        }
    }

    private func simulateDeploy() {
        isDeploying = true
        let channels = Array(selectedChannels)
        let success = channels  // Simulate all success
        let record = DeployRecord(
            artifactName: artifacts.last?.fileName ?? "app-v1.0.0",
            channels: channels,
            successChannels: success,
            failedChannels: []
        )
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
            records.append(record)
            isDeploying = false
            config.lastDeployDate = Date()
        }
    }
}
