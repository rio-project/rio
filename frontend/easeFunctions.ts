export function easeIn(a: number): number {
    return Math.pow(a, 2);
}

export function easeOut(a: number): number {
    return 1 - Math.pow(1 - a, 2);
}

export function easeInOut(a: number): number {
    // Map to the sine function's domain
    a = (a - 0.5) * Math.PI;

    // Apply the sine function
    a = Math.sin(a);

    // Map back to [0, 1]
    a = (a + 1) / 2;

    return a;
}
