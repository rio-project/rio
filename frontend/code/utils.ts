export function commitCss(element: HTMLElement): void {
    element.offsetHeight;
}

export function disableTransitions(element: HTMLElement) {
    element.style.transition = 'none';
    element.offsetHeight;
}

export function enableTransitions(element: HTMLElement) {
    element.style.removeProperty('transition');
    element.offsetHeight;
}

export function withoutTransitions(
    element: HTMLElement,
    func: () => void
): void {
    disableTransitions(element);

    func();

    enableTransitions(element);
}

/// Asynchronously sleeps for the given number of seconds.
export async function sleep(durationInSeconds: number): Promise<void> {
    await new Promise((resolve, reject) =>
        setTimeout(resolve, durationInSeconds * 1000)
    );
}

export function reprElement(element: Element): string {
    let chunks = [element.tagName.toLowerCase()];

    for (let attr of element.attributes) {
        chunks.push(`${attr.name}=${JSON.stringify(attr.value)}`);
    }

    return `<${chunks.join(' ')}>`;
}

/// Returns an array containing all numbers from `start` (inclusive) to `end`
/// (exclusive).
export function range(start: number, end: number): number[] {
    let result: number[] = [];

    for (let ii = start; ii < end; ii++) {
        result.push(ii);
    }

    return result;
}

/// Returns the first argument that isn't `undefined`.
export function firstDefined(...args: any[]): any {
    for (let arg of args) {
        if (arg !== undefined) {
            return arg;
        }
    }

    return undefined;
}
