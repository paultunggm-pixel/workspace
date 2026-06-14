import SwiftUI

struct ModelEngineCard: View {
    @EnvironmentObject var appState: AppState
    @State private var showDropdown = false
    
    var body: some View {
        VStack(spacing: 0) {
            Text("模型引擎").font(.system(size: 10, weight: .semibold)).foregroundColor(.secondary)
            Text("DeepSeek v4-pro").font(.system(size: 12, weight: .semibold)).padding(.vertical, 4)
            Divider().padding(.vertical, 4)
            Text("余额 ¥18.42").font(.system(size: 16, weight: .bold))
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius: 10).fill(Color.white.opacity(0.55)).overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.black.opacity(0.07), lineWidth: 1)))
    }
}
