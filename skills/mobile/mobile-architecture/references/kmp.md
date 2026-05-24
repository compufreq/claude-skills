# Kotlin Multiplatform (KMP) Reference

## Table of Contents
1. KMP Overview
2. Project Structure
3. What to Share vs Keep Platform-Specific
4. expect/actual Mechanism
5. Shared Architecture Patterns
6. Networking with Ktor
7. Persistence with SQLDelight
8. Testing Shared Code
9. Gradle Configuration
10. Migration Strategy

---

## 1. KMP Overview

Kotlin Multiplatform allows sharing Kotlin code between iOS and Android while keeping
platform-specific code where it belongs. It's not "write once, run everywhere" — it's
"share what makes sense, keep platform idioms where they matter."

### What KMP Is
- Shared business logic compiled to JVM (Android) and native (iOS via Kotlin/Native)
- Platform-specific APIs available through `expect/actual` mechanism
- Gradle-based build system with multiplatform targets
- First-party support from JetBrains, adopted by Google for Jetpack libraries

### What KMP Is NOT
- A UI framework (use SwiftUI/Compose for UI)
- A replacement for native development skills
- A guarantee that code will work identically on all platforms

---

## 2. Project Structure

```
my-kmp-app/
├── shared/                          # KMP shared module
│   ├── src/
│   │   ├── commonMain/              # Shared code (Kotlin)
│   │   │   └── kotlin/com/example/shared/
│   │   │       ├── domain/
│   │   │       │   ├── model/
│   │   │       │   │   └── User.kt
│   │   │       │   ├── repository/
│   │   │       │   │   └── UserRepository.kt
│   │   │       │   └── usecase/
│   │   │       │       └── GetUsersUseCase.kt
│   │   │       ├── data/
│   │   │       │   ├── remote/
│   │   │       │   │   ├── UserApi.kt
│   │   │       │   │   └── dto/UserDto.kt
│   │   │       │   ├── local/
│   │   │       │   │   └── UserLocalSource.kt
│   │   │       │   └── repository/
│   │   │       │       └── UserRepositoryImpl.kt
│   │   │       └── util/
│   │   │           └── Platform.kt   # expect declarations
│   │   ├── commonTest/               # Shared tests
│   │   │   └── kotlin/
│   │   ├── androidMain/              # Android-specific implementations
│   │   │   └── kotlin/com/example/shared/util/
│   │   │       └── Platform.android.kt
│   │   ├── iosMain/                  # iOS-specific implementations
│   │   │   └── kotlin/com/example/shared/util/
│   │   │       └── Platform.ios.kt
│   │   ├── androidUnitTest/
│   │   └── iosTest/
│   └── build.gradle.kts
├── androidApp/                       # Android application
│   ├── src/main/
│   │   └── kotlin/com/example/android/
│   │       ├── MainActivity.kt
│   │       └── ui/                   # Jetpack Compose UI
│   └── build.gradle.kts
├── iosApp/                           # iOS application (Xcode project)
│   ├── iosApp/
│   │   ├── ContentView.swift
│   │   └── iOSApp.swift
│   └── iosApp.xcodeproj
├── gradle/
│   └── libs.versions.toml
├── build.gradle.kts
└── settings.gradle.kts
```

---

## 3. What to Share vs Keep Platform-Specific

### Share (commonMain)

| Layer | Share | Examples |
|-------|-------|---------|
| Domain models | ✅ Always | `User`, `Product`, `Order` |
| Repository interfaces | ✅ Always | `UserRepository` protocol |
| Use cases | ✅ Always | `GetUsersUseCase`, `LoginUseCase` |
| Business rules | ✅ Always | Validation, calculations, transformations |
| Networking (Ktor) | ✅ Usually | API client, DTOs, serialization |
| Database (SQLDelight) | ✅ Usually | Queries, schema, local data source |
| State management | ✅ Often | State classes, reducers |
| Utilities | ✅ Often | Date formatting, string utils, logging |

### Keep Platform-Specific

| Layer | Platform-Specific | Why |
|-------|-------------------|-----|
| UI | ✅ Always | SwiftUI / Compose are fundamentally different |
| Navigation | ✅ Always | Platform navigation is too different |
| ViewModels | ⚠️ Usually | Lifecycle management differs (but logic can be shared) |
| DI | ✅ Always | Hilt vs Swinject/manual |
| Push notifications | ✅ Always | APNs vs FCM |
| Biometrics | ✅ Always | Face ID vs Fingerprint APIs |
| Permissions | ✅ Always | Platform-specific permission flows |
| File system | ⚠️ Usually | Paths differ; use expect/actual |
| Keychain/Keystore | ✅ Always | Security APIs are platform-specific |

### The 60/40 Rule
A well-structured KMP app typically shares ~60% of code (domain, data, business logic)
and keeps ~40% platform-specific (UI, navigation, platform integrations).

---

## 4. expect/actual Mechanism

`expect` declares an API in common code. `actual` implements it per platform.

### Example: Platform Info

```kotlin
// commonMain
expect class Platform() {
    val name: String
    val version: String
}

expect fun createUUID(): String
```

```kotlin
// androidMain
actual class Platform actual constructor() {
    actual val name: String = "Android"
    actual val version: String = "${android.os.Build.VERSION.SDK_INT}"
}

actual fun createUUID(): String = java.util.UUID.randomUUID().toString()
```

```kotlin
// iosMain
import platform.UIKit.UIDevice
import platform.Foundation.NSUUID

actual class Platform actual constructor() {
    actual val name: String = UIDevice.currentDevice.systemName
    actual val version: String = UIDevice.currentDevice.systemVersion
}

actual fun createUUID(): String = NSUUID().UUIDString
```

### Example: Secure Storage

```kotlin
// commonMain
expect class SecureStorage {
    fun getString(key: String): String?
    fun putString(key: String, value: String)
    fun remove(key: String)
}
```

```kotlin
// androidMain
actual class SecureStorage(private val context: Context) {
    private val prefs = EncryptedSharedPreferences.create(/* ... */)
    actual fun getString(key: String): String? = prefs.getString(key, null)
    actual fun putString(key: String, value: String) { prefs.edit().putString(key, value).apply() }
    actual fun remove(key: String) { prefs.edit().remove(key).apply() }
}
```

```kotlin
// iosMain
import platform.Security.*

actual class SecureStorage {
    actual fun getString(key: String): String? { /* Keychain query */ }
    actual fun putString(key: String, value: String) { /* Keychain save */ }
    actual fun remove(key: String) { /* Keychain delete */ }
}
```

### When to Use expect/actual
- Platform-specific implementations of a common interface
- Accessing platform APIs (file system, crypto, sensors)
- Factory methods that need platform context

### When NOT to Use expect/actual
- If a multiplatform library already exists (Ktor, SQLDelight, kotlinx.datetime)
- For UI code (keep entirely platform-specific)
- For simple platform differences (use `if` checks or interface injection instead)

---

## 5. Shared Architecture Patterns

### Shared ViewModel Logic (KMP-ViewModel)

```kotlin
// commonMain — shared ViewModel logic
class UserListSharedViewModel(
    private val getUsersUseCase: GetUsersUseCase,
) {
    private val _state = MutableStateFlow(UserListState())
    val state: StateFlow<UserListState> = _state.asStateFlow()

    fun load(scope: CoroutineScope) {
        scope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val users = getUsersUseCase()
                _state.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }
}

data class UserListState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)
```

```kotlin
// Android — thin wrapper
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val shared: UserListSharedViewModel,
) : ViewModel() {
    val state = shared.state
    fun load() = shared.load(viewModelScope)
}
```

```swift
// iOS — thin wrapper
@Observable
class UserListViewModel {
    private let shared: UserListSharedViewModel
    var state: UserListState { shared.state.value as! UserListState }

    init(shared: UserListSharedViewModel) {
        self.shared = shared
    }

    func load() {
        // Use SKIE or KMP-NativeCoroutines for proper Swift integration
    }
}
```

---

## 6. Networking with Ktor (KMP)

```kotlin
// commonMain
class UserApi(private val client: HttpClient) {
    suspend fun getUsers(): List<UserDto> =
        client.get("api/v1/users").body()

    suspend fun getUser(id: String): UserDto =
        client.get("api/v1/users/$id").body()

    suspend fun createUser(request: CreateUserRequest): UserDto =
        client.post("api/v1/users") { setBody(request) }.body()
}

// HttpClient factory (commonMain)
fun createHttpClient(): HttpClient = HttpClient {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            isLenient = true
        })
    }
    install(Logging) { level = LogLevel.BODY }
    defaultRequest {
        url("https://api.example.com/")
        contentType(ContentType.Application.Json)
    }
}
```

### Platform-Specific Engine

```kotlin
// androidMain
actual fun createPlatformHttpClient(): HttpClient = HttpClient(Android) { /* config */ }

// iosMain
actual fun createPlatformHttpClient(): HttpClient = HttpClient(Darwin) { /* config */ }
```

---

## 7. Persistence with SQLDelight (KMP)

```kotlin
// build.gradle.kts
sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.shared.db")
        }
    }
}
```

```sql
-- commonMain/sqldelight/com/example/shared/db/User.sq
CREATE TABLE UserEntity (
    id TEXT NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    is_active INTEGER AS Boolean NOT NULL DEFAULT 1,
    created_at INTEGER NOT NULL
);

getAll:
SELECT * FROM UserEntity ORDER BY name ASC;

getById:
SELECT * FROM UserEntity WHERE id = ?;

insert:
INSERT OR REPLACE INTO UserEntity(id, name, email, is_active, created_at)
VALUES (?, ?, ?, ?, ?);

deleteById:
DELETE FROM UserEntity WHERE id = ?;

search:
SELECT * FROM UserEntity WHERE name LIKE '%' || ? || '%';
```

```kotlin
// commonMain — Repository using SQLDelight
class UserLocalSource(private val db: AppDatabase) {
    fun getAll(): Flow<List<UserEntity>> =
        db.userEntityQueries.getAll().asFlow().mapToList(Dispatchers.IO)

    suspend fun insert(user: UserEntity) {
        db.userEntityQueries.insert(user.id, user.name, user.email, user.is_active, user.created_at)
    }
}
```

### Driver Creation (expect/actual)
```kotlin
// commonMain
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

// androidMain
actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver =
        AndroidSqliteDriver(AppDatabase.Schema, context, "app.db")
}

// iosMain
actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver =
        NativeSqliteDriver(AppDatabase.Schema, "app.db")
}
```

---

## 8. Testing Shared Code

```kotlin
// commonTest
class GetUsersUseCaseTest {
    private val fakeRepository = FakeUserRepository()
    private val useCase = GetUsersUseCase(fakeRepository)

    @Test
    fun `returns active users sorted by name`() = runTest {
        fakeRepository.setUsers(listOf(
            User(id = "1", name = "Charlie", isActive = true),
            User(id = "2", name = "Alice", isActive = true),
            User(id = "3", name = "Bob", isActive = false),
        ))

        val result = useCase()

        assertEquals(2, result.size)
        assertEquals("Alice", result[0].name)
        assertEquals("Charlie", result[1].name)
    }
}

// FakeRepository (commonTest)
class FakeUserRepository : UserRepository {
    private var users = mutableListOf<User>()
    private var error: Exception? = null

    fun setUsers(newUsers: List<User>) { users = newUsers.toMutableList() }
    fun setError(e: Exception) { error = e }

    override suspend fun getUsers(): List<User> {
        error?.let { throw it }
        return users.toList()
    }
}
```

---

## 9. Gradle Configuration

### settings.gradle.kts
```kotlin
pluginManagement {
    repositories {
        google()
        gradlePluginPortal()
        mavenCentral()
    }
}

include(":shared")
include(":androidApp")
```

### shared/build.gradle.kts
```kotlin
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    alias(libs.plugins.kotlinSerialization)
    alias(libs.plugins.sqldelight)  // If using SQLDelight
}

kotlin {
    androidTarget { compilations.all { kotlinOptions { jvmTarget = "17" } } }

    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "shared"
            isStatic = true
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.ktor.client.core)
            implementation(libs.ktor.client.content.negotiation)
            implementation(libs.ktor.serialization.json)
            implementation(libs.kotlinx.datetime)
        }
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
        }
        androidMain.dependencies {
            implementation(libs.ktor.client.android)
            implementation(libs.sqldelight.android.driver)
        }
        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.native.driver)
        }
    }
}

android {
    namespace = "com.example.shared"
    compileSdk = 35
    defaultConfig { minSdk = 26 }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
```

---

## 10. Migration Strategy

### Incremental KMP Adoption

1. **Start with domain models** — Share data classes first (lowest risk)
2. **Share business logic** — Move use cases and validation to shared module
3. **Share networking** — Move API client + DTOs to Ktor in shared module
4. **Share persistence** — Move database schema to SQLDelight
5. **Keep UI native** — Always. SwiftUI and Compose are too different to share.

### Migration Checklist
- [ ] Create shared module with KMP Gradle plugin
- [ ] Move one domain model to commonMain — verify it compiles on both targets
- [ ] Move one use case — verify tests pass on both platforms
- [ ] Integrate shared module into Android app (add dependency)
- [ ] Integrate shared module into iOS app (embed framework)
- [ ] Remove duplicated code from platform apps
- [ ] Repeat for each layer

### iOS Integration Options

| Method | Complexity | Best For |
|--------|-----------|---------|
| Xcode framework (direct) | Medium | Simple projects |
| CocoaPods plugin | Low | Teams using CocoaPods |
| SPM (Swift Package Manager) | Medium | Modern iOS projects |
| SKIE (Swift-friendly API) | Low | Better Swift interop |

### Common Pitfalls
- Trying to share UI → Don't. Keep UI platform-native.
- Ignoring iOS developer experience → Swift interop matters. Use SKIE.
- Sharing too much too fast → Start small, prove value, expand.
- Not testing on both platforms → CI must build both Android and iOS.
- Forgetting iOS memory model → Kotlin/Native has different concurrency rules.



---
