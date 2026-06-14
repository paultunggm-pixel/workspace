import SwiftUI

struct SidebarView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        ScrollView {
            VStack(spacing: 10) {
                ModelEngineCard()
                    .padding(.horizontal, 10)
                ProjectListCard()
                    .padding(.horizontal, 10)
            }
            .padding(.top, 10).padding(.bottom, 10)
        }
        .background(Color(nsColor:.windowBackgroundColor).opacity(0.5))
    }
}

struct ProjectListCard: View {
    let cats = ProjectStore.sampleCategories
    let projs = ProjectStore.sampleProjects
    
    var body: some View {
        VStack(alignment:.leading,spacing:0) {
            HStack {
                Text("项目").font(.system(size:10,weight:.semibold)).foregroundColor(.secondary)
                Spacer()
                Text("+ 分类").font(.system(size:10)).foregroundColor(.secondary)
                Text("+ 项目").font(.system(size:10)).foregroundColor(.secondary)
            }.padding(.bottom,8).overlay(Rectangle().frame(height:1).foregroundColor(Color.black.opacity(0.07)),alignment:.bottom)
            
            ForEach(cats) { cat in
                HStack(spacing:6) {
                    Text(cat.icon)
                    Text(cat.name).font(.system(size:11,weight:.semibold))
                    Spacer()
                    Text("\(projs.filter{$0.categoryId==cat.id}.count)").font(.system(size:9)).foregroundColor(.secondary)
                }.padding(.vertical,5)
                
                ForEach(projs.filter{$0.categoryId==cat.id}) { p in
                    HStack(spacing:4) {
                        Text(p.name).font(.system(size:11))
                        Spacer()
                        Text("⋯").font(.system(size:12)).foregroundColor(.secondary)
                    }.padding(.vertical,4).padding(.leading,28)
                }
            }
            Spacer(minLength:20)
        }
        .padding(12)
        .background(RoundedRectangle(cornerRadius:10).fill(Color.white.opacity(0.55)).overlay(RoundedRectangle(cornerRadius:10).stroke(Color.black.opacity(0.07),lineWidth:1)))
    }
}
