# C# keywords — grouped (from Microsoft documentation)


## Literal keywords
- `true`
- `false`
- `null`

---

## Type keywords (built-in / special type identifiers)
- `bool`
- `byte`
- `sbyte`
- `short`
- `ushort`
- `int`
- `uint`
- `long`
- `ulong`
- `char`
- `float`
- `double`
- `decimal`
- `string`
- `object`
- `void`

---

## Declaration keywords (types, members, namespaces, generics)
- `class`
- `struct`
- `interface`
- `enum`
- `delegate`
- `namespace`
- `record`
- `where` *(generic constraint)*
- `new` *(also an operator keyword; used in object creation and generic constraints)*

---

## Access modifiers
- `public`
- `private`
- `protected`
- `internal`
- `file` *(file-scoped types; modifier)*

---

## Member / type modifiers
- `static`
- `readonly`
- `const`
- `sealed`
- `abstract`
- `virtual`
- `override`
- `extern`
- `unsafe`
- `volatile`
- `partial`
- `ref` *(also used in parameter passing / returns)*
- `required`

---

## Parameter / argument modifiers
- `in`
- `out`
- `ref`
- `params`
- `scoped` *(ref-safety)*

---

## Inheritance / type relationship keywords
- `base`
- `this`
- `is`
- `as`
- `typeof`
- `nameof`
- `sizeof`
- `checked`
- `unchecked`

---

## Statement / control-flow keywords (selection, iteration, jumps)
### Selection
- `if`
- `else`
- `switch`
- `case`
- `default`

### Iteration
- `for`
- `foreach`
- `while`
- `do`

### Jumps
- `break`
- `continue`
- `goto`
- `return`

---

## Exception handling keywords
- `try`
- `catch`
- `finally`
- `throw`

---

## Resource management keywords
- `using` *(also a directive keyword)*

---

## Concurrency / async keywords
- `async`
- `await`

---

## Pattern / matching keywords
- `when` *(pattern guard; also used in `catch` filters)*

---

## Expression / operator keywords (by intent)
### Object/instance creation and value initialization
- `new`
- `stackalloc`

### Lambda / function-like constructs
- `delegate`

### Type/metadata and reflection-like expressions
- `typeof`
- `nameof`

### Arithmetic / bitwise / boolean-ish operator keywords
- `operator` *(overload declaration)*
- `implicit` *(conversion operator declaration)*
- `explicit` *(conversion operator declaration)*

---

## Contextual keywords (special meaning in specific contexts)
### Query keywords (LINQ query expressions)
- `from`
- `where`
- `select`
- `group`
- `into`
- `join`
- `let`
- `in`
- `on`
- `equals`
- `by`
- `orderby`
- `ascending`
- `descending`

### Partial / type inference / anonymous types / convenience
- `var`
- `dynamic`

### Nullable and related operators / constraints context
- `not` *(pattern)*
- `and` *(pattern)*
- `or` *(pattern)*

### Member access / property patterns / init-only
- `value` *(in setters)*
- `init` *(init accessor)*

### Ranges / indices context
- `with` *(record `with` expression; also used with `using`-like constructs? — record cloning context)*

### Advanced / newer language constructs
- `global` *(global using directives, global namespace alias)*
- `alias` *(extern alias context)*
- `add` *(event accessor context)*
- `remove` *(event accessor context)*
- `get` *(accessor context)*
- `set` *(accessor context)*

---

## Preprocessor directive keywords (appear after `#`)
- `#if`
- `#elif`
- `#else`
- `#endif`
- `#define`
- `#undef`
- `#warning`
- `#error`
- `#line`
- `#region`
- `#endregion`
- `#nullable`
- `#pragma`

---

## Other reserved keywords (misc language features)
- `event`
- `operator`
- `implicit`
- `explicit`
- `this`
- `base`
- `lock`
- `fixed`
- `yield`
- `get`
- `set`
- `add`
- `remove`
- `value`
- `params`
- `type`
- `nameof`
- `with`

---

## Keywords related to advanced memory / interop / safety
- `unsafe`
- `fixed`
- `stackalloc`
- `extern`
- `volatile`

---

## Keywords related to iterators
- `yield`

---

## Keywords related to synchronization
- `lock`

---

## Keywords related to type inference / dynamic binding
- `var`
- `dynamic`
