
import { colorToCssString, fillToCssString, textStyleToCss } from './cssUtils';
import { TextStyle, Theme } from './models';
import { snakeToCamel } from './utils';


export async function registerFont(name: string, urls: (string | null)[]): Promise<void> {
    const VARIATIONS = [
        { weight: 'normal', style: 'normal' },
        { weight: 'bold', style: 'normal' },
        { weight: 'normal', style: 'italic' },
        { weight: 'bold', style: 'italic' },
    ];

    let promises = new Map<string, Promise<FontFace>>();

    for (let [i, url] of urls.entries()) {
        if (url === null) {
            continue;
        }

        let fontFace = new FontFace(
            name,
            `url(${url})`,
            VARIATIONS[i],
        );
        promises.set(url, fontFace.load());
    }

    let numSuccesses = 0;
    let numFailures = 0;

    for (let [url, promise] of promises.entries()) {
        let fontFace: FontFace;
        try {
            fontFace = await promise;
        } catch (error) {
            numFailures++;
            console.warn(`Failed to load font file ${url}: ${error}`);
            continue;
        }

        numSuccesses++;
        document.fonts.add(fontFace);
    }

    if (numFailures === 0) {
        console.log(`Successfully registered all ${numSuccesses} variations of font ${name}`);
    } else if (numSuccesses === 0) {
        console.warn(`Failed to register all ${numFailures} variations of font ${name}`);
    } else {
        console.warn(`Successfully registered ${numSuccesses} variations of font ${name}, but failed to register ${numFailures} variations`);
    }
}


export function requestFileUpload(message: any): void {
    // Create a file upload input element
    let input = document.createElement('input');
    input.type = 'file';
    input.multiple = message.multiple;

    if (message.fileExtensions !== null) {
        input.accept = message.fileExtensions.join(',');
    }

    input.style.display = 'none';

    function finish() {
        // Don't run twice
        if (input.parentElement === null) {
            return;
        }

        // Build a `FormData` object containing the files
        const data = new FormData();

        let ii = 0;
        for (const file of input.files || []) {
            ii += 1;
            data.append('file_names', file.name);
            data.append('file_types', file.type);
            data.append('file_sizes', file.size.toString());
            data.append('file_streams', file, file.name);
        }

        // FastAPI has trouble parsing empty form data. Append a dummy value so
        // it's never empty
        data.append('dummy', 'dummy');

        // Upload the files
        fetch(message.uploadUrl, {
            method: 'PUT',
            body: data,
        });

        // Remove the input element from the DOM. Removing this too early causes
        // weird behavior in some browsers
        input.remove();
    }

    // Listen for changes to the input
    input.addEventListener('change', finish);

    // Detect if the window gains focus. This means the file upload dialog was
    // closed without selecting a file
    window.addEventListener(
        'focus',
        function () {
            // In some browsers `focus` fires before `change`. Give `change`
            // time to run first.
            this.window.setTimeout(finish, 500);
        },
        { once: true }
    );

    // Add the input element to the DOM
    document.body.appendChild(input);

    // Trigger the file upload
    input.click();
}


export function applyTheme(theme: Theme): void {
    let variables = {
        "--rio-global-corner-radius-small": `${theme.cornerRadiusSmall}rem`,
        "--rio-global-corner-radius-medium": `${theme.cornerRadiusMedium}rem`,
        "--rio-global-corner-radius-large": `${theme.cornerRadiusLarge}rem`,
        "--rio-global-shadow-radius": `${theme.shadowRadius}rem`,
    };

    // Theme Colors
    let colorNames = [
        "primary_color",
        "secondary_color",
        "disabled_color",
        "primary_color_variant",
        "secondary_color_variant",
        "disabled_color_variant",
        "background_color",
        "surface_color",
        "surface_color_variant",
        "surface_active_color",
        "success_color",
        "warning_color",
        "danger_color",
        "success_color_variant",
        "warning_color_variant",
        "danger_color_variant",
        "shadow_color",
        "heading_on_primary_color",
        "text_on_primary_color",
        "heading_on_secondary_color",
        "text_on_secondary_color",
        "text_color_on_light",
        "text_color_on_dark",
    ];

    for (let pyColorName of colorNames) {
        let cssColorName = `--rio-global-${pyColorName.replace("_", "-")}`;
        let jsColorName = snakeToCamel(pyColorName);

        let color = theme[jsColorName];
        variables[cssColorName] = colorToCssString(color);
    }

    // Text styles
    let styleNames = [
        "heading1",
        "heading2",
        "heading3",
        "text",
    ];

    for (let styleName of styleNames) {
        let style: TextStyle = theme[snakeToCamel(styleName) + 'Style'];
        let cssPrefix = `--rio-global-${styleName}`;

        for (let [name, value] of Object.entries(textStyleToCss(style))) {
            variables[`${cssPrefix}-${name}`] = value;
        }
    }

    // Colors that need to be extracted from styles
    // FIXME
    // variables["--rio-global-heading-on-surface-color"] = colorToCssString(theme.heading1Style.fill);
    // variables["--rio-global-text-on-surface-color"] = colorToCssString(theme.textStyle.fill);

    // Colors derived from, but not stored in the theme
    let derivedColors = {
        "text-on-success-color": theme.textOnSuccessColor,
        "text-on-warning-color": theme.textOnWarningColor,
        "text-on-danger-color": theme.textOnDangerColor,
    };

    for (let [css_name, color] of Object.entries(derivedColors)) {
        variables[`--rio-global-${css_name}`] = colorToCssString(color);
    }

    for (let [name, value] of Object.entries(variables)) {
        document.documentElement.style.setProperty(name, value);
    }

    // Assign to the html's `data-theme` attribute. This is used to dynamically
    // switch highlight.js themes.
    document.documentElement.setAttribute("data-theme", theme.variant);
}
