import { replaceChildrenAndResetCssProperties } from '../componentManagement';
import { ComponentId } from '../models';
import { ComponentBase, ComponentState } from './componentBase';

export type FundamentalRootComponentState = ComponentState & {
    _type_: 'FundamentalRootComponent';
    child: ComponentId;
    connection_lost_component: ComponentId;
};

export class FundamentalRootComponent extends ComponentBase {
    state: Required<FundamentalRootComponentState>;

    _createElement(): HTMLElement {
        return document.createElement('div');
    }

    _updateElement(
        element: HTMLElement,
        deltaState: FundamentalRootComponentState
    ): void {
        replaceChildrenAndResetCssProperties(
            element.id,
            element,
            [deltaState.child, deltaState.connection_lost_component],
            true
        );

        for (let childElement of element.children) {
            childElement.classList.add('rio-single-container');
        }

        let connectionLostPopup = element.lastElementChild as HTMLElement;
        connectionLostPopup.id = 'rio-connection-lost-popup';
    }
}
