import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        VStack(spacing: 0) {
            TitlebarView()

            HStack(spacing: 0) {
                SidebarView()
                    .frame(width: AppTheme.sidebarWidth)

                Rectangle()
                    .fill(AppTheme.dividerGray)
                    .frame(width: 1)

                ContentArea()
                    .frame(maxWidth: .infinity)
            }
            .frame(maxHeight: .infinity)

            StatusBarView()
        }
    }
}
