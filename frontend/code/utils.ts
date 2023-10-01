
export function snakeToCamel(s: string): string {
    return s.replace(/(_\w)/g, function (m) {
        return m[1].toUpperCase();
    });
}
