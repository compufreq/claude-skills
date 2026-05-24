---
name: android-kotlin-dev
description: >-
  Android development with Kotlin, Jetpack Compose, XML Views, Retrofit, Room, Hilt, Coroutines, and Play Store submission. Use when the user mentions Android, Kotlin, Compose UI, XML layout, Retrofit, OkHttp, Room, DataStore, Hilt, Dagger, ViewModel, StateFlow, Coroutines, Flow, WorkManager, Navigation, Gradle, Material Design, Play Store, APK, AAB, ProGuard, R8, or building Android apps with MVVM/MVI/Clean Architecture. Trigger even without saying "Android" if describing Kotlin mobile development with Gradle or Compose.
---

# Android Kotlin Development

A production-grade skill for native Android development with Kotlin, Jetpack Compose, XML Views,
and the Android Jetpack ecosystem. Covers architecture patterns, networking, persistence,
multi-module projects, and Play Store submission.

## Quick Reference

| Area | Key Technologies | Reference File |
|------|-----------------|----------------|
| UI (Modern) | Jetpack Compose, Material 3 | `references/compose-ui.md` |
| UI (Legacy) | XML Views, View Binding, Fragments | `references/xml-views.md` |
| Architecture | MVVM, MVI, Clean, Multi-module | `references/architecture.md` |
| Networking | Retrofit, Ktor, OkHttp, Coroutines | `references/networking-data.md` |
| Persistence | Room, DataStore, SharedPreferences | `references/networking-data.md` |
| Play Store | Policies, metadata, submission | `references/play-store.md` |

## Core Workflow

1. **Identify the request type:**
   - Compose UI → Read `references/compose-ui.md`
   - XML/legacy UI → Read `references/xml-views.md`
   - Architecture/DI → Read `references/architecture.md`
   - API/database → Read `references/networking-data.md`
   - Play Store → Read `references/play-store.md`

2. **Identify target SDK** — Default to minSdk 26 (Android 8.0), targetSdk 35 for new projects.

3. **Apply architecture** — Default MVVM+Hilt for most apps. MVI for complex UI state.
   Clean Architecture for large teams. Multi-module for 50k+ LOC apps.

4. **Generate code** following Kotlin conventions and Google's Android best practices.

---

## Project Structure (Single Module — MVVM)

```
app/
├── src/main/
│   ├── java/com/example/myapp/
│   │   ├── MyApplication.kt
│   │   ├── MainActivity.kt
│   │   ├── di/
│   │   │   ├── AppModule.kt
│   │   │   ├── NetworkModule.kt
│   │   │   └── DatabaseModule.kt
│   │   ├── ui/
│   │   │   ├── navigation/
│   │   │   │   └── AppNavigation.kt
│   │   │   ├── theme/
│   │   │   │   ├── Theme.kt
│   │   │   │   ├── Color.kt
│   │   │   │   └── Type.kt
│   │   │   ├── components/
│   │   │   │   ├── LoadingIndicator.kt
│   │   │   │   ├── ErrorScreen.kt
│   │   │   │   └── PrimaryButton.kt
│   │   │   ├── home/
│   │   │   │   ├── HomeScreen.kt
│   │   │   │   └── HomeViewModel.kt
│   │   │   ├── auth/
│   │   │   │   ├── LoginScreen.kt
│   │   │   │   └── AuthViewModel.kt
│   │   │   └── settings/
│   │   ├── data/
│   │   │   ├── remote/
│   │   │   │   ├── ApiService.kt
│   │   │   │   ├── dto/
│   │   │   │   │   └── UserDto.kt
│   │   │   │   └── interceptors/
│   │   │   │       └── AuthInterceptor.kt
│   │   │   ├── local/
│   │   │   │   ├── AppDatabase.kt
│   │   │   │   ├── dao/
│   │   │   │   │   └── UserDao.kt
│   │   │   │   └── entity/
│   │   │   │       └── UserEntity.kt
│   │   │   └── repository/
│   │   │       └── UserRepositoryImpl.kt
│   │   ├── domain/
│   │   │   ├── model/
│   │   │   │   └── User.kt
│   │   │   ├── repository/
│   │   │   │   └── UserRepository.kt
│   │   │   └── usecase/
│   │   │       └── GetUserUseCase.kt
│   │   └── util/
│   │       ├── Resource.kt
│   │       └── Extensions.kt
│   ├── res/
│   │   ├── values/
│   │   │   ├── strings.xml
│   │   │   ├── colors.xml
│   │   │   └── themes.xml
│   │   └── ...
│   └── AndroidManifest.xml
├── src/test/           # Unit tests
├── src/androidTest/    # Instrumentation tests
├── build.gradle.kts
└── proguard-rules.pro
```

## Multi-Module Structure

```
project/
├── app/                        # Application module — wires everything together
├── core/
│   ├── core-ui/                # Shared Compose components, theme
│   ├── core-network/           # Retrofit, OkHttp, API client
│   ├── core-database/          # Room database, DAOs
│   ├── core-common/            # Utilities, extensions, base classes
│   └── core-testing/           # Test utilities, fakes, rules
├── feature/
│   ├── feature-home/           # Home feature module
│   ├── feature-auth/           # Auth feature module
│   ├── feature-settings/       # Settings feature module
│   └── feature-profile/        # Profile feature module
├── domain/                     # Domain models, repository interfaces, use cases
├── build-logic/                # Convention plugins for Gradle
│   └── convention/
│       └── src/main/kotlin/
├── gradle/
│   └── libs.versions.toml      # Version catalog
├── settings.gradle.kts
└── build.gradle.kts
```

---

## Kotlin Conventions

### Naming
- Classes/Interfaces: `PascalCase` — `UserRepository`, `HomeViewModel`
- Functions/Properties: `camelCase` — `fetchUser()`, `userName`
- Constants: `SCREAMING_SNAKE_CASE` — `const val MAX_RETRY = 3`
- Packages: `lowercase` — `com.example.myapp.data.remote`
- Compose functions: `PascalCase` (they produce UI) — `HomeScreen()`, `PrimaryButton()`
- Compose parameters: `camelCase` — `onClick`, `modifier`, `contentPadding`

### Kotlin Style
- Use `val` over `var` — immutability by default
- Use data classes for models: `data class User(val id: String, val name: String)`
- Use sealed classes/interfaces for restricted hierarchies
- Prefer extension functions over utility classes
- Use `when` expressions exhaustively with sealed types
- Use coroutines + Flow for async work (not callbacks)
- Use `require()` and `check()` for preconditions
- Use scope functions judiciously: `let`, `also`, `apply`, `run`, `with`

### Sealed Class for UI State

```kotlin
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val cause: Throwable? = null) : UiState<Nothing>
}
```

### Resource Wrapper (for repository results)

```kotlin
sealed interface Resource<out T> {
    data class Success<T>(val data: T) : Resource<T>
    data class Error(val message: String, val cause: Throwable? = null) : Resource<Nothing>
    data object Loading : Resource<Nothing>
}

// Usage in ViewModel
fun <T> Flow<T>.asResource(): Flow<Resource<T>> = this
    .map<T, Resource<T>> { Resource.Success(it) }
    .onStart { emit(Resource.Loading) }
    .catch { emit(Resource.Error(it.message ?: "Unknown error", it)) }
```

---

## Key Patterns

### ViewModel (Hilt-injected)

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val getUsersUseCase: GetUsersUseCase,
    private val savedStateHandle: SavedStateHandle,
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<User>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<User>>> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            getUsersUseCase()
                .catch { _uiState.value = UiState.Error(it.message ?: "Failed to load") }
                .collect { _uiState.value = UiState.Success(it) }
        }
    }

    fun refresh() = loadUsers()
}
```

### Compose Screen with ViewModel

```kotlin
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel(),
    onNavigateToDetail: (String) -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    HomeScreenContent(
        uiState = uiState,
        onRefresh = viewModel::refresh,
        onItemClick = onNavigateToDetail,
    )
}

@Composable
private fun HomeScreenContent(
    uiState: UiState<List<User>>,
    onRefresh: () -> Unit,
    onItemClick: (String) -> Unit,
) {
    when (uiState) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Error -> ErrorScreen(message = uiState.message, onRetry = onRefresh)
        is UiState.Success -> {
            LazyColumn {
                items(uiState.data, key = { it.id }) { user ->
                    UserCard(user = user, onClick = { onItemClick(user.id) })
                }
            }
        }
    }
}
```

---

## Gradle Version Catalog (libs.versions.toml)

```toml
[versions]
kotlin = "2.0.21"
agp = "8.7.3"
compose-bom = "2024.12.01"
hilt = "2.53.1"
room = "2.6.1"
retrofit = "2.11.0"
coroutines = "1.9.0"
lifecycle = "2.8.7"
navigation = "2.8.5"
datastore = "1.1.1"

[libraries]
# Compose
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
compose-material3 = { group = "androidx.compose.material3", name = "material3" }
compose-tooling-preview = { group = "androidx.compose.ui", name = "ui-tooling-preview" }

# Lifecycle
lifecycle-viewmodel = { group = "androidx.lifecycle", name = "lifecycle-viewmodel-compose", version.ref = "lifecycle" }
lifecycle-runtime = { group = "androidx.lifecycle", name = "lifecycle-runtime-compose", version.ref = "lifecycle" }

# Hilt
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-android-compiler", version.ref = "hilt" }
hilt-navigation = { group = "androidx.hilt", name = "hilt-navigation-compose", version = "1.2.0" }

# Room
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }

# Retrofit
retrofit = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
retrofit-gson = { group = "com.squareup.retrofit2", name = "converter-gson", version.ref = "retrofit" }
okhttp-logging = { group = "com.squareup.okhttp3", name = "logging-interceptor", version = "4.12.0" }

# Navigation
navigation-compose = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigation" }

# DataStore
datastore-preferences = { group = "androidx.datastore", name = "datastore-preferences", version.ref = "datastore" }

# Coroutines
coroutines-android = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-android", version.ref = "coroutines" }
coroutines-test = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-test", version.ref = "coroutines" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version = "2.0.21-1.0.28" }
```

---

## Testing Strategy

### Unit Tests
- Test ViewModels with fake repositories (use Turbine for Flow testing)
- Test Use Cases with mocked dependencies
- Test Repositories with mock API/DAO
- Use `kotlinx-coroutines-test` for `runTest {}` and `TestDispatcher`

### UI Tests
- Compose: Use `createComposeRule()` and semantic matchers
- XML: Use Espresso
- Use Hilt for test DI (`@HiltAndroidTest`)

### Testing Libraries
- JUnit 5 or JUnit 4 + AndroidX Test
- MockK or Mockito-Kotlin for mocking
- Turbine for Flow testing
- Robolectric for JVM-based Android tests

---

## Best Practices

1. Use Kotlin DSL (`build.gradle.kts`) and version catalogs
2. Use `StateFlow` + `collectAsStateWithLifecycle()` in Compose
3. Keep Compose functions small — extract composables at 30+ lines
4. Use `Modifier` as the first optional parameter of every composable
5. Preview composables with `@Preview` using sample data
6. Use sealed interfaces for UI state (exhaustive `when`)
7. Inject dispatchers for testability: `@IoDispatcher`, `@MainDispatcher`
8. Use R8 (ProGuard replacement) for release builds
9. Profile with Android Studio Profiler before optimizing
10. Follow Material 3 guidelines for consistent, modern UI



---
