import { replaceOnlyChildAndResetCssProperties } from '../componentManagement';
import { ComponentBase, ComponentState } from './componentBase';

export type RevealerState = ComponentState & {
    _type_: 'Revealer-builtin';
    header?: string | null;
    content?: number | string;
    is_expanded: boolean;
};

function expandRevealer(elem: HTMLElement): void {
    let header = elem.firstElementChild as HTMLElement;
    let contentOuter = elem.querySelector(
        '.rio-revealer-content-outer'
    ) as HTMLElement;
    let contentInner = contentOuter.firstElementChild as HTMLElement;

    // Do nothing if already expanded
    if (elem.classList.contains('expanded')) {
        return;
    }

    // Update the CSS to trigger the expand animation
    elem.classList.add('expanded');
    contentInner.style.transform = `translateY(0)`;
    contentInner.style.opacity = '1';

    // The components may currently be in flux due to a pending re-layout. If that
    // is the case, reading the `scrollHeight` would lead to an incorrect value.
    // Wait for the resize to finish before fetching it.
    requestAnimationFrame(() => {
        let contentHeight = contentInner.scrollHeight;
        let selfHeight = elem.scrollHeight;
        let headerHeight = header.scrollHeight;
        let targetHeight = Math.max(contentHeight, selfHeight - headerHeight);

        contentOuter.style.maxHeight = `${targetHeight}px`;
    });
}

function collapseRevealer(elem: HTMLElement): void {
    let contentOuter = elem.querySelector(
        '.rio-revealer-content-outer'
    ) as HTMLElement;
    let contentInner = contentOuter.firstElementChild as HTMLElement;

    // Do nothing if already collapsed
    if (!elem.classList.contains('expanded')) {
        return;
    }

    // Update the CSS to trigger the collapse animation
    let contentHeight = contentInner.scrollHeight;

    elem.classList.remove('expanded');
    contentOuter.style.maxHeight = '0';
    contentInner.style.transform = `translateY(-${contentHeight}px)`;
    contentInner.style.opacity = '0';
}

export class RevealerComponent extends ComponentBase {
    state: Required<RevealerState>;

    _createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('rio-revealer');

        element.innerHTML = `
<div class="rio-revealer-header">
    <div class="rio-revealer-label"></div>
    <div class="rio-icon-revealer-arrow"></div>
</div>
<div class="rio-revealer-content-outer rio-single-container">
    <div class="rio-revealer-content-inner rio-single-container"></div>
</div>
`;
        let header = element.querySelector(
            '.rio-revealer-header'
        ) as HTMLElement;

        // Listen for presses
        header.onmouseup = (e) => {
            // Notify the backend
            let is_expanded = element.classList.contains('expanded');

            this.setStateAndNotifyBackend({
                is_expanded: !is_expanded,
            });

            // Update the UI
            if (is_expanded) {
                collapseRevealer(element);
            } else {
                expandRevealer(element);
            }
        };

        // Make sure all CSS is set up for the collapsed state
        //
        // TODO: This doesn't seem to be working. The first time a revealer is
        // expanded, no animation is shown.
        requestAnimationFrame(() => {
            element.classList.add('expanded');
            collapseRevealer(element);
        });

        return element;
    }

    _updateElement(element: HTMLElement, deltaState: RevealerState): void {
        // Update the header
        if (deltaState.header === null) {
            let header = element.querySelector(
                '.rio-revealer-header'
            ) as HTMLElement;

            header.style.display = 'none';
        } else if (deltaState.header !== undefined) {
            let header = element.querySelector(
                '.rio-revealer-header'
            ) as HTMLElement;

            let label = header.querySelector(
                '.rio-revealer-label'
            ) as HTMLElement;

            header.style.removeProperty('display');
            label.innerText = deltaState.header;
        }

        // Update the child
        let contentInner = element.querySelector(
            '.rio-revealer-content-inner'
        ) as HTMLElement;
        replaceOnlyChildAndResetCssProperties(
            element.id,
            contentInner,
            deltaState.content
        );

        // Expand / collapse
        if (deltaState.is_expanded === true) {
            expandRevealer(element);
        } else if (deltaState.is_expanded === false) {
            collapseRevealer(element);
        }
    }
}
