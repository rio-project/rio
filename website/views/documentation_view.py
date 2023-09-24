from typing import *  # type: ignore

import rio
import rio_docs

from .. import components as comps
from .. import theme

OUTLINE: Tuple[Optional[Tuple[str, Tuple[str, ...]]], ...] = (
    (
        "Getting Started",
        (
            "A",
            "B",
            "C",
        ),
    ),
    (
        "How-To",
        (
            "Set up a Project",
            "Add Pages to a Project",
            "Deploy a Project",
            "Multiple Pages",
            "Theming",
        ),
    ),
    # API Docs
    None,
    (
        "Inputs",
        (
            "A",
            "B",
            "C",
        ),
    ),
    (
        "Layout",
        (
            "A",
            "B",
            "C",
        ),
    ),
    (
        "Tripswitches",
        (
            "A",
            "B",
            "C",
        ),
    ),
    (
        "Other",
        (
            "A",
            "B",
            "C",
        ),
    ),
    (
        "Non-Widgets",
        (
            "A",
            "B",
            "C",
        ),
    ),
    # Advanced/ Internal / Developer / Contributor Documentation
    None,
    (
        "Deep Dives",
        (
            "A",
            "B",
            "C",
        ),
    ),
    (
        "Contributing",
        (
            "A",
            "B",
            "C",
        ),
    ),
)


DOCS_STR = """
# `TypeScript` Tutorial

Welcome to the `TypeScript` tutorial! In this tutorial you will see

- what `TypeScript` is
- how to install it
- how to write your first `TypeScript` program
- basic `TypeScript` features

## What is `TypeScript`?

`TypeScript` is a statically typed language that builds on the foundation of
`JavaScript`. It allows you to catch errors at compile-time and write more
maintainable code.

### Installation

To get started with `TypeScript`, you need to install it using npm:

```sh
npm install - g typescript
```

You can check the installed version using:

## Your First `TypeScript` Program

Let's create a simple `TypeScript` program. Create a file called hello.ts with
the following content:

```typescript
function sayHello(name: string) {
    console.log(`Hello, ${name}!`);
}

sayHello("TypeScript");
```

Compile the `TypeScript` code to `JavaScript` using the `TypeScript` compiler:

```bash
tsc hello.ts
```

This will generate a hello.js file that you can run with Node.js:

```bash
node hello.js
```

You should see the output: "Hello, TypeScript!"

## Basic `TypeScript` Features

### Variables and Types

In `TypeScript`, you can declare variables with types:

```typescript
let age: number = 30; let name: string = "John"; let isStudent:
boolean = true;
```

### Functions

Functions can also have type annotations:

```typescript
function add(a: number, b: number): number {
    return a + b;
}

const result = add(10, 20);
```

### Interfaces

You can define custom types using interfaces:

```typescript
interface Person {
    name: string; age: number;
}

const person: Person = {
    name: "Alice", age: 25,
};
```

### Classes

Create classes with `TypeScript`:

```typescript
class Animal {
    constructor(public name: string) { }

    speak() {
        console.log(`The ${this.name} makes a sound.`);
    }
}

const dog = new Animal("Dog"); dog.speak();
```

## Conclusion

_This is just the beginning of your `TypeScript` journey_. `TypeScript` offers
many more features like enums, generics, and advanced type system capabilities.
Explore and enjoy the power of `TypeScript` in your projects!

You can find more information on the [official `TypeScript`
website](https://www.typescriptlang.org/).

**Thank you for reading!**
"""


class Outliner(rio.Widget):
    def build(self) -> rio.Widget:
        chapter_expanders = []

        for section in OUTLINE:
            if section is None:
                chapter_expanders.append(rio.Spacer(height=3))
                continue

            title, subsections = section

            buttons = [
                rio.Button(
                    section,
                    color=rio.Color.TRANSPARENT,
                    on_press=lambda _: self.session.navigate_to(f"./{section}"),
                )
                for section in subsections
            ]

            chapter_expanders.append(
                rio.Revealer(
                    title,
                    rio.Column(
                        *buttons,
                        spacing=theme.THEME.base_spacing,
                    ),
                ),
            )

        return comps.FlatCard(
            child=rio.Column(
                *chapter_expanders,
                width=13,
                align_y=0,
            ),
            corner_radius=(
                0,
                theme.THEME.corner_radius_large,
                theme.THEME.corner_radius_large,
                0,
            ),
            align_y=0,
        )


class DocumentationView(rio.Widget):
    def build(self) -> rio.Widget:
        return rio.Column(
            rio.Sticky(
                Outliner(
                    align_x=0,
                    align_y=0.4,
                ),
            ),
            rio.Stack(
                comps.NavigationBarDeadSpace(
                    height=22,
                    align_y=0,
                ),
                rio.Router(
                    margin_top=14,
                    width="grow",
                    height="grow",
                ),
                width="grow",
                height="grow",
            ),
        )
