let pixelsPerEm = 16;

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

type AugmentedNodeState = NodeState & {
    element: HTMLElement;
};

type AugmentedConnectionState = ConnectionState & {
    element: SVGPathElement;
};

class GraphStore {
    private nodes: AugmentedNodeState[];
    private connections: AugmentedConnectionState[];

    constructor() {
        this.nodes = [];
        this.connections = [];
    }

    addNode(node: AugmentedNodeState): void {
        this.nodes.push(node);
    }

    addConnection(conn: AugmentedConnectionState): void {
        this.connections.push(conn);
    }

    allNodes(): AugmentedNodeState[] {
        return this.nodes;
    }

    getNodeById(nodeId: number): AugmentedNodeState {
        for (let node of this.nodes) {
            if (node.id === nodeId) {
                return node;
            }
        }

        throw new Error(`NodeEditor has no node with id ${nodeId}`);
    }

    allConnections(): AugmentedConnectionState[] {
        return this.connections;
    }

    getConnectionsForNode(nodeId: number): AugmentedConnectionState[] {
        let result: AugmentedConnectionState[] = [];

        for (let conn of this.connections) {
            if (conn.fromNode === nodeId || conn.toNode === nodeId) {
                result.push(conn);
            }
        }

        return result;
    }
}

class DevelComponent {
    private htmlChild: HTMLElement;
    private svgChild: SVGSVGElement;

    private graphStore: GraphStore;

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
        // Create some nodes
        let rawNodes: NodeState[] = [
            {
                id: 1,
                title: 'Test Node',
                inputs: ['Input 1', 'Input 2'],
                outputs: ['Output 1'],
                left: 5,
                top: 5,
            },
            {
                id: 2,
                title: 'Test Node 2',
                inputs: ['Input 1', 'Input 2'],
                outputs: ['Output 1'],
                left: 20,
                top: 20,
            },
        ];

        let rawConnections: ConnectionState[] = [
            {
                id: 1,
                fromNode: 1,
                fromPort: 'Output 1',
                toNode: 2,
                toPort: 'Input 1',
            },
        ];

        // Create all nodes and add them to the graph store
        this.graphStore = new GraphStore();

        for (let node of rawNodes) {
            let nodeElement = this._makeNode(node);

            let augmentedNode = node as AugmentedNodeState;
            augmentedNode.element = nodeElement;
            this.graphStore.addNode(augmentedNode);
        }

        // Same again, for connections
        for (let conn of rawConnections) {
            let augmentedConn = this._makeConnection(conn);
            this.graphStore.addConnection(augmentedConn);
        }
    }

    _beginDrag(
        nodeState: NodeState,
        nodeElement: HTMLElement,
        event: MouseEvent
    ): boolean {
        // Make sure this node is on top
        nodeElement.style.zIndex = '1';

        // Accept the drag
        return true;
    }

    _dragMove(
        nodeState: NodeState,
        nodeElement: HTMLElement,
        event: MouseEvent
    ): void {
        // Update the node state
        nodeState.left += event.movementX / pixelsPerEm;
        nodeState.top += event.movementY / pixelsPerEm;

        // Move its element
        nodeElement.style.left = `${nodeState.left}rem`;
        nodeElement.style.top = `${nodeState.top}rem`;

        // Update any connections
        let connections = this.graphStore.getConnectionsForNode(nodeState.id);

        for (let conn of connections) {
            this._updateConnection(conn);
        }
    }

    _endDrag(
        nodeState: NodeState,
        nodeElement: HTMLElement,
        event: MouseEvent
    ): void {
        // The node no longer needs to be on top
        nodeElement.style.removeProperty('z-index');
    }

    _makeNode(nodeState: NodeState): HTMLElement {
        // Build the node HTML
        const nodeElement = document.createElement('div');
        nodeElement.dataset.nodeId = nodeState.id.toString();
        nodeElement.classList.add('rio-node-editor-node');
        nodeElement.style.left = `${nodeState.left}rem`;
        nodeElement.style.top = `${nodeState.top}rem`;
        nodeElement.style.width = `$25rem`;
        nodeElement.style.height = `$40rem`;
        this.htmlChild.appendChild(nodeElement);

        // Header
        const header = document.createElement('div');
        header.classList.add('rio-node-editor-node-header');
        header.innerText = nodeState.title;
        nodeElement.appendChild(header);

        // Body
        const body = document.createElement('div');
        body.classList.add('rio-node-editor-node-body');
        nodeElement.appendChild(body);

        // Inputs
        nodeState.inputs.forEach((input) => {
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
        nodeState.outputs.forEach((output) => {
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

        // Allow dragging the node
        // @ts-ignore
        this.rioWrapper.addDragHandler({
            element: header,
            onStart: (event: MouseEvent) =>
                this._beginDrag(nodeState, nodeElement, event),
            onMove: (event: MouseEvent) =>
                this._dragMove(nodeState, nodeElement, event),
            onEnd: (event: MouseEvent) =>
                this._endDrag(nodeState, nodeElement, event),
        });

        return nodeElement;
    }

    _makeConnection(
        connectionState: ConnectionState
    ): AugmentedConnectionState {
        // Create the SVG path. Don't worry about positioning it yet
        const svgPath = document.createElementNS(
            'http://www.w3.org/2000/svg',
            'path'
        ) as SVGPathElement;

        svgPath.setAttribute('stroke', '#999');
        svgPath.setAttribute('stroke-width', '0.2rem');
        svgPath.setAttribute('fill', 'none');
        this.svgChild.appendChild(svgPath);

        // Augment the connection state
        let augmentedConn = connectionState as AugmentedConnectionState;
        augmentedConn.element = svgPath;

        // Update the connection
        this._updateConnection(augmentedConn);

        return augmentedConn;
    }

    _updateConnection(connectionState: AugmentedConnectionState): void {
        // Get the port elements
        let node1 = this.graphStore.getNodeById(connectionState.fromNode);
        let node2 = this.graphStore.getNodeById(connectionState.toNode);

        let port1Element = node1.element.querySelector(
            '.rio-node-editor-output > *:first-child'
        ) as HTMLElement;

        let port2Element = node2.element.querySelector(
            '.rio-node-editor-input > *:first-child'
        ) as HTMLElement;

        const box1 = port1Element.getBoundingClientRect();
        const box2 = port2Element.getBoundingClientRect();

        // Calculate the start and end points
        const x1 = box1.left + box1.width / 2;
        const y1 = box1.top + box1.height / 2;

        const x4 = box2.left + box2.width / 2;
        const y4 = box2.top + box2.height / 2;

        // Control the curve's bend
        let signedDistance = x4 - x1;

        let minVelocity = 4 * pixelsPerEm;
        let maxVelocity = 15 * pixelsPerEm;

        let velocity = signedDistance * 0.5;
        velocity = Math.max(velocity, minVelocity);
        velocity = Math.min(velocity, maxVelocity);

        // Calculate the intermediate points
        const x2 = x1 + velocity;
        const y2 = y1;

        const x3 = x4 - velocity;
        const y3 = y4;

        // Update the SVG path
        connectionState.element.setAttribute(
            'd',
            `M${x1} ${y1} C ${x2} ${y2}, ${x3} ${y3}, ${x4} ${y4}`
        );
    }
}
