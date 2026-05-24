# Jetpack Compose UI Reference

## Table of Contents
1. Compose Essentials
2. Layout System
3. Navigation
4. Material 3 Components
5. State Management
6. Custom Components
7. Animations
8. Performance

---

## 1. Compose Essentials

### Composable Lifecycle
```kotlin
@Composable
fun MyScreen() {
    // Runs on every recomposition — keep cheap
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        // Runs once when composable enters composition
        // Canceled when composable leaves composition
        viewModel.loadData()
    }

    LaunchedEffect(searchQuery) {
        // Re-launches when searchQuery changes
        delay(300) // debounce
        viewModel.search(searchQuery)
    }

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event -> /* ... */ }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    SideEffect {
        // Runs after every successful recomposition
        analytics.trackScreenView("MyScreen")
    }
}
```

### State in Compose

| API | Use Case |
|-----|----------|
| `remember { }` | Cache computation across recompositions |
| `remember { mutableStateOf() }` | Local mutable UI state |
| `rememberSaveable { }` | Survives configuration changes |
| `derivedStateOf { }` | Computed state that only recomposes when result changes |
| `collectAsStateWithLifecycle()` | Collect Flow as Compose State (lifecycle-aware) |
| `produceState` | Convert non-Compose state source into Compose State |

```kotlin
// Local state
var text by remember { mutableStateOf("") }
var expanded by rememberSaveable { mutableStateOf(false) }

// Derived state (avoids recomposition when list changes but firstVisible doesn't)
val showButton by remember { derivedStateOf { listState.firstVisibleItemIndex > 0 } }

// Flow → State (PREFERRED for ViewModels)
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

---

## 2. Layout System

### Column / Row / Box
```kotlin
Column(
    modifier = Modifier.fillMaxSize().padding(16.dp),
    verticalArrangement = Arrangement.spacedBy(12.dp),
    horizontalAlignment = Alignment.CenterHorizontally,
) {
    Text("Title", style = MaterialTheme.typography.headlineMedium)
    Text("Subtitle", style = MaterialTheme.typography.bodyMedium)
}

Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically,
) {
    Text("Label")
    Switch(checked = enabled, onCheckedChange = { enabled = it })
}
```

### LazyColumn / LazyRow (RecyclerView equivalent)
```kotlin
LazyColumn(
    contentPadding = PaddingValues(16.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp),
) {
    items(items = users, key = { it.id }) { user ->
        UserCard(user = user, onClick = { onUserClick(user.id) })
    }
}
```

### LazyVerticalGrid
```kotlin
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 150.dp),
    contentPadding = PaddingValues(16.dp),
    horizontalArrangement = Arrangement.spacedBy(8.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp),
) {
    items(products) { product -> ProductCard(product) }
}
```

### Modifier Chain (order matters)
```kotlin
Modifier
    .fillMaxWidth()
    .padding(16.dp)          // Padding OUTSIDE the background
    .background(MaterialTheme.colorScheme.surface, RoundedCornerShape(12.dp))
    .padding(16.dp)          // Padding INSIDE the background
    .clickable { onClick() }
```

### ConstraintLayout (complex layouts)
```kotlin
ConstraintLayout(modifier = Modifier.fillMaxWidth()) {
    val (image, title, subtitle, button) = createRefs()

    AsyncImage(
        model = imageUrl,
        modifier = Modifier.constrainAs(image) {
            top.linkTo(parent.top)
            start.linkTo(parent.start)
            width = Dimension.value(80.dp)
            height = Dimension.value(80.dp)
        }
    )
    // ...
}
```

---

## 3. Navigation

### Navigation Compose (Type-safe — recommended)

```kotlin
// Define routes as serializable classes
@Serializable data object Home
@Serializable data class Detail(val itemId: String)
@Serializable data object Settings

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Home) {
        composable<Home> {
            HomeScreen(
                onItemClick = { id -> navController.navigate(Detail(itemId = id)) },
                onSettingsClick = { navController.navigate(Settings) },
            )
        }
        composable<Detail> { backStackEntry ->
            val detail: Detail = backStackEntry.toRoute()
            DetailScreen(itemId = detail.itemId, onBack = { navController.popBackStack() })
        }
        composable<Settings> {
            SettingsScreen(onBack = { navController.popBackStack() })
        }
    }
}
```

### Bottom Navigation
```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val currentBackStackEntry by navController.currentBackStackEntryAsState()

    Scaffold(
        bottomBar = {
            NavigationBar {
                TopLevelRoute.entries.forEach { route ->
                    NavigationBarItem(
                        selected = currentBackStackEntry?.destination?.route == route.route,
                        onClick = {
                            navController.navigate(route.destination) {
                                popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        icon = { Icon(route.icon, contentDescription = route.label) },
                        label = { Text(route.label) },
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(navController, startDestination = Home, modifier = Modifier.padding(innerPadding)) {
            composable<Home> { HomeScreen() }
            composable<Search> { SearchScreen() }
            composable<Profile> { ProfileScreen() }
        }
    }
}
```

---

## 4. Material 3 Components

```kotlin
// Top App Bar
TopAppBar(
    title = { Text("Home") },
    navigationIcon = { IconButton(onClick = onBack) { Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back") } },
    actions = { IconButton(onClick = {}) { Icon(Icons.Default.MoreVert, "Menu") } },
)

// Cards
ElevatedCard(modifier = Modifier.fillMaxWidth()) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text("Title", style = MaterialTheme.typography.titleMedium)
        Text("Description", style = MaterialTheme.typography.bodyMedium)
    }
}

// Buttons
Button(onClick = {}) { Text("Primary") }
OutlinedButton(onClick = {}) { Text("Secondary") }
TextButton(onClick = {}) { Text("Tertiary") }
FilledTonalButton(onClick = {}) { Text("Tonal") }
FloatingActionButton(onClick = {}) { Icon(Icons.Default.Add, "Add") }

// Text Fields
OutlinedTextField(
    value = text,
    onValueChange = { text = it },
    label = { Text("Email") },
    leadingIcon = { Icon(Icons.Default.Email, null) },
    isError = emailError != null,
    supportingText = emailError?.let { { Text(it) } },
    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email, imeAction = ImeAction.Next),
    singleLine = true,
)

// Bottom Sheet
ModalBottomSheet(onDismissRequest = onDismiss, sheetState = sheetState) {
    Column(modifier = Modifier.padding(16.dp)) { /* content */ }
}

// Dialogs
AlertDialog(
    onDismissRequest = onDismiss,
    title = { Text("Confirm Delete") },
    text = { Text("Are you sure?") },
    confirmButton = { TextButton(onClick = onConfirm) { Text("Delete") } },
    dismissButton = { TextButton(onClick = onDismiss) { Text("Cancel") } },
)

// Pull-to-Refresh
PullToRefreshBox(isRefreshing = isRefreshing, onRefresh = onRefresh) {
    LazyColumn { /* content */ }
}
```

---

## 5. State Management

### Unidirectional Data Flow

```
User Action → ViewModel (process) → State (emit) → UI (recompose)
```

```kotlin
// State
data class HomeUiState(
    val items: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val searchQuery: String = "",
)

// Events (user actions)
sealed interface HomeEvent {
    data object LoadItems : HomeEvent
    data object Refresh : HomeEvent
    data class Search(val query: String) : HomeEvent
    data class DeleteItem(val id: String) : HomeEvent
}

// ViewModel
@HiltViewModel
class HomeViewModel @Inject constructor(
    private val repository: ItemRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    fun onEvent(event: HomeEvent) {
        when (event) {
            is HomeEvent.LoadItems -> loadItems()
            is HomeEvent.Refresh -> loadItems()
            is HomeEvent.Search -> search(event.query)
            is HomeEvent.DeleteItem -> deleteItem(event.id)
        }
    }

    private fun loadItems() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.getItems()
                .catch { e -> _uiState.update { it.copy(isLoading = false, error = e.message) } }
                .collect { items -> _uiState.update { it.copy(isLoading = false, items = items) } }
        }
    }
}

// Screen
@Composable
fun HomeScreen(viewModel: HomeViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeContent(uiState = uiState, onEvent = viewModel::onEvent)
}
```

---

## 6. Custom Components

### Reusable Composable Pattern
```kotlin
@Composable
fun PrimaryButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,   // Always accept Modifier
    enabled: Boolean = true,
    isLoading: Boolean = false,
) {
    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth().height(48.dp),
        enabled = enabled && !isLoading,
    ) {
        if (isLoading) {
            CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp, color = MaterialTheme.colorScheme.onPrimary)
        } else {
            Text(text)
        }
    }
}
```

### Async Image Loading (Coil)
```kotlin
AsyncImage(
    model = ImageRequest.Builder(LocalContext.current)
        .data(imageUrl)
        .crossfade(true)
        .placeholder(R.drawable.placeholder)
        .error(R.drawable.error)
        .build(),
    contentDescription = "User avatar",
    contentScale = ContentScale.Crop,
    modifier = Modifier.size(48.dp).clip(CircleShape),
)
```

---

## 7. Animations

```kotlin
// Animate visibility
AnimatedVisibility(visible = isVisible, enter = fadeIn() + slideInVertically(), exit = fadeOut()) {
    Card { /* content */ }
}

// Animate content changes
AnimatedContent(targetState = uiState, transitionSpec = { fadeIn() togetherWith fadeOut() }) { state ->
    when (state) {
        is UiState.Loading -> LoadingIndicator()
        is UiState.Success -> ContentList(state.data)
        is UiState.Error -> ErrorScreen(state.message)
    }
}

// Animate values
val alpha by animateFloatAsState(targetValue = if (selected) 1f else 0.5f, label = "alpha")
val size by animateDpAsState(targetValue = if (expanded) 200.dp else 100.dp, label = "size")
val color by animateColorAsState(targetValue = if (active) Color.Green else Color.Gray, label = "color")
```

---

## 8. Performance

### Stability & Recomposition
```kotlin
// Use Immutable collections to prevent unnecessary recomposition
@Immutable
data class UserList(val users: List<User>)

// Use key parameter in LazyColumn
items(users, key = { it.id }) { user -> UserCard(user) }

// Use derivedStateOf for expensive computations
val showScrollToTop by remember { derivedStateOf { lazyListState.firstVisibleItemIndex > 5 } }

// Use remember with keys for expensive operations
val sortedItems = remember(items, sortOrder) { items.sortedBy { /* ... */ } }
```

### Common Performance Pitfalls
- Creating lambdas inside composables → use `remember` or method references
- Reading state in unnecessary scopes → use `derivedStateOf`
- Large recomposition scopes → extract smaller composables
- Not using `key` in `LazyColumn` → causes unnecessary recompositions
- Heavy computation in composition → move to ViewModel



---
