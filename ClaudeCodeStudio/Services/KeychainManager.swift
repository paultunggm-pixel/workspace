import Foundation
import Security

/// macOS Keychain wrapper for secure API key storage.
/// Keys are stored with service="com.claudecodestudio" and account="{providerId}".
enum KeychainManager {

    private static let service = "com.claudecodestudio"

    // MARK: - CRUD

    static func save(key: String, for providerId: String) throws {
        // Delete existing item first to avoid duplicates
        try? delete(for: providerId)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: providerId,
            kSecValueData as String: Data(key.utf8),
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlocked
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else {
            throw KeychainError.unableToSave(status: status)
        }
    }

    static func read(for providerId: String) throws -> String {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: providerId,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var item: CFTypeRef?
        let status = SecItemCopyMatching(query as CFDictionary, &item)

        guard status == errSecSuccess,
              let data = item as? Data,
              let key = String(data: data, encoding: .utf8)
        else {
            throw KeychainError.unableToRead(status: status)
        }

        return key
    }

    static func delete(for providerId: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: providerId
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unableToDelete(status: status)
        }
    }

    /// Check if a key exists without reading it
    static func exists(for providerId: String) -> Bool {
        (try? read(for: providerId)) != nil
    }
}

enum KeychainError: LocalizedError {
    case unableToSave(status: OSStatus)
    case unableToRead(status: OSStatus)
    case unableToDelete(status: OSStatus)

    var errorDescription: String? {
        switch self {
        case .unableToSave(let s): return "Keychain save failed (OSStatus: \(s))"
        case .unableToRead(let s): return "Keychain read failed (OSStatus: \(s))"
        case .unableToDelete(let s): return "Keychain delete failed (OSStatus: \(s))"
        }
    }
}
