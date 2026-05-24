# Android Architecture Patterns Reference

## Table of Contents
1. MVVM with Hilt
2. MVI (Model-View-Intent)
3. Clean Architecture
4. Multi-Module Architecture
5. Dependency Injection with Hilt
6. Choosing the Right Architecture

---

## 1. MVVM with Hilt (Google Recommended)

```
View (Compose/Fragment) ←observes← ViewModel → Repository → DataSource
                                       ↓
                                   Use Cases (optional)
```

### Hilt ViewModel

```kotlin
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: UserRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    private val _events = Channel<HomeEvent>()
    val events = _events.receiveAsFlow()  // One-time events (navigation, snackbar)

    init { loadUsers() }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            repository.getUsers()
                .catch { e -> _uiState.update { it.copy(isLoading = false, error = e.message) } }
                .collect { users -> _uiState.update { it.copy(isLoading = false, users = users) } }
        }
    }

    fun onDeleteUser(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            _events.send(HomeEvent.ShowSnackbar("User deleted"))
        }
    }
}

data class HomeUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
)

sealed interface HomeEvent {
    data class ShowSnackbar(val message: String) : HomeEvent
    data class NavigateToDetail(val userId: String) : HomeEvent
}
```

### One-Time Events in Compose
```kotlin
@Composable
fun HomeScreen(viewModel: HomeViewModel = hiltViewModel(), onNavigateToDetail: (String) -> Unit) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is HomeEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
                is HomeEvent.NavigateToDetail -> onNavigateToDetail(event.userId)
            }
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { padding ->
        // UI content
    }
}
```

---

## 2. MVI (Model-View-Intent)

Stricter unidirectional data flow. All user interactions are modeled as Intents.

```
User → Intent → Reducer(State, Intent) → new State → View
                     ↓
                  Side Effects
```

### MVI Implementation

```kotlin
// Contract
interface HomeContract {
    data class State(
        val items: List<Item> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null,
    )

    sealed interface Intent {
        data object LoadItems : Intent
        data object Refresh : Intent
        data class DeleteItem(val id: String) : Intent
        data class Search(val query: String) : Intent
    }

    sealed interface Effect {
        data class ShowToast(val message: String) : Effect
        data class NavigateToDetail(val id: String) : Effect
    }
}

// ViewModel
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: ItemRepository,
) : ViewModel() {

    private val _state = MutableStateFlow(HomeContract.State())
    val state: StateFlow<HomeContract.State> = _state.asStateFlow()

    private val _effects = Channel<HomeContract.Effect>()
    val effects = _effects.receiveAsFlow()

    fun handleIntent(intent: HomeContract.Intent) {
        when (intent) {
            is HomeContract.Intent.LoadItems -> reduce { copy(isLoading = true) }.also { loadItems() }
            is HomeContract.Intent.Refresh -> reduce { copy(isLoading = true) }.also { loadItems() }
            is HomeContract.Intent.DeleteItem -> deleteItem(intent.id)
            is HomeContract.Intent.Search -> search(intent.query)
        }
    }

    private fun reduce(block: HomeContract.State.() -> HomeContract.State) {
        _state.update(block)
    }

    private fun loadItems() {
        viewModelScope.launch {
            try {
                val items = repository.getItems()
                reduce { copy(isLoading = false, items = items, error = null) }
            } catch (e: Exception) {
                reduce { copy(isLoading = false, error = e.message) }
            }
        }
    }

    private fun deleteItem(id: String) {
        viewModelScope.launch {
            repository.deleteItem(id)
            reduce { copy(items = items.filter { it.id != id }) }
            _effects.send(HomeContract.Effect.ShowToast("Item deleted"))
        }
    }
}

// View
@Composable
fun HomeScreen(viewModel: HomeViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    HomeContent(state = state, onIntent = viewModel::handleIntent)
}
```

---

## 3. Clean Architecture

### Layer Separation

```
┌─────────────────────────────────────┐
│  Presentation (UI)                  │  ← Compose, ViewModels
│  depends on: Domain                 │
├─────────────────────────────────────┤
│  Domain (Business Logic)            │  ← Use Cases, Entities, Repository interfaces
│  depends on: NOTHING               │  ← Pure Kotlin, no Android imports
├─────────────────────────────────────┤
│  Data (Implementation)              │  ← Repository impl, API, Database
│  depends on: Domain                 │
└─────────────────────────────────────┘
```

### Domain Layer

```kotlin
// Entity (domain model)
data class User(
    val id: String,
    val name: String,
    val email: String,
    val isVerified: Boolean,
)

// Repository interface (in domain — implemented in data)
interface UserRepository {
    fun getUsers(): Flow<List<User>>
    suspend fun getUser(id: String): User
    suspend fun updateUser(user: User)
    suspend fun deleteUser(id: String)
}

// Use Case
class GetUsersUseCase @Inject constructor(
    private val repository: UserRepository,
) {
    operator fun invoke(): Flow<List<User>> =
        repository.getUsers().map { users -> users.filter { it.isVerified }.sortedBy { it.name } }
}

class DeleteUserUseCase @Inject constructor(
    private val repository: UserRepository,
    private val analyticsTracker: AnalyticsTracker,
) {
    suspend operator fun invoke(userId: String) {
        repository.deleteUser(userId)
        analyticsTracker.track(AnalyticsEvent.UserDeleted(userId))
    }
}
```

### Data Layer

```kotlin
// DTO (API response model)
@Serializable
data class UserDto(
    @SerialName("id") val id: String,
    @SerialName("full_name") val fullName: String,
    @SerialName("email_address") val emailAddress: String,
    @SerialName("is_verified") val isVerified: Boolean,
) {
    fun toDomain(): User = User(id = id, name = fullName, email = emailAddress, isVerified = isVerified)
}

// Repository implementation
class UserRepositoryImpl @Inject constructor(
    private val api: UserApiService,
    private val dao: UserDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher,
) : UserRepository {

    override fun getUsers(): Flow<List<User>> =
        dao.getAllUsers()
            .map { entities -> entities.map { it.toDomain() } }
            .flowOn(ioDispatcher)

    override suspend fun getUser(id: String): User = withContext(ioDispatcher) {
        try {
            val dto = api.getUser(id)
            dao.insertUser(dto.toEntity())
            dto.toDomain()
        } catch (e: Exception) {
            dao.getUser(id)?.toDomain() ?: throw e
        }
    }
}
```

---

## 4. Multi-Module Architecture

### Module Types

| Module | Purpose | Dependencies |
|--------|---------|-------------|
| `:app` | Application, wires everything | All modules |
| `:core:network` | API client, interceptors | `:core:common` |
| `:core:database` | Room database, DAOs | `:core:common` |
| `:core:ui` | Shared composables, theme | `:core:common` |
| `:core:common` | Utilities, extensions | None |
| `:core:testing` | Test fakes, utilities | `:core:common` |
| `:domain` | Models, use cases, repo interfaces | `:core:common` |
| `:feature:home` | Home feature | `:domain`, `:core:ui`, `:core:network` |
| `:feature:auth` | Auth feature | `:domain`, `:core:ui`, `:core:network` |

### Module Configuration (build.gradle.kts)

```kotlin
// feature module
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.feature.home"
    compileSdk = 35
    defaultConfig { minSdk = 26 }
    buildFeatures { compose = true }
}

dependencies {
    implementation(project(":domain"))
    implementation(project(":core:ui"))
    implementation(project(":core:common"))

    implementation(libs.compose.ui)
    implementation(libs.compose.material3)
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
    implementation(libs.hilt.navigation)
    implementation(libs.lifecycle.viewmodel)
    implementation(libs.lifecycle.runtime)

    testImplementation(project(":core:testing"))
}
```

### settings.gradle.kts

```kotlin
include(":app")
include(":domain")
include(":core:network")
include(":core:database")
include(":core:ui")
include(":core:common")
include(":core:testing")
include(":feature:home")
include(":feature:auth")
include(":feature:settings")
```

### Benefits
- Faster build times (parallel compilation, incremental builds)
- Enforced dependency rules (features can't depend on each other)
- Better code ownership (team per module)
- Easier testing (modules are isolated)
- Dynamic feature delivery (on-demand modules)

---

## 5. Dependency Injection with Hilt

### Setup

```kotlin
// Application
@HiltAndroidApp
class MyApplication : Application()

// Activity
@AndroidEntryPoint
class MainActivity : ComponentActivity()
```

### Modules

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient =
        OkHttpClient.Builder()
            .addInterceptor(AuthInterceptor())
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG) Level.BODY else Level.NONE
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.API_BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provideUserApiService(retrofit: Retrofit): UserApiService =
        retrofit.create(UserApiService::class.java)
}

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app_db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()
}

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// Dispatcher qualifiers
@Qualifier @Retention(AnnotationRetention.BINARY) annotation class IoDispatcher
@Qualifier @Retention(AnnotationRetention.BINARY) annotation class MainDispatcher

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {
    @IoDispatcher @Provides fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
    @MainDispatcher @Provides fun provideMainDispatcher(): CoroutineDispatcher = Dispatchers.Main
}
```

---

## 6. Choosing the Right Architecture

| Criteria | MVVM | MVI | Clean | Multi-Module |
|----------|------|-----|-------|-------------|
| Team size | 1-5 | 2-6 | 3-10 | 5+ |
| App size | Any | Medium+ | Large | Large (50k+ LOC) |
| Complexity | Low-Medium | Medium-High | High | High |
| Learning curve | Low | Medium | High | High |
| State management | Good | Excellent | Good | Good |
| Testability | Good | Excellent | Excellent | Excellent |
| Build speed | N/A | N/A | N/A | Better (parallel) |
| Google support | Official | Community | Community | Official guidance |

### Recommendation
- **Start with MVVM + Hilt** — it's Google's recommendation and works for 90% of apps
- **Add MVI** when UI state gets complex (multiple interacting states, undo/redo)
- **Add Clean Architecture** when the team grows beyond 3-4 developers
- **Add Multi-Module** when build times exceed 2 minutes or LOC exceeds 50k
- These are **additive** — you can layer them: Multi-Module + Clean + MVI



---
