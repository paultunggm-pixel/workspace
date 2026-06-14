import Foundation

/// The three project types supported for publishing
enum ProjectType: String, CaseIterable, Codable {
    case web = "🌐 Web 产品"
    case mobile = "📱 移动 App"
    case desktop = "💻 桌面客户端"

    var icon: String {
        switch self {
        case .web: return "🌐"
        case .mobile: return "📱"
        case .desktop: return "💻"
        }
    }
}

/// Deployment configuration for a project
struct DeployConfig: Codable, Equatable {
    var projectType: ProjectType
    var buildTarget: BuildTarget
    var distributionChannels: [DistributionChannel]
    var lastBuildDate: Date?
    var lastDeployDate: Date?

    init(
        projectType: ProjectType = .web,
        buildTarget: BuildTarget = .none,
        distributionChannels: [DistributionChannel] = [],
        lastBuildDate: Date? = nil,
        lastDeployDate: Date? = nil
    ) {
        self.projectType = projectType
        self.buildTarget = buildTarget
        self.distributionChannels = distributionChannels
        self.lastBuildDate = lastBuildDate
        self.lastDeployDate = lastDeployDate
    }
}

/// Build targets per project type
enum BuildTarget: String, CaseIterable, Codable {
    case none = "无需构建"
    case staticSite = "静态站点"
    case iosIPA = "iOS .ipa"
    case androidAPK = "Android .apk"
    case androidAAB = "Android .aab"
    case macosDMG = "macOS .dmg"
    case windowsEXE = "Windows .exe"
    case linuxAppImage = "Linux .AppImage"

    static func targets(for type: ProjectType) -> [BuildTarget] {
        switch type {
        case .web: return [.none, .staticSite]
        case .mobile: return [.iosIPA, .androidAPK, .androidAAB]
        case .desktop: return [.macosDMG, .windowsEXE, .linuxAppImage]
        }
    }
}

/// Distribution channels per project type
enum DistributionChannel: String, CaseIterable, Codable {
    case oss = "☁️ OSS"
    case githubPages = "🌐 GitHub Pages"
    case testflight = "🍎 TestFlight"
    case appStore = "📱 App Store"
    case googlePlay = "🤖 Google Play"
    case githubReleases = "🐙 GitHub Releases"
    case macAppStore = "💻 Mac App Store"

    static func channels(for type: ProjectType) -> [DistributionChannel] {
        switch type {
        case .web: return [.oss, .githubPages]
        case .mobile: return [.testflight, .appStore, .googlePlay]
        case .desktop: return [.githubReleases, .macAppStore]
        }
    }
}

/// A deployable artifact file
struct DeployArtifact: Identifiable, Codable, Equatable {
    var id: UUID
    var fileName: String
    var fileSize: Int64
    var type: ProjectType
    var createdAt: Date

    init(id: UUID = UUID(), fileName: String, fileSize: Int64 = 0, type: ProjectType = .web, createdAt: Date = Date()) {
        self.id = id
        self.fileName = fileName
        self.fileSize = fileSize
        self.type = type
        self.createdAt = createdAt
    }

    var sizeFormatted: String {
        if fileSize < 1024 { return "\(fileSize)B" }
        if fileSize < 1048576 { return "\(fileSize / 1024)KB" }
        return String(format: "%.1fMB", Double(fileSize) / 1048576.0)
    }
}

/// A deployment history record
struct DeployRecord: Identifiable, Codable {
    var id: UUID
    var date: Date
    var artifactName: String
    var channels: [DistributionChannel]
    var successChannels: [DistributionChannel]
    var failedChannels: [DistributionChannel]

    init(
        id: UUID = UUID(),
        date: Date = Date(),
        artifactName: String,
        channels: [DistributionChannel] = [],
        successChannels: [DistributionChannel] = [],
        failedChannels: [DistributionChannel] = []
    ) {
        self.id = id
        self.date = date
        self.artifactName = artifactName
        self.channels = channels
        self.successChannels = successChannels
        self.failedChannels = failedChannels
    }

    var isAllSuccess: Bool { failedChannels.isEmpty && !channels.isEmpty }
}
