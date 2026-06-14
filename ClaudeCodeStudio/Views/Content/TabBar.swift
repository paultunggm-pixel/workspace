import SwiftUI

struct TabBar: View {
    @Binding var selectedTab: ContentTab

    var body: some View {
        HStack(spacing: 0) {
            ForEach(ContentTab.allCases, id: \.self) { tab in
                Button(action: { selectedTab = tab }) {
                    Text(tabIcon(for: tab) + " " + tab.rawValue)
                        .font(.system(size: 11, weight: selectedTab == tab ? .semibold : .regular))
                        .padding(.horizontal, 13)
                        .padding(.vertical, 7)
                }
                .buttonStyle(.plain)
                .foregroundColor(selectedTab == tab ? AppTheme.accent : AppTheme.textSecondary)
                .background(alignment: .bottom) {
                    if selectedTab == tab {
                        Rectangle()
                            .fill(AppTheme.accent)
                            .frame(height: 2)
                    }
                }
            }

            Spacer()
        }
        .padding(.horizontal, 18)
        .padding(.top, 10)
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
    }

    func tabIcon(for tab: ContentTab) -> String {
        switch tab {
        case .chat: return "💬"
        case .plan: return "📋"
        case .preview: return "🎨"
        case .code: return "📝"
        case .publish: return "🚀"
        case .service: return "🔌"
        }
    }
}
