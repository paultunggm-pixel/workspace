import Foundation

/// Handles HTTP requests to AI provider APIs with streaming support.
/// Supports OpenAI-compatible (DeepSeek/Qwen/custom) and Anthropic native formats.
enum APIService {

    // MARK: - Request Types

    struct ChatRequest: Encodable {
        let model: String
        let messages: [Message]
        let stream: Bool
        let max_tokens: Int

        init(model: String, messages: [Message], stream: Bool = true) {
            self.model = model
            self.messages = messages
            self.stream = stream
            self.max_tokens = 4096
        }
    }

    struct Message: Encodable {
        let role: String
        let content: String
    }

    // MARK: - Anthropic Request Types

    struct AnthropicRequest: Encodable {
        let model: String
        let messages: [AnthropicMessage]
        let maxTokens: Int
        let stream: Bool

        init(model: String, messages: [AnthropicMessage], stream: Bool = true) {
            self.model = model
            self.messages = messages
            self.stream = stream
            self.maxTokens = 4096
        }
    }

    struct AnthropicMessage: Encodable {
        let role: String
        let content: String
    }

    // MARK: - Chunk Types

    struct OpenAIChunk: Decodable {
        let choices: [Choice]?

        struct Choice: Decodable {
            let delta: Delta?
            struct Delta: Decodable { let content: String? }
        }
    }

    struct AnthropicChunk: Decodable {
        let type: String?
        let delta: Delta?
        struct Delta: Decodable { let text: String? }
    }

    // MARK: - Send Message

    /// Send a streaming chat request and receive chunks via callback
    static func sendMessage(
        provider: ProviderConfig,
        apiKey: String,
        model: String,
        messages: [Message],
        onChunk: @escaping (String) -> Void,
        onComplete: @escaping (Result<String, Error>) -> Void
    ) {
        let isAnthropic = provider.type == .anthropic

        guard let url = buildURL(for: provider, isAnthropic: isAnthropic) else {
            onComplete(.failure(APIError.invalidURL))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.timeoutInterval = 120

        // Headers
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if isAnthropic {
            request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
            request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        } else {
            request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        }

        // Body
        do {
            if isAnthropic {
                let antMsgs = messages.map { AnthropicMessage(role: $0.role, content: $0.content) }
                let body = AnthropicRequest(model: model, messages: antMsgs)
                let encoder = JSONEncoder()
                encoder.keyEncodingStrategy = .convertToSnakeCase
                request.httpBody = try encoder.encode(body)
            } else {
                let body = ChatRequest(model: model, messages: messages)
                request.httpBody = try JSONEncoder().encode(body)
            }
        } catch {
            onComplete(.failure(error))
            return
        }

        // Streaming URLSession
        let delegate = StreamingDelegate(onChunk: onChunk, onComplete: onComplete, isAnthropic: isAnthropic)
        let session = URLSession(configuration: .default, delegate: delegate, delegateQueue: nil)
        let task = session.dataTask(with: request)
        task.resume()
    }

    private static func buildURL(for provider: ProviderConfig, isAnthropic: Bool) -> URL? {
        let base = provider.endpoint.trimmingCharacters(in: CharacterSet(charactersIn: "/"))
        if isAnthropic {
            return URL(string: "\(base)/messages")
        } else {
            return URL(string: "\(base)/chat/completions")
        }
    }

    // MARK: - Validation

    /// Quick connection test
    static func testConnection(provider: ProviderConfig, apiKey: String) async throws -> Bool {
        let isAnthropic = provider.type == .anthropic
        guard let url = buildURL(for: provider, isAnthropic: isAnthropic) else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        if isAnthropic {
            request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
            request.setValue("2023-06-01", forHTTPHeaderField: "anthropic-version")
        } else {
            request.setValue("Bearer \(apiKey)", forHTTPHeaderField: "Authorization")
        }
        request.timeoutInterval = 15

        // Send minimal request just to check auth
        if isAnthropic {
            let body = AnthropicRequest(model: "claude-sonnet-4-20250514", messages: [
                AnthropicMessage(role: "user", content: "hi")
            ], stream: false)
            let encoder = JSONEncoder()
            encoder.keyEncodingStrategy = .convertToSnakeCase
            request.httpBody = try encoder.encode(body)
        } else {
            let body = ChatRequest(model: provider.defaultModel.isEmpty ? "gpt-3.5-turbo" : provider.defaultModel, messages: [
                Message(role: "user", content: "hi")
            ], stream: false)
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        if httpResponse.statusCode == 200 { return true }
        if httpResponse.statusCode == 401 { throw APIError.httpError(401, "API Key 无效") }
        // Show error body
        if let body = String(data: data, encoding: .utf8), !body.isEmpty {
            throw APIError.httpError(httpResponse.statusCode, body.prefix(200).description)
        }
        throw APIError.httpError(httpResponse.statusCode, nil)
    }
}

// MARK: - Streaming Delegate

private class StreamingDelegate: NSObject, URLSessionDataDelegate {
    let onChunk: (String) -> Void
    let onComplete: (Result<String, Error>) -> Void
    let isAnthropic: Bool
    private var fullContent = ""
    private var buffer = Data()

    init(onChunk: @escaping (String) -> Void, onComplete: @escaping (Result<String, Error>) -> Void, isAnthropic: Bool) {
        self.onChunk = onChunk
        self.onComplete = onComplete
        self.isAnthropic = isAnthropic
    }

    func urlSession(_ session: URLSession, dataTask: URLSessionDataTask, didReceive data: Data) {
        buffer.append(data)

        // Process complete SSE lines
        while let newlineRange = buffer.range(of: Data("\n".utf8)) {
            let lineData = buffer[..<newlineRange.lowerBound]
            buffer.removeSubrange(..<newlineRange.upperBound)

            guard let line = String(data: lineData, encoding: .utf8)?
                .trimmingCharacters(in: .whitespacesAndNewlines),
                  !line.isEmpty else { continue }

            if line.hasPrefix("data: ") {
                let jsonStr = String(line.dropFirst(6))
                if jsonStr == "[DONE]" { continue }

                if let jsonData = jsonStr.data(using: .utf8) {
                    let text = extractText(from: jsonData, isAnthropic: isAnthropic)
                    if let text = text {
                        fullContent += text
                        DispatchQueue.main.async { self.onChunk(text) }
                    }
                }
            }
        }
    }

    func urlSession(_ session: URLSession, task: URLSessionTask, didCompleteWithError error: Error?) {
        // Process any remaining buffer
        if !buffer.isEmpty, let line = String(data: buffer, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines),
           line.hasPrefix("data: "), line != "data: [DONE]" {
            let jsonStr = String(line.dropFirst(6))
            if let jsonData = jsonStr.data(using: .utf8),
               let text = extractText(from: jsonData, isAnthropic: isAnthropic) {
                fullContent += text
            }
        }

        DispatchQueue.main.async {
            if let error = error {
                self.onComplete(.failure(error))
            } else {
                self.onComplete(.success(self.fullContent))
            }
        }
    }

    private func extractText(from jsonData: Data, isAnthropic: Bool) -> String? {
        if isAnthropic {
            if let chunk = try? JSONDecoder().decode(APIService.AnthropicChunk.self, from: jsonData),
               let text = chunk.delta?.text {
                return text
            }
        } else {
            if let chunk = try? JSONDecoder().decode(APIService.OpenAIChunk.self, from: jsonData),
               let text = chunk.choices?.first?.delta?.content {
                return text
            }
        }
        return nil
    }
}

// MARK: - Errors

enum APIError: LocalizedError {
    case invalidURL
    case invalidResponse
    case keyNotFound
    case httpError(Int, String?)

    var errorDescription: String? {
        switch self {
        case .invalidURL: return "无效的 API 端点"
        case .invalidResponse: return "无效的服务器响应"
        case .keyNotFound: return "未找到 API Key，请在侧栏配置"
        case .httpError(let code, let body): return "HTTP \(code)" + (body.map { ": \($0)" } ?? "")
        }
    }
}
