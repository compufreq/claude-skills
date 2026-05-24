# Reactive Programming Reference

## Table of Contents
1. Combine Framework
2. Combine Operators
3. Combine + SwiftUI
4. Combine + UIKit
5. RxSwift Essentials
6. RxSwift ↔ Combine Migration
7. Choosing Between Combine, RxSwift, and async/await

---

## 1. Combine Framework

Combine is Apple's first-party reactive framework. It uses Publishers that emit values
over time and Subscribers that receive them.

### Core Concepts

| Concept | Description |
|---------|------------|
| **Publisher** | Emits a sequence of values over time, then completes or fails |
| **Subscriber** | Receives values from a Publisher |
| **Operator** | Transforms, filters, or combines publishers |
| **Subject** | A publisher you can imperatively send values to |
| **Cancellable** | A handle to cancel a subscription |

### Subjects

```swift
// PassthroughSubject — no initial value, forwards values
let taps = PassthroughSubject<Void, Never>()
taps.send()

// CurrentValueSubject — has an initial value, remembers the latest
let username = CurrentValueSubject<String, Never>("")
username.value = "alice"
username.send("bob")
print(username.value) // "bob"
```

### Built-in Publishers

```swift
// Just — emits a single value
Just(42).sink { print($0) } // 42

// Future — async operation that produces one value
Future<User, Error> { promise in
    Task {
        let user = try await fetchUser()
        promise(.success(user))
    }
}

// Timer
Timer.publish(every: 1.0, on: .main, in: .common).autoconnect()

// NotificationCenter
NotificationCenter.default.publisher(for: UIApplication.willEnterForegroundNotification)

// URLSession
URLSession.shared.dataTaskPublisher(for: url)

// @Published property wrapper (ObservableObject)
class ViewModel: ObservableObject {
    @Published var searchText = ""
    @Published private(set) var results: [Item] = []
}
```

---

## 2. Combine Operators

### Transforming

```swift
// map — transform each value
publisher.map { $0.uppercased() }
publisher.map(\.name) // KeyPath shorthand

// flatMap — transform into a new publisher (for chaining async operations)
searchTextPublisher
    .flatMap { query in apiClient.search(query) }

// compactMap — transform + filter nil
publisher.compactMap { Int($0) } // Only emits non-nil Int conversions

// tryMap — map that can throw
publisher.tryMap { try JSONDecoder().decode(User.self, from: $0) }
```

### Filtering

```swift
// filter
publisher.filter { $0.count > 3 }

// removeDuplicates
publisher.removeDuplicates()

// debounce — wait for pause in emissions
searchText.debounce(for: .milliseconds(300), scheduler: RunLoop.main)

// throttle — emit at most once per interval
scrollOffset.throttle(for: .milliseconds(100), scheduler: RunLoop.main, latest: true)

// first / last
publisher.first()
publisher.first(where: { $0 > 10 })
```

### Combining

```swift
// combineLatest — emit when any publisher emits
Publishers.CombineLatest(usernamePublisher, passwordPublisher)
    .map { username, password in !username.isEmpty && password.count >= 8 }

// merge — combine publishers of the same type
Publishers.Merge(localResults, remoteResults)

// zip — pair values 1:1
Publishers.Zip(namePublisher, avatarPublisher)

// switchToLatest — cancel previous, use latest
searchText
    .map { query in apiClient.search(query) }
    .switchToLatest() // Cancels in-flight request when new query arrives
```

### Error Handling

```swift
// catch — replace error with fallback publisher
publisher.catch { error in Just(fallbackValue) }

// retry — retry on failure
publisher.retry(3)

// replaceError — replace error with a value
publisher.replaceError(with: [])

// mapError — transform error type
publisher.mapError { AppError.networkFailure(underlying: $0) }
```

### Scheduling

```swift
// receive(on:) — deliver values on a specific queue
publisher.receive(on: DispatchQueue.main) // UI updates

// subscribe(on:) — perform subscription work on a specific queue
publisher.subscribe(on: DispatchQueue.global(qos: .background))
```

---

## 3. Combine + SwiftUI

### Search with Debounce (Pre-iOS 17)

```swift
class SearchViewModel: ObservableObject {
    @Published var query = ""
    @Published private(set) var results: [Item] = []
    @Published private(set) var isSearching = false
    
    private var cancellables = Set<AnyCancellable>()
    
    init(searchService: SearchServiceProtocol) {
        $query
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .handleEvents(receiveOutput: { [weak self] _ in self?.isSearching = true })
            .flatMap { query in
                searchService.search(query: query)
                    .catch { _ in Just([]) }
            }
            .receive(on: DispatchQueue.main)
            .sink { [weak self] results in
                self?.results = results
                self?.isSearching = false
            }
            .store(in: &cancellables)
    }
}
```

### Form Validation

```swift
class SignUpViewModel: ObservableObject {
    @Published var email = ""
    @Published var password = ""
    @Published var confirmPassword = ""
    @Published private(set) var isValid = false
    @Published private(set) var emailError: String?
    @Published private(set) var passwordError: String?
    
    private var cancellables = Set<AnyCancellable>()
    
    init() {
        let validEmail = $email.map { $0.contains("@") && $0.contains(".") }
        let validPassword = $password.map { $0.count >= 8 }
        let passwordsMatch = Publishers.CombineLatest($password, $confirmPassword)
            .map { $0 == $1 }
        
        Publishers.CombineLatest3(validEmail, validPassword, passwordsMatch)
            .map { $0 && $1 && $2 }
            .assign(to: &$isValid)
        
        $email
            .debounce(for: .milliseconds(500), scheduler: RunLoop.main)
            .map { email -> String? in
                guard !email.isEmpty else { return nil }
                return email.contains("@") ? nil : "Invalid email format"
            }
            .assign(to: &$emailError)
    }
}
```

---

## 4. Combine + UIKit

```swift
class LoginViewController: UIViewController {
    private let viewModel = LoginViewModel()
    private var cancellables = Set<AnyCancellable>()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Bind text field to view model
        emailTextField.textPublisher
            .assign(to: \.email, on: viewModel)
            .store(in: &cancellables)
        
        // Observe loading state
        viewModel.$isLoading
            .receive(on: DispatchQueue.main)
            .sink { [weak self] isLoading in
                self?.loginButton.isEnabled = !isLoading
                self?.activityIndicator.isHidden = !isLoading
            }
            .store(in: &cancellables)
        
        // Observe errors
        viewModel.$error
            .compactMap { $0 }
            .receive(on: DispatchQueue.main)
            .sink { [weak self] error in
                self?.showAlert(message: error.localizedDescription)
            }
            .store(in: &cancellables)
    }
}

// UITextField publisher extension
extension UITextField {
    var textPublisher: AnyPublisher<String, Never> {
        NotificationCenter.default
            .publisher(for: UITextField.textDidChangeNotification, object: self)
            .compactMap { ($0.object as? UITextField)?.text }
            .eraseToAnyPublisher()
    }
}
```

---

## 5. RxSwift Essentials

RxSwift is the Swift implementation of ReactiveX. If the project already uses RxSwift,
follow these patterns.

### Core Types

| RxSwift | Combine Equivalent | Description |
|---------|-------------------|-------------|
| `Observable` | `Publisher` | Emits values over time |
| `Observer` / `subscribe` | `Subscriber` / `sink` | Receives values |
| `Subject` | `Subject` | Imperative publishing |
| `BehaviorSubject` | `CurrentValueSubject` | Has initial/latest value |
| `PublishSubject` | `PassthroughSubject` | No initial value |
| `DisposeBag` | `Set<AnyCancellable>` | Manages subscription lifetimes |
| `Driver` | `AnyPublisher + .receive(on: main)` | Main thread, no errors |
| `Single` | `Future` | One value or error |

### RxSwift MVVM Pattern

```swift
class TaskListViewModel {
    struct Input {
        let viewDidLoad: Observable<Void>
        let pullToRefresh: Observable<Void>
        let deleteTask: Observable<IndexPath>
    }
    
    struct Output {
        let tasks: Driver<[Task]>
        let isLoading: Driver<Bool>
        let error: Driver<String>
    }
    
    private let repository: TaskRepositoryProtocol
    private let disposeBag = DisposeBag()
    
    init(repository: TaskRepositoryProtocol) {
        self.repository = repository
    }
    
    func transform(input: Input) -> Output {
        let isLoading = BehaviorSubject<Bool>(value: false)
        let errorSubject = PublishSubject<String>()
        
        let tasks = Observable.merge(input.viewDidLoad, input.pullToRefresh)
            .do(onNext: { isLoading.onNext(true) })
            .flatMapLatest { [repository] in
                repository.fetchAll()
                    .catch { error in
                        errorSubject.onNext(error.localizedDescription)
                        return .just([])
                    }
            }
            .do(onNext: { _ in isLoading.onNext(false) })
            .asDriver(onErrorJustReturn: [])
        
        return Output(
            tasks: tasks,
            isLoading: isLoading.asDriver(onErrorJustReturn: false),
            error: errorSubject.asDriver(onErrorJustReturn: "")
        )
    }
}
```

### RxSwift Operators Cheat Sheet

```swift
// Transform
.map { }, .flatMap { }, .compactMap { }, .scan(initialValue) { acc, val in }

// Filter
.filter { }, .distinctUntilChanged(), .debounce(.milliseconds(300)), .throttle(.milliseconds(100))

// Combine
.combineLatest(other), .merge(other), .zip(other), .withLatestFrom(other), .startWith(value)

// Error
.catchError { }, .retry(3), .catchErrorJustReturn(fallback)

// Thread
.observe(on: MainScheduler.instance), .subscribe(on: ConcurrentDispatchQueueScheduler(qos: .background))

// Lifecycle
.take(1), .takeUntil(trigger), .share(replay: 1)
```

---

## 6. RxSwift ↔ Combine Migration

### Operator Mapping

| RxSwift | Combine |
|---------|---------|
| `subscribe { }` | `sink { }` |
| `disposed(by: bag)` | `.store(in: &cancellables)` |
| `map` | `map` |
| `flatMap` | `flatMap` |
| `flatMapLatest` | `map + switchToLatest` |
| `compactMap` | `compactMap` |
| `filter` | `filter` |
| `distinctUntilChanged` | `removeDuplicates` |
| `debounce` | `debounce` |
| `throttle` | `throttle` |
| `combineLatest` | `combineLatest` |
| `merge` | `merge` |
| `zip` | `zip` |
| `withLatestFrom` | No direct equivalent (use `combineLatest + map`) |
| `catchError` | `catch` |
| `catchErrorJustReturn` | `replaceError(with:)` |
| `asDriver` | `.receive(on: DispatchQueue.main).replaceError(with:)` |
| `observe(on: MainScheduler)` | `receive(on: DispatchQueue.main)` |
| `do(onNext:)` | `handleEvents(receiveOutput:)` |
| `startWith` | `prepend` |
| `take(1)` | `first()` or `prefix(1)` |
| `share(replay: 1)` | `share()` (no replay) or `multicast + makeConnectable` |

---

## 7. Choosing Between Combine, RxSwift, and async/await

| Criteria | async/await | Combine | RxSwift |
|----------|------------|---------|---------|
| Apple support | First-party | First-party | Third-party |
| Min deployment | iOS 13 (structured iOS 15) | iOS 13 | iOS 9 |
| Learning curve | Low | Medium | High |
| Best for | Request/response, sequential async | Streams, UI binding, reactive chains | Legacy projects, complex reactive chains |
| Testability | Good | Good | Excellent (RxTest) |
| Community | Growing | Moderate | Large (but declining) |

### Recommendation for New Projects
- **Default**: `async/await` + `@Observable` (iOS 17+)
- **Reactive UI binding**: Combine (if needed beyond @Observable)
- **Legacy/existing RxSwift**: Continue using, migrate gradually to async/await
- **Complex event streams**: Combine or RxSwift (whichever team knows)

### Mixing async/await with Combine
```swift
// Combine → async
let value = try await publisher.values.first(where: { _ in true })

// async → Combine
func searchPublisher(query: String) -> AnyPublisher<[Result], Error> {
    Future { promise in
        Task {
            do {
                let results = try await searchAPI(query: query)
                promise(.success(results))
            } catch {
                promise(.failure(error))
            }
        }
    }.eraseToAnyPublisher()
}
```



---
