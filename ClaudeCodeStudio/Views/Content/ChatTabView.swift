import SwiftUI
struct ChatTabView: View {
    @State private var input = ""
    @State private var messages: [ChatMsg] = [ChatMsg(role: .assistant, content: "你好，我是 Claude Code。有什么可以帮助你的？")]
    @StateObject private var engine = ChatEngine()
    
    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 14) {
                        ForEach(messages) { msg in
                            HStack(alignment: .top, spacing: 8) {
                                if msg.role == .assistant {
                                    Circle().fill(Color(red:0.85,green:0.47,blue:0.34)).frame(width: 24, height: 24).overlay(Text("C").font(.system(size:10,weight:.bold)).foregroundColor(.white))
                                }
                                VStack(alignment: .leading, spacing: 3) {
                                    Text(msg.role == .assistant ? "Claude Code" : "我").font(.system(size: 10, weight: .semibold)).foregroundColor(.secondary)
                                    Text(msg.content).font(.system(size: 12)).padding(10).background(msg.role == .assistant ? Color(.controlBackgroundColor) : Color.blue.opacity(0.1)).clipShape(RoundedRectangle(cornerRadius: 8))
                                }
                                if msg.role == .user {
                                    Circle().fill(LinearGradient(colors:[.purple,.blue],startPoint:.topLeading,endPoint:.bottomTrailing)).frame(width: 24, height: 24).overlay(Text("P").font(.system(size:10,weight:.semibold)).foregroundColor(.white))
                                }
                            }.frame(maxWidth: .infinity, alignment: msg.role == .user ? .trailing : .leading)
                        }
                    }.padding(16)
                }
            }
            
            // Quick actions
            HStack(spacing: 6) {
                Button("📜 CLAUDE.md") {}.buttonStyle(.plain).font(.system(size: 9)).padding(.horizontal, 10).padding(.vertical, 4).background(RoundedRectangle(cornerRadius: 6).stroke(Color.black.opacity(0.1))).foregroundColor(.secondary)
                Button("📋 Skills") {}.buttonStyle(.plain).font(.system(size: 9)).padding(.horizontal, 10).padding(.vertical, 4).background(RoundedRectangle(cornerRadius: 6).stroke(Color.black.opacity(0.1))).foregroundColor(.secondary)
                Button("🗜 压缩") {}.buttonStyle(.plain).font(.system(size: 9)).padding(.horizontal, 10).padding(.vertical, 4).background(RoundedRectangle(cornerRadius: 6).stroke(Color.black.opacity(0.1))).foregroundColor(.secondary)
            }.padding(.horizontal, 16).padding(.top, 4)
            
            // Input row
            HStack(spacing: 6) {
                Button(action:{}) { Image(systemName:"paperclip").font(.system(size:12)) }.buttonStyle(.plain).foregroundColor(.secondary)
                TextField("输入消息...", text: $input).textFieldStyle(.plain).font(.system(size: 12))
                    .onSubmit { sendMsg() }
                Button(action:{}) { Image(systemName:"magnifyingglass").font(.system(size:12)) }.buttonStyle(.plain).foregroundColor(.secondary)
                Button(action:{ sendMsg() }) { Image(systemName:"arrow.up.circle.fill").font(.system(size: 22)) }.buttonStyle(.plain).foregroundColor(.blue)
            }.padding(8).background(Color(.controlBackgroundColor)).clipShape(RoundedRectangle(cornerRadius: 8)).padding(.horizontal, 14).padding(.vertical, 8)
        }
    }
    
    func sendMsg() {
        guard !input.trimmingCharacters(in: .whitespaces).isEmpty else { return }
        let msg = ChatMsg(role: .user, content: input)
        messages.append(msg)
        input = ""
        engine.send(msg.content) { reply in
            messages.append(ChatMsg(role: .assistant, content: reply))
        }
    }
}

struct ChatMsg: Identifiable { var id = UUID(); var role: MsgRole; var content: String }
enum MsgRole { case user, assistant }

class ChatEngine: ObservableObject {
    func send(_ prompt: String, completion: @escaping (String) -> Void) {
        DispatchQueue.global().async {
            let proc = Process()
            proc.executableURL = URL(fileURLWithPath: "/opt/homebrew/bin/claude")
            proc.arguments = ["-p", prompt, "--output-format", "text"]
            let outPipe = Pipe()
            proc.standardOutput = outPipe
            try? proc.run()
            proc.waitUntilExit()
            let data = outPipe.fileHandleForReading.readDataToEndOfFile()
            let result = String(data: data, encoding: .utf8) ?? "无响应"
            DispatchQueue.main.async { completion(result.trimmingCharacters(in: .whitespacesAndNewlines)) }
        }
    }
}
