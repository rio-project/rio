import { pixelsPerEm } from './app';
import { textStyleToCss } from './cssUtils';
import { TextStyle } from './models';

const _textDimensionsCache = new Map<string, [number, number]>();

let cacheHits: number = 0;
let cacheMisses: number = 0;

/// Returns the width and height of the given text in pixels. Does not cache
/// the result.
export function getTextDimensions(
    text: string,
    style: 'heading1' | 'heading2' | 'heading3' | 'text' | 'dim' | TextStyle
): [number, number] {
    // Make sure the text isn't just whitespace, as that results in a wrong [0,
    // 0]
    //
    // FIXME: Still imperfect, as now all whitespace is the same width, and an
    // empty string has a width.
    if (text.trim().length === 0) {
        text = 'l';
    }

    // Build a key for the cache
    let key;
    if (typeof style === 'string') {
        key = `${style}+${text}`;
    } else {
        key = `${style.fontName}+${style.fontWeight}+${style.italic}+${style.underlined}+${style.allCaps}+${text}`;
    }

    // Display cache statistics
    // if (cacheHits + cacheMisses > 0) {
    //     console.log(`Cache hit rate: ${cacheHits / (cacheHits + cacheMisses)}`);
    // }

    // Check the cache
    let cached = _textDimensionsCache.get(key);

    if (cached !== undefined) {
        cacheHits++;
        return cached;
    }
    cacheMisses++;

    // Spawn an element to measure the text
    let element = document.createElement('div');
    element.textContent = text;
    Object.assign(element.style, textStyleToCss(style));
    element.style.position = 'absolute';

    document.body.appendChild(element);

    let rect = element.getBoundingClientRect();
    let result = [rect.width / pixelsPerEm, rect.height / pixelsPerEm] as [
        number,
        number,
    ];
    element.remove();

    // Store in the cache and return
    _textDimensionsCache.set(key, result);
    return result;
}
