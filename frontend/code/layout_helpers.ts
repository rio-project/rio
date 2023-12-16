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
    // Build a key for the cache
    let key;
    if (typeof style === 'string') {
        key = style;
    } else {
        key = `${style.fontName}+${style.fontWeight}+${style.italic}+${style.underlined}+${style.allCaps}`;
    }

    // Display cache statistics
    if (cacheHits + cacheMisses > 0) {
        console.log(`Cache hit rate: ${cacheHits / (cacheHits + cacheMisses)}`);
    }

    // Check the cache
    let cached = _textDimensionsCache.get(key);

    if (cached !== undefined) {
        cacheHits++;
        return cached;
    }
    cacheMisses++;

    // Spawn an element to measure the text
    let element = document.createElement('div');
    element.innerText = text;
    Object.assign(element.style, textStyleToCss(style));
    element.style.position = 'absolute';
    // element.style.width = 'min-content';
    // element.style.height = 'min-content';

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
