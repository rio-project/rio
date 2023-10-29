# Snippets

This directory, and in particular the subdirectory `snippet-files` contains rio
related code snippets which can be used for tutorials, setting up sample
projects, or simlar. You can find facilities for reading these files in this
very directory. Just import it as a Python module.

## Snippets Structure

There should be no files directly in the `snippet-files` directory. Instead, all
files must be located in subdirectories. The name of the subdirectory is used as
the group name for all snippets within it (directly or indirectly). Any more
subdirectories will be ignored. Thus, these files would be available as
`group/foo`, `group/bar`, and `group/baz`:

```
snippet-files
└── group
    ├── foo.py
    ├── bar.py
    └── baz.py
```

Note that the file extensions are not part of the snippet name.
