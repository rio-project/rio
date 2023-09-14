from typing import *  # type: ignore

import reflex as rx
from .. import theme

from .. import components as comps
import tools.build_docs


OUTLINE = {
    "Introduction": (
        "What is Reflex?",
        "Why Reflex?",
        "How does Reflex work?",
    ),
    "Getting Started": (
        "Installation",
        "Hello World",
        "Widgets",
        "Layouts",
    ),
    "Advanced": (
        "Styling",
        "Events",
        "Animations",
        "Reflex CLI",
    ),
}


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


class DocumentationView(rx.Widget):
    def build(self) -> rx.Widget:
        # Build the outliner
        chapter_expanders = []

        for chapter, sections in OUTLINE.items():
            buttons = [
                rx.Button(
                    section,
                    color=rx.Color.TRANSPARENT,
                    on_press=lambda _: self.session.navigate_to(f"./{section}"),
                )
                for section in sections
            ]

            chapter_expanders.append(
                rx.Revealer(
                    chapter,
                    rx.Column(
                        *buttons,
                        spacing=theme.THEME.base_spacing,
                    ),
                ),
            )

        # Combine everything
        return rx.Column(
            comps.NavigationBarDeadSpace(),
            rx.Row(
                rx.Column(
                    *chapter_expanders,
                    margin_left=3,
                    width=20,
                    align_y=0,
                ),
                rx.Router(
                    rx.Route(
                        "",
                        lambda: rx.Column(
                            comps.ClassApiDocsView(
                                tools.build_docs.parse_class(rx.Column)
                            ),
                            rx.MarkdownView(text=DOCS_STR),
                            width=65,
                            height="grow",
                            align_x=0.5,
                        ),
                    ),
                    width="grow",
                    height="grow",
                ),
                height="grow",
                spacing=3,
            ),
        )
