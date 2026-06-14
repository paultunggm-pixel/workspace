import SwiftUI

private let sampleServices: [ServiceConfig] = [
    ServiceConfig(name: "GitHub", category: .devTools, description: "代码仓库与 CI/CD", status: .connected, endpoint: "api.github.com", dailyCalls: 47, tools: ["repo", "pr", "issues", "actions", "gist"]),
    ServiceConfig(name: "阿里云 OSS", category: .dataStorage, description: "对象存储与 CDN", status: .connected, endpoint: "oss-cn-hangzhou.aliyuncs.com", dailyCalls: 12, tools: ["upload", "list", "delete"]),
    ServiceConfig(name: "DeepSeek", category: .aiSearch, description: "AI 推理模型", status: .connected, endpoint: "api.deepseek.com", dailyCalls: 156, tools: ["chat", "completion", "models"]),
    ServiceConfig(name: "Firecrawl", category: .aiSearch, description: "网站爬取与提取", status: .error, endpoint: "api.firecrawl.dev", dailyCalls: 3, tools: ["scrape", "crawl", "map"]),
    ServiceConfig(name: "Runway", category: .contentMedia, description: "AI 视频/图像生成", status: .pendingAuth, dailyCalls: 0, tools: ["generate-video", "generate-image"]),
]

/// Service management tab — unified MCP & non-MCP service connections.
/// Summary bar + expandable service list + add-service catalog.
struct ServiceTabView: View {
    @EnvironmentObject var providerManager: ProviderManager
    @State private var services: [ServiceConfig] = []
    @State private var expandedServiceId: UUID? = nil
    @State private var showCatalog = false

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("🔌 服务").font(.system(size: 12, weight: .semibold)).foregroundColor(AppTheme.textPrimary)
                Spacer()
                Button(action: { showCatalog = true }) {
                    Label("添加服务", systemImage: "plus.circle").font(.system(size: 10))
                }
                .buttonStyle(.plain).foregroundColor(AppTheme.accent)
            }
            .padding(.horizontal, 18).padding(.vertical, 10)
            .background(Color.white.overlay(
                Rectangle().frame(height: 1).foregroundColor(AppTheme.dividerGray), alignment: .bottom))

            summaryBar

            ScrollView {
                LazyVStack(spacing: 2) {
                    ForEach(services) { service in
                        ServiceRowView(
                            service: service,
                            isExpanded: expandedServiceId == service.id,
                            onToggle: {
                                withAnimation(.easeInOut(duration: 0.15)) {
                                    expandedServiceId = expandedServiceId == service.id ? nil : service.id
                                }
                            },
                            onDisconnect: {
                                if let idx = services.firstIndex(where: { $0.id == service.id }) {
                                    services[idx].status = .disconnected
                                }
                                // Also disconnect matching provider
                                if let pid = providerManager.store.providers.first(where: { service.name.contains($0.label) || $0.label.contains(service.name) })?.id {
                                    providerManager.updateConnectionStatus(providerId: pid, status: .disconnected)
                                }
                            }
                        )
                    }
                }
                .padding(.vertical, 8)
            }
            .background(Color.white)
        }
        .sheet(isPresented: $showCatalog) {
            ServiceCatalogView(services: $services)
        }
        .onAppear { syncFromProviders() }
    }

    private func syncFromProviders() {
        var merged = sampleServices
        for p in providerManager.store.providers {
            let svc = ServiceConfig(
                name: p.label,
                category: .aiSearch,
                description: p.type.rawValue + " · " + p.defaultModel,
                status: p.connectionStatus == .connected ? .connected :
                        p.connectionStatus == .error ? .error : .disconnected,
                endpoint: p.endpoint,
                dailyCalls: 0,
                tools: p.models
            )
            if !merged.contains(where: { $0.name == svc.name }) {
                merged.append(svc)
            }
        }
        services = merged
    }

    private var summaryBar: some View {
        let connected = services.filter { $0.status == .connected }.count
        let errors = services.filter { $0.status == .error || $0.status == .rateLimited }.count
        return HStack(spacing: 16) {
            Text("共 \(services.count) 项").font(.system(size: 9)).foregroundColor(AppTheme.textSecondary)
            Text("\(connected) 正常").font(.system(size: 9)).foregroundColor(.green)
            if errors > 0 { Text("\(errors) 异常").font(.system(size: 9)).foregroundColor(.red) }
            Spacer()
        }
        .padding(.horizontal, 18).padding(.vertical, 6).background(Color(white: 0.98))
    }
}

// MARK: - Service Row

struct ServiceRowView: View {
    let service: ServiceConfig
    let isExpanded: Bool
    let onToggle: () -> Void
    let onDisconnect: () -> Void

    var body: some View {
        VStack(spacing: 0) {
            HStack(spacing: 8) {
                Text(service.statusColor)
                    .font(.system(size: 10))
                Text(service.name)
                    .font(.system(size: 11, weight: .medium))
                    .foregroundColor(AppTheme.textPrimary)
                Text(service.description)
                    .font(.system(size: 9))
                    .foregroundColor(AppTheme.textTertiary)
                    .lineLimit(1)
                Spacer()
                Text("今日 \(service.dailyCalls)次")
                    .font(.system(size: 9))
                    .foregroundColor(AppTheme.textTertiary)
                Text(service.status.rawValue)
                    .font(.system(size: 9, weight: .medium))
                    .foregroundColor(statusColor)
                Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                    .font(.system(size: 8))
                    .foregroundColor(AppTheme.textTertiary)
            }
            .padding(.horizontal, 18)
            .padding(.vertical, 8)

            if isExpanded {
                VStack(spacing: 0) {
                    Divider().padding(.horizontal, 18)
                    HStack(alignment: .top, spacing: 20) {
                        VStack(alignment: .leading, spacing: 4) {
                            detailRow("端点", service.endpoint)
                            detailRow("认证", service.authMethod.rawValue)
                            detailRow("用量", "今日 \(service.dailyCalls) 次调用")
                        }
                        Spacer()
                        VStack(alignment: .trailing, spacing: 6) {
                            if !service.tools.isEmpty {
                                HStack(spacing: 4) {
                                    ForEach(service.tools.prefix(5), id: \.self) { tool in
                                        Text(tool)
                                            .font(.system(size: 8))
                                            .padding(.horizontal, 5).padding(.vertical, 2)
                                            .background(RoundedRectangle(cornerRadius: 3).fill(AppTheme.accentBackground))
                                            .foregroundColor(AppTheme.accent)
                                    }
                                }
                            }
                            HStack(spacing: 8) {
                                Button("重连") {}.buttonStyle(.plain).foregroundColor(AppTheme.accent).font(.system(size: 9))
                                Button("日志") {}.buttonStyle(.plain).foregroundColor(AppTheme.textSecondary).font(.system(size: 9))
                                Button("断开") { onDisconnect() }.buttonStyle(.plain).foregroundColor(.red).font(.system(size: 9))
                            }
                        }
                    }
                    .padding(14)
                    .font(.system(size: 9))
                }
                .background(Color(white: 0.98))
            }
        }
        .background(Color.white)
        .contentShape(Rectangle())
        .onTapGesture { onToggle() }
    }

    private func detailRow(_ label: String, _ value: String) -> some View {
        HStack(spacing: 4) {
            Text(label + ":").foregroundColor(AppTheme.textTertiary)
            Text(value.isEmpty ? "—" : value).foregroundColor(AppTheme.textPrimary)
        }.font(.system(size: 9))
    }

    private var statusColor: Color {
        switch service.status {
        case .connected: return .green
        case .disconnected: return AppTheme.textTertiary
        case .error: return .red
        case .rateLimited: return .yellow
        case .pendingAuth: return .orange
        }
    }
}

struct ServiceCatalogView: View {
    @Binding var services: [ServiceConfig]
    @Environment(\.dismiss) private var dismiss
    var body: some View {
        VStack(spacing: 0) {
            HStack { Text("添加服务").font(.headline); Spacer(); Button("完成") { dismiss() } }.padding()
            ScrollView {
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(ServiceCategory.allCases, id: \.self) { category in
                        VStack(alignment: .leading, spacing: 4) {
                            Text(category.rawValue).font(.system(size: 11, weight: .semibold)).foregroundColor(AppTheme.textSecondary).padding(.horizontal, 18)
                            ForEach(category.defaultServices, id: \.self) { name in
                                Button(action: {
                                    if !services.contains(where: { $0.name == name }) {
                                        services.append(ServiceConfig(name: name, category: category, description: "\(category.icon) \(category.rawValue)", status: .pendingAuth))
                                    }
                                }) {
                                    HStack {
                                        Text(name).font(.system(size: 11)).foregroundColor(AppTheme.textPrimary)
                                        Spacer()
                                        if services.contains(where: { $0.name == name }) {
                                            Text("✓ 已安装").font(.system(size: 9)).foregroundColor(.green)
                                        } else {
                                            Image(systemName: "plus.circle").font(.system(size: 10)).foregroundColor(AppTheme.accent)
                                        }
                                    }.padding(.horizontal, 18).padding(.vertical, 6)
                                }.buttonStyle(.plain)
                            }
                        }
                        Divider().padding(.horizontal, 18)
                    }
                }.padding(.vertical, 8)
            }
        }.frame(width: 360, height: 560)
    }
}