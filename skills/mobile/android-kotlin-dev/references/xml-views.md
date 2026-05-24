# XML Views & View Binding Reference

## Table of Contents
1. View Binding Setup
2. Common XML Layouts
3. Fragment Patterns
4. RecyclerView with ListAdapter
5. Hybrid: XML + Compose
6. Migration Strategy

---

## 1. View Binding Setup

### Enable in build.gradle.kts
```kotlin
android {
    buildFeatures {
        viewBinding = true
    }
}
```

### Usage in Activity
```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.titleText.text = "Hello"
        binding.loginButton.setOnClickListener { login() }
    }
}
```

### Usage in Fragment
```kotlin
class HomeFragment : Fragment(R.layout.fragment_home) {
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)

        binding.recyclerView.adapter = adapter
        binding.swipeRefresh.setOnRefreshListener { viewModel.refresh() }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Prevent memory leaks
    }
}
```

---

## 2. Common XML Layouts

### ConstraintLayout (recommended for complex layouts)
```xml
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:padding="16dp">

    <ImageView
        android:id="@+id/avatar"
        android:layout_width="48dp"
        android:layout_height="48dp"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintTop_toTopOf="parent" />

    <TextView
        android:id="@+id/name"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:layout_marginStart="12dp"
        android:textAppearance="?attr/textAppearanceTitleMedium"
        app:layout_constraintStart_toEndOf="@id/avatar"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toTopOf="@id/avatar" />

    <TextView
        android:id="@+id/subtitle"
        android:layout_width="0dp"
        android:layout_height="wrap_content"
        android:textAppearance="?attr/textAppearanceBodyMedium"
        app:layout_constraintStart_toStartOf="@id/name"
        app:layout_constraintEnd_toEndOf="parent"
        app:layout_constraintTop_toBottomOf="@id/name" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

### MaterialCardView
```xml
<com.google.android.material.card.MaterialCardView
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:cardElevation="2dp"
    app:cardCornerRadius="12dp"
    android:layout_margin="8dp">

    <LinearLayout
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:orientation="vertical"
        android:padding="16dp">
        <!-- Content -->
    </LinearLayout>
</com.google.android.material.card.MaterialCardView>
```

---

## 3. Fragment Patterns

### Fragment with ViewModel and ViewBinding
```kotlin
@AndroidEntryPoint
class HomeFragment : Fragment(R.layout.fragment_home) {
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    private val viewModel: HomeViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentHomeBinding.bind(view)

        setupRecyclerView()
        observeState()
    }

    private fun setupRecyclerView() {
        binding.recyclerView.apply {
            adapter = userAdapter
            layoutManager = LinearLayoutManager(requireContext())
            addItemDecoration(DividerItemDecoration(requireContext(), DividerItemDecoration.VERTICAL))
        }
    }

    private fun observeState() {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    when (state) {
                        is UiState.Loading -> binding.progressBar.isVisible = true
                        is UiState.Success -> {
                            binding.progressBar.isVisible = false
                            userAdapter.submitList(state.data)
                        }
                        is UiState.Error -> {
                            binding.progressBar.isVisible = false
                            Snackbar.make(binding.root, state.message, Snackbar.LENGTH_LONG).show()
                        }
                    }
                }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
```

### Fragment Navigation (Navigation Component)
```kotlin
// Navigate with Safe Args
findNavController().navigate(HomeFragmentDirections.actionHomeToDetail(userId = user.id))

// Navigate with popBackStack
findNavController().popBackStack()

// Navigate and clear back stack
findNavController().navigate(R.id.loginFragment) {
    popUpTo(R.id.nav_graph) { inclusive = true }
}
```

---

## 4. RecyclerView with ListAdapter

```kotlin
class UserAdapter(
    private val onItemClick: (User) -> Unit,
) : ListAdapter<User, UserAdapter.ViewHolder>(UserDiffCallback()) {

    inner class ViewHolder(private val binding: ItemUserBinding) : RecyclerView.ViewHolder(binding.root) {
        fun bind(user: User) {
            binding.nameText.text = user.name
            binding.emailText.text = user.email
            binding.root.setOnClickListener { onItemClick(user) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val binding = ItemUserBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return ViewHolder(binding)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(old: User, new: User) = old.id == new.id
    override fun areContentsTheSame(old: User, new: User) = old == new
}
```

---

## 5. Hybrid: XML + Compose

### Compose inside Fragment (ComposeView)
```kotlin
class ProfileFragment : Fragment() {
    private val viewModel: ProfileViewModel by viewModels()

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View {
        return ComposeView(requireContext()).apply {
            setViewCompositionStrategy(ViewCompositionStrategy.DisposeOnViewTreeLifecycleDestroyed)
            setContent {
                MaterialTheme {
                    ProfileScreen(viewModel = viewModel)
                }
            }
        }
    }
}
```

### Compose inside XML Layout
```xml
<LinearLayout ...>
    <TextView android:id="@+id/title" ... />
    <androidx.compose.ui.platform.ComposeView
        android:id="@+id/composeContainer"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>
```

```kotlin
binding.composeContainer.setContent {
    MaterialTheme { ChartComposable(data = chartData) }
}
```

### XML View inside Compose (AndroidView)
```kotlin
@Composable
fun MapViewComposable(location: LatLng) {
    AndroidView(
        factory = { context ->
            MapView(context).apply { /* setup */ }
        },
        update = { mapView ->
            mapView.moveCamera(location)
        },
        modifier = Modifier.fillMaxWidth().height(300.dp),
    )
}
```

---

## 6. Migration Strategy

### Recommended Approach: Incremental (Bottom-Up)

1. **Start with leaves**: Replace simple, self-contained views first (buttons, cards, list items)
2. **Replace screens**: Convert entire screens to Compose, one at a time
3. **Keep Fragments as shells**: Fragment just hosts `ComposeView`, all UI logic in Compose
4. **Replace Navigation last**: Migrate to Navigation Compose once most screens are Compose
5. **Remove XML**: Delete XML layouts as they're replaced

### Migration Priority
```
High priority to migrate:        Low priority (keep XML):
- New features (always Compose)   - Stable, rarely-changed screens
- Screens under active development - Screens with complex custom views
- Simple list/detail screens      - Screens heavily dependent on XML libraries
- Settings/Profile screens        - WebView-heavy screens
```



---

<!-- Script: scripts/scaffold_android_project.py -->

# Script: scaffold_android_project.py

```python
#!/usr/bin/env python3
"""
Generate Android project scaffolding with proper file structure, boilerplate Kotlin code,
Gradle configuration, and Hilt DI setup.

Usage:
    python scaffold_android_project.py --config project.json --output ./MyApp

Config JSON:
{
    "project_name": "MyApp",
    "package_name": "com.example.myapp",
    "min_sdk": 26,
    "target_sdk": 35,
    "architecture": "mvvm",
    "features": ["home", "auth", "settings"],
    "use_compose": true,
    "use_room": true,
    "use_retrofit": true,
    "use_hilt": true,
    "use_datastore": true,
    "include_tests": true,
    "multi_module": false
}
"""

import json
import sys
import os
import argparse


def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Created: {path}")


def pkg_to_path(package_name):
    return package_name.replace(".", "/")


def generate_application_class(config):
    pkg = config["package_name"]
    name = config["project_name"]
    hilt = "@HiltAndroidApp\n" if config.get("use_hilt") else ""
    hilt_import = "import dagger.hilt.android.HiltAndroidApp\n" if config.get("use_hilt") else ""
    return f"""package {pkg}

import android.app.Application
{hilt_import}
{hilt}class {name}Application : Application()
"""


def generate_main_activity(config):
    pkg = config["package_name"]
    hilt = "@AndroidEntryPoint\n" if config.get("use_hilt") else ""
    hilt_import = "import dagger.hilt.android.AndroidEntryPoint\n" if config.get("use_hilt") else ""
    nav_import = f"import {pkg}.ui.navigation.AppNavigation\n" if config.get("use_compose") else ""

    if config.get("use_compose"):
        return f"""package {pkg}

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
{hilt_import}import {pkg}.ui.theme.{config["project_name"]}Theme
{nav_import}
{hilt}class MainActivity : ComponentActivity() {{
    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {{
            {config["project_name"]}Theme {{
                AppNavigation()
            }}
        }}
    }}
}}
"""
    else:
        return f"""package {pkg}

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
{hilt_import}import {pkg}.databinding.ActivityMainBinding

{hilt}class MainActivity : AppCompatActivity() {{
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {{
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }}
}}
"""


def generate_nav(config):
    pkg = config["package_name"]
    features = config.get("features", ["home"])
    imports = "\n".join(f"import {pkg}.ui.{f}.{f.title()}Screen" for f in features)

    routes = "\n".join(f'    @Serializable data object {f.title()} : Route' for f in features)
    destinations = ""
    for f in features:
        hilt_vm = f"viewModel: {f.title()}ViewModel = hiltViewModel()" if config.get("use_hilt") else ""
        destinations += f"""
            composable<Route.{f.title()}> {{
                {f.title()}Screen()
            }}"""

    return f"""package {pkg}.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import kotlinx.serialization.Serializable
{imports}

sealed interface Route {{
{routes}
}}

@Composable
fun AppNavigation() {{
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Route.{features[0].title()}) {{{destinations}
    }}
}}
"""


def generate_theme(config):
    pkg = config["package_name"]
    name = config["project_name"]
    return f"""package {pkg}.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.platform.LocalContext

private val DarkColorScheme = darkColorScheme()
private val LightColorScheme = lightColorScheme()

@Composable
fun {name}Theme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = true,
    content: @Composable () -> Unit,
) {{
    val colorScheme = when {{
        dynamicColor -> {{
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }}
        darkTheme -> DarkColorScheme
        else -> LightColorScheme
    }}

    MaterialTheme(colorScheme = colorScheme, content = content)
}}
"""


def generate_ui_state(config):
    pkg = config["package_name"]
    return f"""package {pkg}.util

sealed interface UiState<out T> {{
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val cause: Throwable? = null) : UiState<Nothing>
}}
"""


def generate_resource(config):
    pkg = config["package_name"]
    return f"""package {pkg}.util

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.catch
import kotlinx.coroutines.flow.map
import kotlinx.coroutines.flow.onStart

sealed interface Resource<out T> {{
    data class Success<T>(val data: T) : Resource<T>
    data class Error(val message: String, val cause: Throwable? = null) : Resource<Nothing>
    data object Loading : Resource<Nothing>
}}

fun <T> Flow<T>.asResource(): Flow<Resource<T>> = this
    .map<T, Resource<T>> {{ Resource.Success(it) }}
    .onStart {{ emit(Resource.Loading) }}
    .catch {{ emit(Resource.Error(it.message ?: "Unknown error", it)) }}
"""


def generate_feature_screen(feature, config):
    pkg = config["package_name"]
    title = feature.title()
    hilt_vm = ""
    hilt_import = ""
    vm_param = ""
    state_code = ""
    content_code = f'Text("{title}", style = MaterialTheme.typography.headlineMedium)'

    if config.get("use_hilt"):
        hilt_import = "import androidx.hilt.navigation.compose.hiltViewModel\n"
        vm_param = f"viewModel: {title}ViewModel = hiltViewModel(),"
        state_code = f"""    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
"""
        content_code = f"""when (uiState) {{
                is UiState.Loading -> CircularProgressIndicator()
                is UiState.Success -> Text("{title} loaded", style = MaterialTheme.typography.headlineMedium)
                is UiState.Error -> Text("Error: ${{(uiState as UiState.Error).message}}")
            }}"""

    return f"""package {pkg}.ui.{feature}

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
{hilt_import}import {pkg}.util.UiState

@Composable
fun {title}Screen(
    {vm_param}
) {{
{state_code}
    Scaffold {{ padding ->
        Box(
            modifier = Modifier.fillMaxSize().padding(padding),
            contentAlignment = Alignment.Center,
        ) {{
            {content_code}
        }}
    }}
}}
"""


def generate_feature_viewmodel(feature, config):
    pkg = config["package_name"]
    title = feature.title()
    hilt_inject = "@HiltViewModel\n" if config.get("use_hilt") else ""
    hilt_import = "import dagger.hilt.android.lifecycle.HiltViewModel\nimport javax.inject.Inject\n" if config.get("use_hilt") else ""
    inject = " @Inject constructor()" if config.get("use_hilt") else "()"

    return f"""package {pkg}.ui.{feature}

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
{hilt_import}import {pkg}.util.UiState

{hilt_inject}class {title}ViewModel{inject} : ViewModel() {{

    private val _uiState = MutableStateFlow<UiState<List<String>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<String>>> = _uiState.asStateFlow()

    init {{
        load()
    }}

    private fun load() {{
        viewModelScope.launch {{
            _uiState.value = UiState.Loading
            // TODO: Load data from repository
            _uiState.value = UiState.Success(emptyList())
        }}
    }}

    fun refresh() = load()
}}
"""


def generate_hilt_modules(config):
    pkg = config["package_name"]
    modules = {}

    if config.get("use_retrofit"):
        modules["NetworkModule"] = f"""package {pkg}.di

import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {{

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient =
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor().apply {{
                level = HttpLoggingInterceptor.Level.BODY
            }})
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
}}
"""

    if config.get("use_room"):
        modules["DatabaseModule"] = f"""package {pkg}.di

import android.content.Context
import androidx.room.Room
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

// TODO: Import your AppDatabase class
// import {pkg}.data.local.AppDatabase

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {{

    // @Provides
    // @Singleton
    // fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
    //     Room.databaseBuilder(context, AppDatabase::class.java, "app_db")
    //         .fallbackToDestructiveMigration()
    //         .build()
}}
"""

    return modules


def generate_build_gradle(config):
    pkg = config["package_name"]
    name = config["project_name"]
    min_sdk = config.get("min_sdk", 26)
    target_sdk = config.get("target_sdk", 35)

    plugins = ['    alias(libs.plugins.android.application)', '    alias(libs.plugins.kotlin.android)']
    if config.get("use_compose"):
        plugins.append('    alias(libs.plugins.kotlin.compose)')
    if config.get("use_hilt"):
        plugins.append('    alias(libs.plugins.hilt)')
        plugins.append('    alias(libs.plugins.ksp)')
    plugins_str = "\n".join(plugins)

    deps = [
        '    // Core',
        '    implementation(libs.androidx.core.ktx)',
        '    implementation(libs.lifecycle.viewmodel)',
        '    implementation(libs.lifecycle.runtime)',
        '    implementation(libs.coroutines.android)',
    ]

    if config.get("use_compose"):
        deps.extend([
            '',
            '    // Compose',
            '    implementation(platform(libs.compose.bom))',
            '    implementation(libs.compose.ui)',
            '    implementation(libs.compose.material3)',
            '    implementation(libs.compose.tooling.preview)',
            '    implementation(libs.navigation.compose)',
            '    debugImplementation("androidx.compose.ui:ui-tooling")',
        ])

    if config.get("use_hilt"):
        deps.extend([
            '',
            '    // Hilt',
            '    implementation(libs.hilt.android)',
            '    ksp(libs.hilt.compiler)',
            '    implementation(libs.hilt.navigation)',
        ])

    if config.get("use_retrofit"):
        deps.extend([
            '',
            '    // Networking',
            '    implementation(libs.retrofit)',
            '    implementation(libs.retrofit.gson)',
            '    implementation(libs.okhttp.logging)',
        ])

    if config.get("use_room"):
        deps.extend([
            '',
            '    // Room',
            '    implementation(libs.room.runtime)',
            '    implementation(libs.room.ktx)',
            '    ksp(libs.room.compiler)',
        ])

    if config.get("use_datastore"):
        deps.extend([
            '',
            '    // DataStore',
            '    implementation(libs.datastore.preferences)',
        ])

    deps.extend([
        '',
        '    // Testing',
        '    testImplementation("junit:junit:4.13.2")',
        '    testImplementation(libs.coroutines.test)',
        '    androidTestImplementation("androidx.test.ext:junit:1.2.1")',
    ])

    deps_str = "\n".join(deps)
    compose_block = """
    buildFeatures {
        compose = true
    }""" if config.get("use_compose") else ""

    return f"""plugins {{
{plugins_str}
    kotlin("plugin.serialization") version libs.versions.kotlin
}}

android {{
    namespace = "{pkg}"
    compileSdk = {target_sdk}

    defaultConfig {{
        applicationId = "{pkg}"
        minSdk = {min_sdk}
        targetSdk = {target_sdk}
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }}

    buildTypes {{
        release {{
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }}
    }}
{compose_block}
    compileOptions {{
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }}
    kotlinOptions {{
        jvmTarget = "17"
    }}
}}

dependencies {{
{deps_str}
}}
"""


def generate_manifest(config):
    pkg = config["package_name"]
    name = config["project_name"]
    return f"""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:name=".{name}Application"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.{name}">
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.{name}">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
"""


def generate_strings(config):
    return f"""<resources>
    <string name="app_name">{config["project_name"]}</string>
</resources>
"""


def generate_unit_test(feature, config):
    pkg = config["package_name"]
    title = feature.title()
    return f"""package {pkg}.ui.{feature}

import {pkg}.util.UiState
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Test

class {title}ViewModelTest {{

    @Test
    fun `initial state is loading`() = runTest {{
        val viewModel = {title}ViewModel()
        // Verify initial state
        // assertEquals(UiState.Loading, viewModel.uiState.value)
    }}
}}
"""


def scaffold_project(config, output_dir):
    name = config["project_name"]
    pkg = config["package_name"]
    pkg_path = pkg_to_path(pkg)
    features = config.get("features", ["home"])
    base = os.path.join(output_dir, name)
    src = os.path.join(base, "app", "src", "main", "java", pkg_path)
    res = os.path.join(base, "app", "src", "main", "res")

    print(f"\n🤖 Scaffolding {name} (Android + Kotlin)\n")

    # App class & Activity
    create_file(os.path.join(src, f"{name}Application.kt"), generate_application_class(config))
    create_file(os.path.join(src, "MainActivity.kt"), generate_main_activity(config))

    # Navigation
    if config.get("use_compose"):
        create_file(os.path.join(src, "ui", "navigation", "AppNavigation.kt"), generate_nav(config))
        create_file(os.path.join(src, "ui", "theme", "Theme.kt"), generate_theme(config))

    # Utilities
    create_file(os.path.join(src, "util", "UiState.kt"), generate_ui_state(config))
    create_file(os.path.join(src, "util", "Resource.kt"), generate_resource(config))

    # Features
    for feature in features:
        create_file(os.path.join(src, "ui", feature, f"{feature.title()}Screen.kt"), generate_feature_screen(feature, config))
        create_file(os.path.join(src, "ui", feature, f"{feature.title()}ViewModel.kt"), generate_feature_viewmodel(feature, config))

    # Hilt modules
    if config.get("use_hilt"):
        modules = generate_hilt_modules(config)
        for module_name, content in modules.items():
            create_file(os.path.join(src, "di", f"{module_name}.kt"), content)

    # Manifest & Resources
    create_file(os.path.join(base, "app", "src", "main", "AndroidManifest.xml"), generate_manifest(config))
    create_file(os.path.join(res, "values", "strings.xml"), generate_strings(config))

    # Gradle
    create_file(os.path.join(base, "app", "build.gradle.kts"), generate_build_gradle(config))

    # Tests
    if config.get("include_tests"):
        test_src = os.path.join(base, "app", "src", "test", "java", pkg_path)
        for feature in features:
            create_file(os.path.join(test_src, "ui", feature, f"{feature.title()}ViewModelTest.kt"),
                        generate_unit_test(feature, config))

    # Gitignore
    create_file(os.path.join(output_dir, ".gitignore"), """# Android
*.iml
.gradle/
build/
local.properties
.idea/
*.apk
*.aab

# Kotlin
*.class
""")

    print(f"\n✅ Project scaffolded at: {base}")
    print(f"   Package: {pkg}")
    print(f"   Features: {', '.join(f.title() for f in features)}")
    print(f"   Compose: {'Yes' if config.get('use_compose') else 'No'}")
    print(f"   Hilt: {'Yes' if config.get('use_hilt') else 'No'}")
    print(f"   Room: {'Yes' if config.get('use_room') else 'No'}")
    print(f"   Retrofit: {'Yes' if config.get('use_retrofit') else 'No'}")


def main():
    parser = argparse.ArgumentParser(description="Scaffold Android Project")
    parser.add_argument("--config", help="JSON config path")
    parser.add_argument("--output", default=".", help="Output directory")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
    else:
        config = json.load(sys.stdin)

    scaffold_project(config, args.output)


if __name__ == "__main__":
    main()

```
