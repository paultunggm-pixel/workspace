import SwiftUI

enum AppTheme {
    // Sidebar
    static let sidebarWidth: CGFloat = 300
    static let sidebarBackground = Color(nsColor: .windowBackgroundColor)

    // Cards
    static let cardRadius: CGFloat = 10
    static let cardBorder = Color.black.opacity(0.12)
    static let cardBackground = Color(nsColor: .textBackgroundColor)

    // Spacing
    static let cardMargin: CGFloat = 10
    static let cardPadding: CGFloat = 12
    static let rowPadding: CGFloat = 6
    static let contentMargin: CGFloat = 10

    // Typography
    static let titleSize: CGFloat = 12
    static let bodySize: CGFloat = 11
    static let captionSize: CGFloat = 9

    // Colors
    static let accent = Color.blue
    static let accentBackground = Color.blue.opacity(0.06)
    static let claudeAmber = Color(red: 0.85, green: 0.47, blue: 0.34)
    static let dividerGray = Color.primary.opacity(0.1)
    static let textPrimary = Color.primary
    static let textSecondary = Color.secondary
    static let textTertiary = Color.secondary.opacity(0.7)
}
