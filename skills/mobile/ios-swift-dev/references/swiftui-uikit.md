# SwiftUI & UIKit Reference

## Table of Contents
1. SwiftUI Essentials
2. Navigation Patterns
3. Layout System
4. Custom Components
5. UIKit Integration
6. Animations & Transitions
7. Accessibility

---

## 1. SwiftUI Essentials

### View Lifecycle
```swift
struct MyView: View {
    var body: some View {
        Text("Hello")
            .onAppear { /* View appeared */ }
            .onDisappear { /* View disappeared */ }
            .task { /* Async work when view appears, canceled on disappear */ }
            .task(id: someValue) { /* Re-runs when someValue changes */ }
            .onChange(of: someValue) { oldValue, newValue in /* React to changes */ }
    }
}
```

### State Management (iOS 17+)

| Property Wrapper | Use Case | Owns Data? |
|-----------------|----------|-----------|
| `@State` | Simple view-local state | Yes |
| `@Binding` | Two-way connection to parent's state | No (reference) |
| `@Observable` class | Complex state / ViewModel | N/A (macro) |
| `@Environment` | Injected values (colorScheme, dismiss) | No |
| `@AppStorage` | UserDefaults-backed state | Yes |
| `@SceneStorage` | Scene-level state restoration | Yes |

### State Management (iOS 16 and below)

| Property Wrapper | Use Case |
|-----------------|----------|
| `@StateObject` | Create and own an ObservableObject |
| `@ObservedObject` | Reference an ObservableObject from parent |
| `@EnvironmentObject` | Injected ObservableObject via environment |
| `@Published` | Property in ObservableObject that triggers updates |

### Common Views

```swift
// Text
Text("Hello").font(.title).foregroundStyle(.primary)
Text(date, format: .dateTime.month().day())
Text(price, format: .currency(code: "USD"))

// Images
Image(systemName: "star.fill").foregroundStyle(.yellow)
AsyncImage(url: imageURL) { image in image.resizable() } placeholder: { ProgressView() }

// Inputs
TextField("Email", text: $email).textContentType(.emailAddress).keyboardType(.emailAddress)
SecureField("Password", text: $password).textContentType(.password)
Toggle("Enable notifications", isOn: $notificationsEnabled)
Picker("Sort by", selection: $sortOption) { ForEach(SortOption.allCases) { Text($0.name) } }
DatePicker("Date", selection: $date, displayedComponents: .date)
Slider(value: $volume, in: 0...1)

// Lists
List(items) { item in ItemRow(item: item) }.listStyle(.insetGrouped)
List { ForEach(items) { item in ... }.onDelete(perform: delete).onMove(perform: move) }

// Buttons & Actions
Button("Save") { save() }.buttonStyle(.borderedProminent)
Button(role: .destructive) { delete() } label: { Label("Delete", systemImage: "trash") }
Menu("Options") { Button("Edit") {}; Button("Share") {} }
```

---

## 2. Navigation Patterns

### NavigationStack (iOS 16+) — Preferred

```swift
// Value-based navigation
struct ContentView: View {
    @State private var path = NavigationPath()
    
    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: item) {
                    ItemRow(item: item)
                }
            }
            .navigationDestination(for: Item.self) { item in
                ItemDetailView(item: item)
            }
            .navigationDestination(for: Category.self) { category in
                CategoryView(category: category)
            }
        }
    }
    
    func navigateTo(_ item: Item) {
        path.append(item)
    }
    
    func popToRoot() {
        path = NavigationPath()
    }
}
```

### TabView

```swift
struct MainTabView: View {
    @State private var selectedTab = Tab.home
    
    var body: some View {
        TabView(selection: $selectedTab) {
            Tab("Home", systemImage: "house", value: .home) {
                HomeView()
            }
            Tab("Search", systemImage: "magnifyingglass", value: .search) {
                SearchView()
            }
            Tab("Profile", systemImage: "person", value: .profile) {
                ProfileView()
            }
        }
    }
}
```

### Sheet / Full Screen Cover / Popover

```swift
struct ParentView: View {
    @State private var showSheet = false
    @State private var showFullScreen = false
    @State private var detailItem: Item?
    
    var body: some View {
        VStack {
            Button("Show Sheet") { showSheet = true }
            Button("Show Full Screen") { showFullScreen = true }
            Button("Show Detail") { detailItem = items.first }
        }
        .sheet(isPresented: $showSheet) { SheetView() }
        .fullScreenCover(isPresented: $showFullScreen) { FullScreenView() }
        .sheet(item: $detailItem) { item in DetailView(item: item) }
    }
}
```

### Coordinator Pattern (for complex navigation)

```swift
@Observable
final class AppCoordinator {
    var path = NavigationPath()
    var sheet: Sheet?
    var fullScreenCover: FullScreenCover?
    
    enum Sheet: Identifiable {
        case settings
        case addItem
        var id: Int { hashValue }
    }
    
    func navigate(to destination: any Hashable) { path.append(destination) }
    func popToRoot() { path = NavigationPath() }
    func present(_ sheet: Sheet) { self.sheet = sheet }
    func dismissSheet() { sheet = nil }
}
```

---

## 3. Layout System

### VStack / HStack / ZStack
```swift
VStack(alignment: .leading, spacing: 12) {
    Text("Title").font(.headline)
    Text("Subtitle").font(.subheadline).foregroundStyle(.secondary)
}
```

### LazyVGrid / LazyHGrid
```swift
let columns = [GridItem(.adaptive(minimum: 150, maximum: 200))]
LazyVGrid(columns: columns, spacing: 16) {
    ForEach(items) { item in CardView(item: item) }
}
```

### GeometryReader (use sparingly)
```swift
GeometryReader { geometry in
    VStack {
        Image("hero").resizable().frame(height: geometry.size.height * 0.4)
        // ...
    }
}
```

### ViewThatFits (iOS 16+)
```swift
ViewThatFits {
    HStack { content } // Try horizontal first
    VStack { content } // Fall back to vertical
}
```

### Custom Layout (iOS 16+)
```swift
struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        // Calculate required size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        // Position each subview
    }
}
```

---

## 4. Custom Components

### Reusable Button Style
```swift
struct PrimaryButtonStyle: ButtonStyle {
    @Environment(\.isEnabled) private var isEnabled
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(isEnabled ? Color.accentColor : Color.gray, in: .capsule)
            .opacity(configuration.isPressed ? 0.8 : 1.0)
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .animation(.easeInOut(duration: 0.15), value: configuration.isPressed)
    }
}

extension ButtonStyle where Self == PrimaryButtonStyle {
    static var primary: PrimaryButtonStyle { PrimaryButtonStyle() }
}
// Usage: Button("Sign In") { ... }.buttonStyle(.primary)
```

### Reusable View Modifier
```swift
struct CardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.regularMaterial, in: .rect(cornerRadius: 12))
            .shadow(color: .black.opacity(0.08), radius: 8, y: 4)
    }
}
extension View {
    func cardStyle() -> some View { modifier(CardModifier()) }
}
```

### Loading State View
```swift
enum LoadingState<T> {
    case idle
    case loading
    case loaded(T)
    case error(AppError)
}

struct LoadingStateView<T, Content: View, EmptyContent: View>: View {
    let state: LoadingState<T>
    let content: (T) -> Content
    let emptyContent: () -> EmptyContent
    let retry: (() async -> Void)?
    
    var body: some View {
        switch state {
        case .idle: Color.clear
        case .loading: ProgressView()
        case .loaded(let data): content(data)
        case .error(let error):
            ContentUnavailableView {
                Label("Error", systemImage: "exclamationmark.triangle")
            } description: {
                Text(error.localizedDescription)
            } actions: {
                if let retry { Button("Retry") { Task { await retry() } } }
            }
        }
    }
}
```

---

## 5. UIKit Integration

### UIViewRepresentable (Wrapping UIKit in SwiftUI)
```swift
struct MapView: UIViewRepresentable {
    let coordinate: CLLocationCoordinate2D
    
    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        mapView.delegate = context.coordinator
        return mapView
    }
    
    func updateUIView(_ mapView: MKMapView, context: Context) {
        let region = MKCoordinateRegion(center: coordinate, latitudinalMeters: 1000, longitudinalMeters: 1000)
        mapView.setRegion(region, animated: true)
    }
    
    func makeCoordinator() -> Coordinator { Coordinator() }
    
    class Coordinator: NSObject, MKMapViewDelegate { /* delegate methods */ }
}
```

### UIViewControllerRepresentable (Wrapping UIKit VCs)
```swift
struct ImagePicker: UIViewControllerRepresentable {
    @Binding var image: UIImage?
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator { Coordinator(self) }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker
        init(_ parent: ImagePicker) { self.parent = parent }
        
        func imagePickerController(_ picker: UIImagePickerController,
                                   didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            parent.image = info[.originalImage] as? UIImage
            parent.dismiss()
        }
    }
}
```

### Hosting SwiftUI in UIKit
```swift
// In a UIViewController
let swiftUIView = MySwiftUIView(viewModel: viewModel)
let hostingController = UIHostingController(rootView: swiftUIView)
addChild(hostingController)
view.addSubview(hostingController.view)
hostingController.view.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    hostingController.view.topAnchor.constraint(equalTo: view.topAnchor),
    hostingController.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
    hostingController.view.trailingAnchor.constraint(equalTo: view.trailingAnchor),
    hostingController.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
])
hostingController.didMove(toParent: self)
```

---

## 6. Animations & Transitions

```swift
// Implicit animation
Text("Hello")
    .scaleEffect(isAnimating ? 1.2 : 1.0)
    .animation(.spring(response: 0.4, dampingFraction: 0.6), value: isAnimating)

// Explicit animation
withAnimation(.easeInOut(duration: 0.3)) { showDetail.toggle() }

// Matched geometry effect (hero transitions)
@Namespace private var animation
Image(item.image)
    .matchedGeometryEffect(id: item.id, in: animation)

// Phase animator (iOS 17+)
PhaseAnimator([false, true]) { phase in
    Image(systemName: "star.fill")
        .scaleEffect(phase ? 1.5 : 1.0)
        .opacity(phase ? 0.5 : 1.0)
}

// Transition
if showContent {
    CardView().transition(.asymmetric(insertion: .push(from: .bottom), removal: .opacity))
}

// Keyframe animator (iOS 17+)
KeyframeAnimator(initialValue: AnimationValues()) { values in
    Image(systemName: "star.fill")
        .scaleEffect(values.scale)
        .rotationEffect(values.rotation)
} keyframes: { _ in
    KeyframeTrack(\.scale) { SpringKeyframe(1.5, duration: 0.3); SpringKeyframe(1.0, duration: 0.3) }
    KeyframeTrack(\.rotation) { LinearKeyframe(.degrees(360), duration: 0.6) }
}
```

---

## 7. Accessibility

### Essential Accessibility
```swift
Image("profile")
    .accessibilityLabel("Profile photo of \(user.name)")
    .accessibilityHint("Double tap to view profile")
    .accessibilityAddTraits(.isButton)

Button("Delete") { delete() }
    .accessibilityIdentifier("delete-button") // For UI testing

VStack {
    Text(item.title)
    Text(item.subtitle)
}
.accessibilityElement(children: .combine) // Read as one element

// Dynamic Type support — always use system text styles
Text("Title").font(.headline) // ✅ Scales with Dynamic Type
Text("Title").font(.system(size: 18)) // ❌ Fixed size, won't scale
```

### Accessibility Checklist
- [ ] All images have `accessibilityLabel` (or `.accessibilityHidden(true)` for decorative)
- [ ] Interactive elements have `.accessibilityHint` for non-obvious actions
- [ ] Complex views use `.accessibilityElement(children: .combine)` or custom labels
- [ ] Supports Dynamic Type (use system text styles, avoid fixed sizes)
- [ ] Supports VoiceOver navigation order (`.accessibilitySortPriority`)
- [ ] Color is not the only way to convey information (add icons/text)
- [ ] Minimum touch target size: 44×44 points
- [ ] Custom controls have proper traits (`.isButton`, `.isHeader`, `.isSelected`)



---

<!-- Script: scripts/scaffold_ios_project.py -->

# Script: scaffold_ios_project.py

```python
#!/usr/bin/env python3
"""
Generate iOS project scaffolding with proper file structure, boilerplate code,
and configuration for different architecture patterns.

Usage:
    python scaffold_ios_project.py --config project.json --output ./MyApp

Config JSON:
{
    "project_name": "MyApp",
    "bundle_id": "com.example.myapp",
    "organization": "Example Inc",
    "deployment_target": "17.0",
    "architecture": "mvvm",          // mvvm, mv, tca, clean
    "features": ["auth", "home", "settings"],
    "use_swiftdata": true,
    "use_combine": false,
    "use_networking": true,
    "include_tests": true
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


def generate_app_entry(config):
    name = config["project_name"]
    use_swiftdata = config.get("use_swiftdata", False)

    model_container = ""
    if use_swiftdata:
        model_container = "\n            .modelContainer(for: [/* Your models here */])"

    return f"""import SwiftUI

@main
struct {name}App: App {{
    @State private var container = AppContainer()

    var body: some Scene {{
        WindowGroup {{
            ContentView()
                .environment(container){model_container}
        }}
    }}
}}
"""


def generate_content_view(config):
    features = config.get("features", ["home"])
    tabs = ""
    for f in features:
        title = f.title()
        icon = {"auth": "person.circle", "home": "house", "settings": "gear",
                "search": "magnifyingglass", "profile": "person"}.get(f, "star")
        tabs += f"""
            Tab("{title}", systemImage: "{icon}", value: .{f}) {{
                {title}View()
            }}"""

    enum_cases = ", ".join(f".{f}" for f in features)

    return f"""import SwiftUI

struct ContentView: View {{
    @State private var selectedTab = Tab.{features[0]}

    enum Tab {{
        case {", ".join(features)}
    }}

    var body: some View {{
        TabView(selection: $selectedTab) {{{tabs}
        }}
    }}
}}

#Preview {{
    ContentView()
}}
"""


def generate_app_container(config):
    name = config["project_name"]
    use_networking = config.get("use_networking", True)

    network_props = ""
    if use_networking:
        network_props = """
    private(set) lazy var apiClient = APIClient(
        baseURL: URL(string: "https://api.example.com")!
    )
"""

    return f"""import SwiftUI

@Observable
final class AppContainer {{
    {network_props}
    // Add repository factories here
    // func makeHomeViewModel() -> HomeViewModel {{
    //     HomeViewModel(repository: HomeRepository(apiClient: apiClient))
    // }}
}}
"""


def generate_feature_view(feature_name, config):
    title = feature_name.title()
    arch = config.get("architecture", "mvvm")

    if arch == "mvvm":
        return f"""import SwiftUI

struct {title}View: View {{
    @State private var viewModel = {title}ViewModel()

    var body: some View {{
        NavigationStack {{
            VStack {{
                if viewModel.isLoading {{
                    ProgressView()
                }} else {{
                    Text("{title}")
                        .font(.largeTitle)
                }}
            }}
            .navigationTitle("{title}")
            .task {{ await viewModel.load() }}
        }}
    }}
}}

#Preview {{
    {title}View()
}}
"""
    else:  # mv or simple
        return f"""import SwiftUI

struct {title}View: View {{
    var body: some View {{
        NavigationStack {{
            VStack {{
                Text("{title}")
                    .font(.largeTitle)
            }}
            .navigationTitle("{title}")
        }}
    }}
}}

#Preview {{
    {title}View()
}}
"""


def generate_feature_viewmodel(feature_name, config):
    title = feature_name.title()
    return f"""import SwiftUI

@Observable
@MainActor
final class {title}ViewModel {{
    private(set) var isLoading = false
    private(set) var error: AppError?

    func load() async {{
        isLoading = true
        defer {{ isLoading = false }}
        // Load data here
    }}
}}
"""


def generate_api_client(config):
    return """import Foundation

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

    func setAuthToken(_ token: String?) {
        self.authToken = token
    }

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let request = try buildRequest(for: endpoint)
        let (data, response) = try await session.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw AppError.networkFailure(underlying: URLError(.badServerResponse))
        }

        switch httpResponse.statusCode {
        case 200..<300:
            return try decoder.decode(T.self, from: data)
        case 401:
            throw AppError.unauthorized
        case 404:
            throw AppError.notFound
        default:
            throw AppError.serverError(statusCode: httpResponse.statusCode)
        }
    }

    private func buildRequest(for endpoint: Endpoint) throws -> URLRequest {
        guard let url = URL(string: endpoint.path, relativeTo: baseURL) else {
            throw AppError.networkFailure(underlying: URLError(.badURL))
        }

        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method
        request.httpBody = endpoint.body

        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("application/json", forHTTPHeaderField: "Accept")

        if let token = authToken {
            request.setValue("Bearer \\(token)", forHTTPHeaderField: "Authorization")
        }

        return request
    }
}
"""


def generate_endpoint(config):
    return """import Foundation

enum Endpoint {
    // Define your API endpoints here
    // case users
    // case user(id: String)
    // case createUser(CreateUserRequest)

    var path: String {
        switch self {
        // case .users: "/api/v1/users"
        // case .user(let id): "/api/v1/users/\\(id)"
        default: ""
        }
    }

    var method: String {
        switch self {
        default: "GET"
        }
    }

    var body: Data? {
        switch self {
        default: nil
        }
    }
}
"""


def generate_app_error(config):
    return """import Foundation

enum AppError: LocalizedError {
    case networkFailure(underlying: Error)
    case decodingFailure
    case unauthorized
    case notFound
    case serverError(statusCode: Int)
    case unknown

    var errorDescription: String? {
        switch self {
        case .networkFailure(let error):
            "Network error: \\(error.localizedDescription)"
        case .decodingFailure:
            "Failed to process server response"
        case .unauthorized:
            "Please sign in again"
        case .notFound:
            "The requested resource was not found"
        case .serverError(let code):
            "Server error (\\(code))"
        case .unknown:
            "An unexpected error occurred"
        }
    }
}
"""


def generate_loading_state_view(config):
    return """import SwiftUI

enum LoadingState<T> {
    case idle
    case loading
    case loaded(T)
    case error(AppError)
}

struct LoadingStateView<T, Content: View>: View {
    let state: LoadingState<T>
    @ViewBuilder let content: (T) -> Content
    var retry: (() async -> Void)?

    var body: some View {
        switch state {
        case .idle:
            Color.clear
        case .loading:
            ProgressView()
                .frame(maxWidth: .infinity, maxHeight: .infinity)
        case .loaded(let data):
            content(data)
        case .error(let error):
            ContentUnavailableView {
                Label("Error", systemImage: "exclamationmark.triangle")
            } description: {
                Text(error.localizedDescription)
            } actions: {
                if let retry {
                    Button("Retry") {
                        Task { await retry() }
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
        }
    }
}
"""


def generate_primary_button(config):
    return """import SwiftUI

struct PrimaryButtonStyle: ButtonStyle {
    @Environment(\\.isEnabled) private var isEnabled

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .font(.headline)
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .background(isEnabled ? Color.accentColor : Color.gray, in: .capsule)
            .opacity(configuration.isPressed ? 0.85 : 1.0)
            .scaleEffect(configuration.isPressed ? 0.98 : 1.0)
            .animation(.easeInOut(duration: 0.15), value: configuration.isPressed)
    }
}

extension ButtonStyle where Self == PrimaryButtonStyle {
    static var primary: PrimaryButtonStyle { PrimaryButtonStyle() }
}
"""


def generate_view_extensions(config):
    return """import SwiftUI

extension View {
    func cardStyle() -> some View {
        self
            .padding()
            .background(.regularMaterial, in: .rect(cornerRadius: 12))
            .shadow(color: .black.opacity(0.08), radius: 8, y: 4)
    }

    func hideKeyboard() {
        UIApplication.shared.sendAction(
            #selector(UIResponder.resignFirstResponder), to: nil, from: nil, for: nil
        )
    }
}
"""


def generate_unit_test(feature_name, config):
    title = feature_name.title()
    project = config["project_name"]
    return f"""import Testing
@testable import {project}

@Suite("{title}ViewModel Tests")
struct {title}ViewModelTests {{
    @Test("initial state is correct")
    func initialState() {{
        let viewModel = {title}ViewModel()
        #expect(viewModel.isLoading == false)
        #expect(viewModel.error == nil)
    }}

    @Test("loading sets isLoading")
    @MainActor
    func loading() async {{
        let viewModel = {title}ViewModel()
        // Test loading behavior
    }}
}}
"""


def scaffold_project(config, output_dir):
    name = config["project_name"]
    base = os.path.join(output_dir, name)
    features = config.get("features", ["home"])
    arch = config.get("architecture", "mvvm")
    use_networking = config.get("use_networking", True)
    include_tests = config.get("include_tests", True)

    print(f"\n🏗️  Scaffolding {name} ({arch.upper()} architecture)\n")

    # App entry point
    create_file(os.path.join(base, "App", f"{name}App.swift"), generate_app_entry(config))
    create_file(os.path.join(base, "App", "ContentView.swift"), generate_content_view(config))
    create_file(os.path.join(base, "App", "AppContainer.swift"), generate_app_container(config))

    # Feature modules
    for feature in features:
        title = feature.title()
        create_file(
            os.path.join(base, "Features", title, "Views", f"{title}View.swift"),
            generate_feature_view(feature, config)
        )
        if arch == "mvvm":
            create_file(
                os.path.join(base, "Features", title, "ViewModels", f"{title}ViewModel.swift"),
                generate_feature_viewmodel(feature, config)
            )
        create_file(
            os.path.join(base, "Features", title, "Models", ".gitkeep"), ""
        )

    # Core
    create_file(os.path.join(base, "Core", "Models", "AppError.swift"), generate_app_error(config))

    if use_networking:
        create_file(os.path.join(base, "Core", "Networking", "APIClient.swift"), generate_api_client(config))
        create_file(os.path.join(base, "Core", "Networking", "Endpoint.swift"), generate_endpoint(config))

    # Shared components
    create_file(os.path.join(base, "Shared", "Components", "LoadingStateView.swift"), generate_loading_state_view(config))
    create_file(os.path.join(base, "Shared", "Components", "PrimaryButton.swift"), generate_primary_button(config))
    create_file(os.path.join(base, "Shared", "Extensions", "View+Extensions.swift"), generate_view_extensions(config))

    # Tests
    if include_tests:
        for feature in features:
            title = feature.title()
            create_file(
                os.path.join(base, "Tests", "UnitTests", f"{title}ViewModelTests.swift"),
                generate_unit_test(feature, config)
            )

    # Gitignore
    create_file(os.path.join(output_dir, ".gitignore"), """# Xcode
build/
DerivedData/
*.xcuserstate
*.xcworkspacedata
xcuserdata/

# Swift Package Manager
.build/
Packages/

# CocoaPods
Pods/

# Misc
*.DS_Store
*.swp
""")

    print(f"\n✅ Project scaffolded at: {base}")
    print(f"   Architecture: {arch.upper()}")
    print(f"   Features: {', '.join(f.title() for f in features)}")
    print(f"   Networking: {'Yes' if use_networking else 'No'}")
    print(f"   Tests: {'Yes' if include_tests else 'No'}")
    print(f"\n   Next steps:")
    print(f"   1. Open Xcode → Create new project → {name}")
    print(f"   2. Copy generated files into the project")
    print(f"   3. Add to source control")


def main():
    parser = argparse.ArgumentParser(description="Scaffold iOS Project")
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
