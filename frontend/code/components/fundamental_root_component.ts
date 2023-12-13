import { replaceChildren } from '../componentManagement';
import { ComponentId } from '../models';
import { setConnectionLostPopupVisible } from '../rpc';
import { ComponentState } from './componentBase';
import { SingleContainer } from './singleContainer';

export type FundamentalRootComponentState = ComponentState & {
    _type_: 'FundamentalRootComponent';
    child: ComponentId;
    connection_lost_component: ComponentId;
};

export class FundamentalRootComponent extends SingleContainer {
    state: Required<FundamentalRootComponentState>;

    createElement(): HTMLElement {
        return document.createElement('div');
    }

    updateElement(
        element: HTMLElement,
        deltaState: FundamentalRootComponentState
    ): void {
        replaceChildren(element.id, element, [
            deltaState.child,
            deltaState.connection_lost_component,
        ]);

        let connectionLostPopup = element.lastElementChild as HTMLElement;
        connectionLostPopup.classList.add('rio-connection-lost-popup');

        setConnectionLostPopupVisible(false);
    }
}
