# Networking & Data Persistence Reference

## Table of Contents
1. Networking with URLSession
2. API Client Pattern
3. Core Data
4. SwiftData
5. UserDefaults & Keychain
6. Caching Strategies

---

## 1. Networking with URLSession

### Modern async/await Networking

```swift
// Simple request
let (data, response) = try await URLSession.shared.data(from: url)
guard let httpResponse = response as? HTTPURLResponse,
      200..<300 ~= httpResponse.statusCode else {
    throw AppError.serverError(statusCode: (response as? HTTPURLResponse)?.statusCode ?? 0)
}
let decoded = try JSONDecoder().decode(User.self, from: data)
```

### Endpoint Pattern

```swift
enum Endpoint {
    case users
    case user(id: String)
    case createUser(CreateUserRequest)
    case updateUser(id: String, UpdateUserRequest)
    case deleteUser(id: String)
    case login(LoginRequest)
    case uploadImage(Data)
    
    var path: String {
        switch self {
        case .users: "/api/v1/users"
        case .user(let id): "/api/v1/users/\(id)"
        case .createUser: "/api/v1/users"
        case .updateUser(let id, _): "/api/v1/users/\(id)"
        case .deleteUser(let id): "/api/v1/users/\(id)"
        case .login: "/api/v1/auth/login"
        case .uploadImage: "/api/v1/upload"
        }
    }
    
    var method: String {
        switch self {
        case .users, .user: "GET"
        case .createUser, .login, .uploadImage: "POST"
        case .updateUser: "PUT"
        case .deleteUser: "DELETE"
        }
    }
    
    var body: Data? {
        switch self {
        case .createUser(let request): try? JSONEncoder().encode(request)
        case .updateUser(_, let request): try? JSONEncoder().encode(request)
        case .login(let request): try? JSONEncoder().encode(request)
        case .uploadImage(let data): data
        default: nil
        }
    }
    
    var headers: [String: String] {
        var h = ["Content-Type": "application/json", "Accept": "application/json"]
        if case .uploadImage = self { h["Content-Type"] = "multipart/form-data" }
        return h
    }
}
```

---

## 2. API Client Pattern

```swift
actor APIClient {
    private let baseURL: URL
    private let session: URLSession
    private let decoder: JSONDecoder
    private var authToken: String?
    
    init(baseURL: URL, session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
        self.decoder = JSONDecoder()
        self.decoder.dateDecodingStrategy = .iso8601
        self.decoder.keyDecodingStrategy = .convertFromSnakeCase
    }
    
    func setAuthToken(_ token: String?) { self.authToken = token }
    
    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let request = try buildRequest(for: endpoint)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AppError.networkFailure(underlying: URLError(.badServerResponse))
        }
        
        switch httpResponse.statusCode {
        case 200..<300:
            do {
                return try decoder.decode(T.self, from: data)
            } catch {
                throw AppError.decodingFailure
            }
        case 401:
            throw AppError.unauthorized
        case 404:
            throw AppError.notFound
        default:
            throw AppError.serverError(statusCode: httpResponse.statusCode)
        }
    }
    
    func requestVoid(_ endpoint: Endpoint) async throws {
        let request = try buildRequest(for: endpoint)
        let (_, response) = try await session.data(for: request)
        guard let httpResponse = response as? HTTPURLResponse,
              200..<300 ~= httpResponse.statusCode else {
            throw AppError.serverError(statusCode: (response as? HTTPURLResponse)?.statusCode ?? 0)
        }
    }
    
    private func buildRequest(for endpoint: Endpoint) throws -> URLRequest {
        guard let url = URL(string: endpoint.path, relativeTo: baseURL) else {
            throw AppError.networkFailure(underlying: URLError(.badURL))
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method
        request.httpBody = endpoint.body
        
        for (key, value) in endpoint.headers {
            request.setValue(value, forHTTPHeaderField: key)
        }
        
        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        return request
    }
}
```

### Retry & Timeout
```swift
extension APIClient {
    func requestWithRetry<T: Decodable>(_ endpoint: Endpoint, maxRetries: Int = 3) async throws -> T {
        var lastError: Error?
        for attempt in 0..<maxRetries {
            do {
                return try await request(endpoint)
            } catch {
                lastError = error
                if case AppError.unauthorized = error { throw error } // Don't retry auth failures
                if attempt < maxRetries - 1 {
                    try await Task.sleep(for: .seconds(pow(2.0, Double(attempt)))) // Exponential backoff
                }
            }
        }
        throw lastError!
    }
}
```

### Pagination
```swift
struct PaginatedResponse<T: Decodable>: Decodable {
    let items: [T]
    let nextCursor: String?
    let hasMore: Bool
}

@Observable @MainActor
final class PaginatedListViewModel<T: Decodable & Identifiable> {
    private(set) var items: [T] = []
    private(set) var isLoading = false
    private(set) var hasMore = true
    private var nextCursor: String?
    
    func loadNextPage() async {
        guard !isLoading, hasMore else { return }
        isLoading = true
        defer { isLoading = false }
        // Load page, append items, update cursor
    }
}
```

---

## 3. Core Data

### Stack Setup
```swift
final class CoreDataStack {
    static let shared = CoreDataStack()
    
    let container: NSPersistentContainer
    
    var viewContext: NSManagedObjectContext { container.viewContext }
    
    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "MyApp")
        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }
        container.loadPersistentStores { _, error in
            if let error { fatalError("Core Data failed: \(error)") }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }
    
    func newBackgroundContext() -> NSManagedObjectContext {
        let context = container.newBackgroundContext()
        context.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        return context
    }
    
    func save() throws {
        guard viewContext.hasChanges else { return }
        try viewContext.save()
    }
}
```

### SwiftUI Integration
```swift
struct TaskListView: View {
    @FetchRequest(
        sortDescriptors: [SortDescriptor(\.createdAt, order: .reverse)],
        predicate: NSPredicate(format: "isCompleted == NO")
    )
    private var tasks: FetchedResults<TaskEntity>
    
    @Environment(\.managedObjectContext) private var context
    
    var body: some View {
        List(tasks) { task in
            Text(task.title ?? "")
        }
    }
}
```

---

## 4. SwiftData (iOS 17+)

### Model Definition
```swift
import SwiftData

@Model
final class Task {
    var title: String
    var notes: String
    var isCompleted: Bool
    var dueDate: Date?
    var createdAt: Date
    
    @Relationship(deleteRule: .cascade)
    var subtasks: [Subtask]
    
    @Relationship(inverse: \Category.tasks)
    var category: Category?
    
    init(title: String, notes: String = "", dueDate: Date? = nil) {
        self.title = title
        self.notes = notes
        self.isCompleted = false
        self.dueDate = dueDate
        self.createdAt = .now
        self.subtasks = []
    }
}
```

### Container Setup
```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup { ContentView() }
            .modelContainer(for: [Task.self, Category.self])
    }
}
```

### Querying with @Query
```swift
struct TaskListView: View {
    @Query(filter: #Predicate<Task> { !$0.isCompleted },
           sort: \.createdAt, order: .reverse)
    private var tasks: [Task]
    
    @Environment(\.modelContext) private var context
    
    var body: some View {
        List(tasks) { task in
            TaskRow(task: task)
        }
    }
    
    func addTask(title: String) {
        let task = Task(title: title)
        context.insert(task)
        // SwiftData auto-saves
    }
    
    func deleteTask(_ task: Task) {
        context.delete(task)
    }
}
```

---

## 5. UserDefaults & Keychain

### UserDefaults (non-sensitive data)
```swift
// @AppStorage in SwiftUI
@AppStorage("hasCompletedOnboarding") private var hasOnboarded = false
@AppStorage("preferredTheme") private var theme: String = "system"

// Typed wrapper
enum UserDefaultsKey: String {
    case lastSyncDate, selectedLanguage, notificationsEnabled
}

extension UserDefaults {
    var lastSyncDate: Date? {
        get { object(forKey: UserDefaultsKey.lastSyncDate.rawValue) as? Date }
        set { set(newValue, forKey: UserDefaultsKey.lastSyncDate.rawValue) }
    }
}
```

### Keychain (sensitive data — tokens, passwords, API keys)
```swift
import Security

enum KeychainManager {
    static func save(key: String, data: Data) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
        ]
        SecItemDelete(query as CFDictionary) // Remove existing
        let status = SecItemAdd(query as CFDictionary, nil)
        guard status == errSecSuccess else { throw KeychainError.saveFailed(status) }
    }
    
    static func load(key: String) throws -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)
        guard status == errSecSuccess else {
            if status == errSecItemNotFound { return nil }
            throw KeychainError.loadFailed(status)
        }
        return result as? Data
    }
    
    static func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        SecItemDelete(query as CFDictionary)
    }
}

// Store auth token
func saveToken(_ token: String) throws {
    try KeychainManager.save(key: "auth_token", data: Data(token.utf8))
}

func loadToken() throws -> String? {
    guard let data = try KeychainManager.load(key: "auth_token") else { return nil }
    return String(data: data, encoding: .utf8)
}
```

---

## 6. Caching Strategies

### In-Memory Cache
```swift
actor ImageCache {
    private let cache = NSCache<NSString, UIImage>()
    
    init() {
        cache.countLimit = 100
        cache.totalCostLimit = 50 * 1024 * 1024 // 50 MB
    }
    
    func image(for url: URL) -> UIImage? {
        cache.object(forKey: url.absoluteString as NSString)
    }
    
    func setImage(_ image: UIImage, for url: URL) {
        let cost = image.jpegData(compressionQuality: 1)?.count ?? 0
        cache.setObject(image, forKey: url.absoluteString as NSString, cost: cost)
    }
}
```

### URLCache (HTTP caching)
```swift
let config = URLSessionConfiguration.default
config.urlCache = URLCache(
    memoryCapacity: 20 * 1024 * 1024,  // 20 MB memory
    diskCapacity: 100 * 1024 * 1024     // 100 MB disk
)
config.requestCachePolicy = .returnCacheDataElseLoad
let session = URLSession(configuration: config)
```

### Offline-First Pattern
```swift
protocol OfflineCapableRepository {
    associatedtype T
    func fetch() async throws -> [T]        // Network first, cache fallback
    func fetchCached() -> [T]               // Cache only
    func sync() async throws                // Push local changes
}
```



---
