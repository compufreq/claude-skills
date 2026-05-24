# Networking & Data Persistence Reference

## Table of Contents
1. Retrofit
2. Ktor Client
3. OkHttp Interceptors
4. Room Database
5. DataStore
6. Offline-First Pattern

---

## 1. Retrofit

### API Service Definition
```kotlin
interface UserApiService {
    @GET("api/v1/users")
    suspend fun getUsers(): List<UserDto>

    @GET("api/v1/users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @POST("api/v1/users")
    suspend fun createUser(@Body request: CreateUserRequest): UserDto

    @PUT("api/v1/users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body request: UpdateUserRequest): UserDto

    @DELETE("api/v1/users/{id}")
    suspend fun deleteUser(@Path("id") id: String)

    @GET("api/v1/users")
    suspend fun searchUsers(
        @Query("q") query: String,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20,
    ): PaginatedResponse<UserDto>

    @Multipart
    @POST("api/v1/upload")
    suspend fun uploadImage(@Part image: MultipartBody.Part): UploadResponse

    @Headers("Cache-Control: max-age=3600")
    @GET("api/v1/config")
    suspend fun getConfig(): ConfigDto
}
```

### Response Wrapper
```kotlin
@Serializable
data class ApiResponse<T>(
    val data: T,
    val message: String? = null,
    val status: String,
)

@Serializable
data class PaginatedResponse<T>(
    val data: List<T>,
    val page: Int,
    val totalPages: Int,
    val totalItems: Int,
    val hasMore: Boolean,
)
```

### Error Handling
```kotlin
suspend fun <T> safeApiCall(apiCall: suspend () -> T): Resource<T> {
    return try {
        Resource.Success(apiCall())
    } catch (e: HttpException) {
        val errorBody = e.response()?.errorBody()?.string()
        val message = try {
            Gson().fromJson(errorBody, ApiError::class.java).message
        } catch (_: Exception) {
            "Server error (${e.code()})"
        }
        Resource.Error(message)
    } catch (e: IOException) {
        Resource.Error("Network error. Check your connection.")
    } catch (e: Exception) {
        Resource.Error(e.message ?: "Unknown error")
    }
}
```

---

## 2. Ktor Client

### Setup (alternative to Retrofit)
```kotlin
// build.gradle.kts
dependencies {
    implementation("io.ktor:ktor-client-android:2.3.12")
    implementation("io.ktor:ktor-client-content-negotiation:2.3.12")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.12")
    implementation("io.ktor:ktor-client-logging:2.3.12")
    implementation("io.ktor:ktor-client-auth:2.3.12")
}
```

### Client Configuration
```kotlin
@Module
@InstallIn(SingletonComponent::class)
object KtorModule {
    @Provides
    @Singleton
    fun provideKtorClient(): HttpClient = HttpClient(Android) {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                isLenient = true
                ignoreUnknownKeys = true
            })
        }
        install(Logging) {
            logger = Logger.ANDROID
            level = LogLevel.BODY
        }
        install(Auth) {
            bearer {
                loadTokens { BearerTokens(accessToken = tokenManager.getToken(), refreshToken = "") }
                refreshTokens { /* refresh logic */ }
            }
        }
        defaultRequest {
            url("https://api.example.com/")
            contentType(ContentType.Application.Json)
        }
    }
}

// Usage
class UserApiClient @Inject constructor(private val client: HttpClient) {
    suspend fun getUsers(): List<UserDto> = client.get("api/v1/users").body()
    suspend fun getUser(id: String): UserDto = client.get("api/v1/users/$id").body()
    suspend fun createUser(request: CreateUserRequest): UserDto =
        client.post("api/v1/users") { setBody(request) }.body()
}
```

---

## 3. OkHttp Interceptors

### Auth Interceptor
```kotlin
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager,
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val token = tokenManager.getAccessToken()
        val request = chain.request().newBuilder().apply {
            token?.let { addHeader("Authorization", "Bearer $it") }
        }.build()

        val response = chain.proceed(request)

        if (response.code == 401) {
            // Token refresh logic
            synchronized(this) {
                val newToken = runBlocking { tokenManager.refreshToken() }
                if (newToken != null) {
                    val newRequest = request.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()
                    response.close()
                    return chain.proceed(newRequest)
                }
            }
        }
        return response
    }
}
```

### Cache Interceptor
```kotlin
class CacheInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val response = chain.proceed(request)
        return response.newBuilder()
            .header("Cache-Control", "public, max-age=300") // 5 minutes
            .removeHeader("Pragma")
            .build()
    }
}

// OkHttpClient with cache
val cacheSize = 10L * 1024 * 1024 // 10 MB
val cache = Cache(context.cacheDir, cacheSize)
OkHttpClient.Builder().cache(cache).addNetworkInterceptor(CacheInterceptor()).build()
```

---

## 4. Room Database

### Entity
```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    @ColumnInfo(name = "full_name") val name: String,
    val email: String,
    @ColumnInfo(name = "is_verified") val isVerified: Boolean,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis(),
    @ColumnInfo(name = "updated_at") val updatedAt: Long = System.currentTimeMillis(),
) {
    fun toDomain(): User = User(id = id, name = name, email = email, isVerified = isVerified)
}

fun User.toEntity(): UserEntity = UserEntity(id = id, name = name, email = email, isVerified = isVerified)
```

### DAO
```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY full_name ASC")
    fun getAllUsers(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): UserEntity?

    @Query("SELECT * FROM users WHERE full_name LIKE '%' || :query || '%'")
    fun searchUsers(query: String): Flow<List<UserEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<UserEntity>)

    @Update
    suspend fun updateUser(user: UserEntity)

    @Delete
    suspend fun deleteUser(user: UserEntity)

    @Query("DELETE FROM users WHERE id = :id")
    suspend fun deleteById(id: String)

    @Query("DELETE FROM users")
    suspend fun deleteAll()

    @Transaction
    suspend fun replaceAll(users: List<UserEntity>) {
        deleteAll()
        insertUsers(users)
    }
}
```

### Database
```kotlin
@Database(
    entities = [UserEntity::class, TaskEntity::class],
    version = 2,
    exportSchema = true,
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun taskDao(): TaskDao
}

class Converters {
    @TypeConverter fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }
    @TypeConverter fun dateToTimestamp(date: Date?): Long? = date?.time
    @TypeConverter fun fromStringList(value: String?): List<String> =
        value?.split(",")?.filter { it.isNotBlank() } ?: emptyList()
    @TypeConverter fun toStringList(list: List<String>): String = list.joinToString(",")
}
```

### Migration
```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE users ADD COLUMN is_verified INTEGER NOT NULL DEFAULT 0")
    }
}

// In Hilt module
Room.databaseBuilder(context, AppDatabase::class.java, "app_db")
    .addMigrations(MIGRATION_1_2)
    .build()
```

---

## 5. DataStore

### Preferences DataStore (replaces SharedPreferences)
```kotlin
// Create
private val Context.dataStore by preferencesDataStore(name = "settings")

// Keys
object PrefsKeys {
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val USERNAME = stringPreferencesKey("username")
    val NOTIFICATION_ENABLED = booleanPreferencesKey("notification_enabled")
    val LAST_SYNC = longPreferencesKey("last_sync")
}

// Repository
class SettingsRepository @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    val darkMode: Flow<Boolean> = context.dataStore.data
        .map { it[PrefsKeys.DARK_MODE] ?: false }

    val username: Flow<String> = context.dataStore.data
        .map { it[PrefsKeys.USERNAME] ?: "" }

    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { it[PrefsKeys.DARK_MODE] = enabled }
    }

    suspend fun setUsername(name: String) {
        context.dataStore.edit { it[PrefsKeys.USERNAME] = name }
    }

    suspend fun clearAll() {
        context.dataStore.edit { it.clear() }
    }
}
```

### Proto DataStore (typed, schema-enforced)
```kotlin
// Define in user_settings.proto
// message UserSettings {
//     bool dark_mode = 1;
//     string language = 2;
//     int32 font_size = 3;
// }

// Serializer
object UserSettingsSerializer : Serializer<UserSettings> {
    override val defaultValue: UserSettings = UserSettings.getDefaultInstance()
    override suspend fun readFrom(input: InputStream): UserSettings =
        UserSettings.parseFrom(input)
    override suspend fun writeTo(t: UserSettings, output: OutputStream) =
        t.writeTo(output)
}
```

---

## 6. Offline-First Pattern

### Repository with Local + Remote

```kotlin
class UserRepositoryImpl @Inject constructor(
    private val api: UserApiService,
    private val dao: UserDao,
    @IoDispatcher private val ioDispatcher: CoroutineDispatcher,
) : UserRepository {

    // Observe local, refresh from remote
    override fun getUsers(): Flow<List<User>> = dao.getAllUsers()
        .map { entities -> entities.map { it.toDomain() } }
        .onStart { refreshFromRemote() }  // Trigger refresh
        .flowOn(ioDispatcher)

    private suspend fun refreshFromRemote() {
        try {
            val remote = api.getUsers()
            dao.replaceAll(remote.map { it.toEntity() })
        } catch (e: Exception) {
            // Silently fail — local data is still served
            Timber.w(e, "Failed to refresh users from remote")
        }
    }

    override suspend fun getUser(id: String): User = withContext(ioDispatcher) {
        // Try remote first, fall back to local
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

### Connectivity-Aware Sync
```kotlin
class SyncManager @Inject constructor(
    @ApplicationContext private val context: Context,
    private val repository: UserRepository,
) {
    private val connectivityManager = context.getSystemService<ConnectivityManager>()

    val isOnline: Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) { trySend(true) }
            override fun onLost(network: Network) { trySend(false) }
        }
        connectivityManager?.registerDefaultNetworkCallback(callback)
        awaitClose { connectivityManager?.unregisterNetworkCallback(callback) }
    }.distinctUntilChanged()
}
```



---
