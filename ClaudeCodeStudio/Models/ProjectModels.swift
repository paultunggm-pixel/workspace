import Foundation
struct ProjectCategory: Identifiable, Codable { var id=UUID(); var name:String; var icon:String; var isExpanded=true }
struct Project: Identifiable, Codable { var id=UUID(); var name:String; var categoryId:UUID; var description:String=""; var techStack:[String]=[]; var dataSources:[String]=[]; var artifactTypes:[String]=[]; var deployTargets:[String]=[]; var ruleOverrides:String=""; var createdAt=Date() }
struct ProjectStore {
    static let sampleCategories: [ProjectCategory] = [
        ProjectCategory(name:"数据分析", icon:"📂"),
        ProjectCategory(name:"产品开发", icon:"📁", isExpanded:false),
        ProjectCategory(name:"未分类", icon:"📁", isExpanded:false)
    ]
    static let sampleProjects: [Project] = [
        Project(name:"2026世界杯", categoryId: sampleCategories[0].id),
        Project(name:"解题一致性评测", categoryId: sampleCategories[0].id),
        Project(name:"Claude Code Studio", categoryId: sampleCategories[1].id),
        Project(name:"封面工具", categoryId: sampleCategories[1].id)
    ]
}
