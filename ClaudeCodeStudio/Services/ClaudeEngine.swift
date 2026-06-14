import Foundation

/// Manages the Claude Code CLI process lifecycle.
/// Communicates via stdin/stdout pipes for prompt/response.
@MainActor
class ClaudeEngine: ObservableObject {
    @Published var isRunning = false
    @Published var output = ""
    
    private var process: Process?
    private var stdinPipe: Pipe?
    private var stdoutPipe: Pipe?
    private var outputBuffer = ""
    
    func start() throws {
        guard !isRunning else { return }
        
        let proc = Process()
        proc.executableURL = URL(fileURLWithPath: "/opt/homebrew/bin/claude")
        proc.arguments = [] // Interactive mode
        proc.environment = ProcessInfo.processInfo.environment
        
        let inPipe = Pipe()
        let outPipe = Pipe()
        proc.standardInput = inPipe
        proc.standardOutput = outPipe
        proc.standardError = outPipe
        
        // Read output asynchronously
        outPipe.fileHandleForReading.readabilityHandler = { [weak self] handle in
            let data = handle.availableData
            guard !data.isEmpty, let self = self else { return }
            if let str = String(data: data, encoding: .utf8) {
                Task { @MainActor in
                    self.outputBuffer += str
                    self.output = self.outputBuffer
                }
            }
        }
        
        try proc.run()
        self.process = proc
        self.stdinPipe = inPipe
        self.stdoutPipe = outPipe
        self.isRunning = true
    }
    
    func send(_ prompt: String) {
        guard let pipe = stdinPipe, !prompt.isEmpty else { return }
        let data = (prompt + "\n").data(using: .utf8)!
        pipe.fileHandleForWriting.write(data)
    }
    
    func stop() {
        process?.terminate()
        process = nil
        isRunning = false
    }
}
