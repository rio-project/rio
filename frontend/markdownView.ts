import { WidgetBase, WidgetState } from './widgetBase';
import * as showdown from 'showdown';
import hljs from 'highlight.js';

export type MarkdownViewState = WidgetState & {
    _type_: 'MarkdownView-builtin';
    child?: null | number | string;
    classes?: string[];
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
        const stripped = line.trimLeft();
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
function convertMarkdown(markdownSource: string, div: HTMLElement) {
    // Convert the Markdown content to HTML
    const converter = new showdown.Converter();
    div.innerHTML = converter.makeHtml(markdownSource);

    // Enhance code blocks
    const codeBlocks = div.querySelectorAll('pre code');
    codeBlocks.forEach((codeBlockInner) => {
        codeBlockInner = codeBlockInner as HTMLElement;

        // Remove empty leading/trailing lines
        codeBlockInner.textContent = codeBlockInner.textContent
            ? codeBlockInner.textContent.trim()
            : '';

        // Was a language specified?
        let specifiedLanguage: string | null = null;
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

        // Wrap the code block. This outer element will hold additional
        // widgets and styling.
        let codeBlockOuter = document.createElement('div');
        codeBlockOuter.classList.add('reflex-markdown-code-block');

        codeBlockOuter.innerHTML = `<div class="reflex-markdown-code-block-header"><div class="reflex-markdown-code-block-language">${
            languageNiceName === undefined ? '' : languageNiceName
        }</div><button class="reflex-markdown-code-block-copy-button">Copy code</button></div>`;

        codeBlockInner.parentNode!.insertBefore(codeBlockOuter, codeBlockInner);
        codeBlockOuter.appendChild(codeBlockInner);

        // Create a copy button
        let copyButton = codeBlockOuter.querySelector(
            '.reflex-markdown-code-block-copy-button'
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
}

export class MarkdownViewWidget extends WidgetBase {
    state: Required<MarkdownViewState>;

    createElement() {
        const element = document.createElement('div');
        element.classList.add('reflex-markdown-view');
        return element;
    }

    updateElement(element, deltaState) {
        if (deltaState.text !== undefined) {
            convertMarkdown(deltaState.text, element);
        }
    }
}
