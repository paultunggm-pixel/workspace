// swift-tools-version:5.10
import PackageDescription
let package = Package(name:"ClaudeCodeStudio", platforms:[.macOS(.v13)], products:[.executable(name:"ClaudeCodeStudio",targets:["ClaudeCodeStudio"])], targets:[.executableTarget(name:"ClaudeCodeStudio",path:".")])
