type NodeState = {
    id: number;
    title: string;
    inputs: string[];
    outputs: string[];
    left: number;
    top: number;
};

type ConnectionState = {
    id: number;
    fromNode: number;
    fromPort: string;
    toNode: number;
    toPort: string;
};

class GraphStore {
    private nodes: NodeState[];
    private connections: ConnectionState[];

    constructor() {
        this.nodes = [];
        this.connections = [];
    }

    addNode(node: NodeState): void {
        this.nodes.push(node);
    }

    addConnection(conn: ConnectionState): void {
        this.connections.push(conn);
    }

    getNodes(): NodeState[] {
        return this.nodes;
    }

    getConnections(): ConnectionState[] {
        return this.connections;
    }
}

class DevelComponent {
    private htmlChild: HTMLElement;
    private svgChild: SVGSVGElement;

    // Constructor
    createElement(): HTMLElement {
        let element = document.createElement('div');
        element.classList.add('rio-node-editor');
        element.innerHTML = `
            <svg></svg>
            <div></div>
        `;

        this.htmlChild = element.querySelector('div') as HTMLElement;
        this.svgChild = element.querySelector('svg') as SVGSVGElement;

        // Populate the graph for debugging
        requestAnimationFrame(() => {
            this.debugInit();
        });

        return element;
    }

    updateElement(deltaState: object): void {}

    debugInit(): void {
        let node1Element = this._makeNode(
            'Spawned',
            ['Input 1', 'Input 2'],
            ['Output 1'],
            2,
            3,
            4,
            5
        );

        let node2Element = this._makeNode(
            'Spawned 2',
            ['Input 1', 'Input 2'],
            ['Output 1'],
            36,
            17,
            8,
            9
        );

        const port1 = node1Element.querySelector(
            '.rio-node-editor-port'
        ) as HTMLElement;

        const port2 = node2Element.querySelector(
            '.rio-node-editor-port'
        ) as HTMLElement;

        this._makeConnection(port1, port2);
    }

    _makeNode(
        title: string,
        inputs: string[],
        outputs: string[],
        left: number,
        top: number,
        width: number,
        height: number
    ): HTMLElement {
        // Build the node HTML
        const node = document.createElement('div');
        node.classList.add('rio-node-editor-node');
        node.style.left = `${left}rem`;
        node.style.top = `${top}rem`;
        node.style.width = `${width}rem`;
        node.style.height = `${height}rem`;
        this.htmlChild.appendChild(node);

        // Header
        const header = document.createElement('div');
        header.classList.add('rio-node-editor-node-header');
        header.innerText = title;
        node.appendChild(header);

        // Body
        const body = document.createElement('div');
        body.classList.add('rio-node-editor-node-body');
        node.appendChild(body);

        // Inputs
        inputs.forEach((input) => {
            const portElement = document.createElement('div');
            portElement.classList.add(
                'rio-node-editor-port',
                'rio-node-editor-input'
            );
            body.appendChild(portElement);

            const circleElement = document.createElement('div');
            portElement.appendChild(circleElement);

            const labelElement = document.createElement('div');
            labelElement.innerText = input;
            labelElement.classList.add('rio-node-editor-port-label');
            portElement.appendChild(labelElement);
        });

        // Outputs
        outputs.forEach((output) => {
            const portElement = document.createElement('div');
            portElement.classList.add(
                'rio-node-editor-port',
                'rio-node-editor-output'
            );
            body.appendChild(portElement);

            const circleElement = document.createElement('div');
            portElement.appendChild(circleElement);

            const labelElement = document.createElement('div');
            labelElement.innerText = output;
            portElement.appendChild(labelElement);
        });

        return node;
    }

    _makeConnection(el1: HTMLElement, el2: HTMLElement): void {
        const path = document.createElementNS(
            'http://www.w3.org/2000/svg',
            'path'
        ) as SVGPathElement;
        path.setAttribute('stroke', '#999');
        path.setAttribute('stroke-width', '0.2rem');
        path.setAttribute('fill', 'none');
        this.svgChild.appendChild(path);

        this._updateConnection(path, el1, el2);
    }

    _updateConnection(
        conn: SVGPathElement,
        el1: HTMLElement,
        el2: HTMLElement
    ): void {
        const box1 = el1.getBoundingClientRect();
        const box2 = el2.getBoundingClientRect();

        const pixelsPerEm = 16; // TODO: Replace with rio's global

        const x1 = box1.left + box1.width / 2;
        const y1 = box1.top + box1.height / 2;

        const x4 = box2.left + box2.width / 2;
        const y4 = box2.top + box2.height / 2;

        const x2 = x1 + 15 * pixelsPerEm;
        const y2 = y1;

        const x3 = x4 - 15 * pixelsPerEm;
        const y3 = y4;

        console.debug(`Drawing connection from ${x1},${y1} to ${x4},${y4}`);

        conn.setAttribute(
            'd',
            `M${x1} ${y1} C ${x2} ${y2}, ${x3} ${y3}, ${x4} ${y4}`
        );
    }
}
