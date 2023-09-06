import { replaceOnlyChild } from './app';
import { WidgetBase, WidgetState } from './widgetBase';

export type RevealerState = WidgetState & {
    _type_: 'Revealer-builtin';
    label?: string;
    child?: number | string;
    is_expanded: boolean;
};

function expandRevealer(elem: HTMLElement): void {
    let contentOuter = elem.querySelector(
        '.reflex-revealer-content-outer'
    ) as HTMLElement;
    let contentInner = contentOuter.firstElementChild as HTMLElement;

    // Do nothing if already expanded
    if (elem.classList.contains('expanded')) {
        return;
    }

    // Update the CSS to trigger the expand animation
    let contentHeight = contentInner.scrollHeight;

    elem.classList.add('expanded');
    contentOuter.style.maxHeight = contentHeight + 'px';
    contentInner.style.transform = `translateY(0)`;
    contentInner.style.opacity = '1';
}

function collapseRevealer(elem: HTMLElement): void {
    let header = elem.firstElementChild as HTMLElement;
    let contentOuter = elem.querySelector(
        '.reflex-revealer-content-outer'
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

export class RevealerWidget extends WidgetBase {
    createElement(): HTMLElement {
        // Create the element
        let element = document.createElement('div');
        element.classList.add('expanded');
        element.classList.add('reflex-revealer');

        element.innerHTML = `
<div class="reflex-revealer-header">
    <div class="reflex-revealer-label"></div>
    <div class="reflex-revealer-arrow"></div>
</div>
<div class="reflex-revealer-content-outer">
    <div class="reflex-revealer-content-inner reflex-single-container"></div>
</div>
`;
        let header = element.querySelector(
            '.reflex-revealer-header'
        ) as HTMLElement;

        // Listen for presses
        header.onmouseup = (e) => {
            // Notify the backend
            let is_expanded = element.classList.contains('expanded');

            this.setStateAndNotifyBackend({
                is_expanded: !is_expanded,
            });

            // Update the UI
            // if (is_expanded) {
            //     collapseRevealer(element);
            // } else {
            //     expandRevealer(element);
            // }
        };

        return element;
    }

    updateElement(element: HTMLElement, deltaState: RevealerState): void {
        console.log(`Revealer updateElement`, deltaState.is_expanded);

        // Update the label
        if (deltaState.label !== undefined) {
            let label = element.querySelector(
                '.reflex-revealer-label'
            ) as HTMLElement;

            label.innerText = deltaState.label;
        }

        // Update the child
        let contentInner = element.querySelector(
            '.reflex-revealer-content-inner'
        ) as HTMLElement;
        replaceOnlyChild(contentInner, deltaState.child);

        // Expand / collapse
        if (deltaState.is_expanded === true) {
            expandRevealer(element);
        } else if (deltaState.is_expanded === false) {
            collapseRevealer(element);
        }
    }
}
