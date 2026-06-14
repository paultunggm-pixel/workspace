import SwiftUI

struct ContentArea: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(spacing: 0) {
            // Tab bar
            TabBar(selectedTab: $appState.selectedTab)

            // Tab content area
            ZStack {
                switch appState.selectedTab {
                case .chat:    ChatTabView()
                case .plan:    PlanTabView()
                case .preview: PreviewTabView()
                case .code:    CodeTabView()
                case .publish: PublishTabView()
                case .service: ServiceTabView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(Color.white)
        .clipShape(RoundedRectangle(cornerRadius: AppTheme.cardRadius))
        .padding(.trailing, AppTheme.contentMargin)
        .padding(.bottom, AppTheme.contentMargin)
    }
}

struct DebugTabView: View {
    let label: String
    let color: Color
    var body: some View {
        VStack {
            Text(label)
                .font(.largeTitle)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(color)
    }
}
