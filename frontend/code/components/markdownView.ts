import { ComponentBase, ComponentState } from './componentBase';
import { micromark } from 'micromark';

// This import decides which languages are supported by `highlight.js`. See
// their docs for details:
//
// https://github.com/highlightjs/highlight.js#importing-the-library
import hljs from 'highlight.js/lib/common';

export type MarkdownViewState = ComponentState & {
    _type_: 'MarkdownView-builtin';
    text?: string;
    default_language?: null | string;
};

// Remove an equal amount of trim from each line, taking care to ignore
// empty lines.
function blockTrim(value: string) {
    if (!value) {
        return '';
    }

    // Split the input string into lines
    const lines = value.replace(/\t/g, ' ').split('\n');

    // Determine the minimum indentation level
    let indent = Number.MAX_SAFE_INTEGER;
    for (const line of lines.slice(1)) {
        const stripped = line.trimStart();
        if (stripped) {
            indent = Math.min(indent, line.length - stripped.length);
        }
    }

    // Remove excess indentation and leading/trailing blank lines
    const trimmedLines = [lines[0].trim()];
    if (indent < Number.MAX_SAFE_INTEGER) {
        for (const line of lines.slice(1)) {
            trimmedLines.push(line.slice(indent).trimRight());
        }
    }

    // Join the lines back together
    return trimmedLines.join('\n');
}

// Convert a Markdown string to HTML and render it in the given div.
function convertMarkdown(
    markdownSource: string,
    div: HTMLElement,
    defaultLanguage: null | string
) {
    // Drop the default language if it isn't supported or recognized
    if (
        defaultLanguage !== null &&
        hljs.getLanguage(defaultLanguage) === undefined
    ) {
        defaultLanguage = null;
    }

    // Convert the Markdown content to HTML
    div.innerHTML = micromark(markdownSource);

    // Enhance code blocks
    const codeBlocks = div.querySelectorAll('pre code');
    codeBlocks.forEach((codeBlockInner) => {
        codeBlockInner = codeBlockInner as HTMLElement;

        // Remove empty leading/trailing lines
        codeBlockInner.textContent = codeBlockInner.textContent
            ? codeBlockInner.textContent.trim()
            : '';

        // Was a language specified?
        let specifiedLanguage: string | null = defaultLanguage;
        for (const cls of codeBlockInner.classList) {
            if (cls.startsWith('language-')) {
                specifiedLanguage = cls.replace('language-', '');
                break;
            }
        }

        // See if this language is supported
        if (
            specifiedLanguage !== null &&
            hljs.getLanguage(specifiedLanguage) === undefined
        ) {
            specifiedLanguage = null;
        }

        // Add syntax highlighting. This will also detect the actual
        // language.
        let languageNiceName;

        if (specifiedLanguage === null) {
            let hlResult = hljs.highlightAuto(codeBlockInner.textContent);
            codeBlockInner.innerHTML = hlResult.value;
            languageNiceName = hljs.getLanguage(hlResult.language!)!.name;
        } else {
            let hlResult = hljs.highlight(codeBlockInner.textContent, {
                language: specifiedLanguage,
                ignoreIllegals: true,
            });
            codeBlockInner.innerHTML = hlResult.value;
            languageNiceName = hljs.getLanguage(specifiedLanguage)!.name;
        }

        // Get the language from the code block class (if specified)
        // const languageClass = codeBlockInner.className.split(' ').find((cls) =>
        //     cls.startsWith('language-')
        // );
        // const language = languageClass ? languageClass.replace('language-', '') : '';

        // Wrap the code block. This outer element will hold additional widgets
        // and styling.
        let codeBlockOuter = document.createElement('div');
        codeBlockOuter.classList.add('rio-markdown-code-block');

        codeBlockOuter.innerHTML = `<div class="rio-markdown-code-block-header"><div class="rio-markdown-code-block-language">${
            languageNiceName === undefined ? '' : languageNiceName
        }</div><button class="rio-markdown-code-block-copy-button">Copy code</button></div>`;

        codeBlockInner.parentNode!.insertBefore(codeBlockOuter, codeBlockInner);
        codeBlockOuter.appendChild(codeBlockInner);

        // Create a copy button
        let copyButton = codeBlockOuter.querySelector(
            '.rio-markdown-code-block-copy-button'
        ) as HTMLButtonElement;

        copyButton.addEventListener('click', () => {
            const codeToCopy = (codeBlockInner as HTMLElement).innerText;
            const textArea = document.createElement('textarea');
            textArea.value = codeToCopy;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            copyButton.textContent = 'Copied ✓';
            setTimeout(() => {
                copyButton.textContent = 'Copy code';
            }, 5000);
        });
    });

    // Highlight inline code
    //
    // Since these are very short, guessing the language probably isn't a great
    // idea. Only do this if a default language was specified.
    //
    // TODO: What if most code blocks had the same language specified? Use the
    // same one here?
    if (defaultLanguage !== null) {
        const inlineCodeBlocks = div.querySelectorAll('code');
        inlineCodeBlocks.forEach((codeElement) => {
            let hlResult = hljs.highlight(codeElement.textContent || '', {
                language: defaultLanguage!,
                ignoreIllegals: true,
            });

            codeElement.innerHTML = hlResult.value;
        });
    }
}

export class MarkdownViewComponent extends ComponentBase {
    state: Required<MarkdownViewState>;

    createElement(): HTMLElement {
        const element = document.createElement('div');
        element.classList.add('rio-markdown-view');
        return element;
    }

    updateElement(element: HTMLElement, deltaState: MarkdownViewState): void {
        if (deltaState.text !== undefined) {
            let defaultLanguage =
                deltaState.default_language || this.state.default_language;

            convertMarkdown(deltaState.text, element, defaultLanguage);
        }
    }
}
