import { ComponentBase, ComponentState } from './componentBase';

type TableValue = number | string;

export type TableState = ComponentState & {
    data?: {string: TableValue[]};
};

export class TableComponent extends ComponentBase {
    state: Required<TableState>;

    private tableHeader: HTMLElement;
    private tableBody: HTMLElement;

    _createElement(): HTMLElement {
        let element = document.createElement('table');
        element.classList.add('rio-table');

        this.tableHeader = document.createElement('thead');
        element.appendChild(this.tableHeader);

        this.tableBody = document.createElement('tbody');
        element.appendChild(this.tableBody);

        return element;
    }

    _updateElement(element: HTMLTableElement, deltaState: TableState): void {
        if (deltaState.data !== undefined) {
            this.replaceData(deltaState.data);
        }
    }

    private replaceData(data: {string: TableValue[]}): void {
        // Figure out if only the data in the table changed, or if the columns
        // changed as well. If only the data changed, we'll preserve the current
        // sort order.
        let preserveSort: boolean;
        if (this.state.data === undefined){
            preserveSort = false;
        } else {
            // Note: JS sorts object keys, so the order of the columns doesn't
            // affect this comparison
            preserveSort = Object.keys(data) === Object.keys(this.state.data);
        }

        let sortColumn: string | null = null;
        let sortColumnIndex: number = -1;
        let sortReverse: boolean = false;
        if (preserveSort){
            let i = 0;
            for (let headerCell of this.tableHeader.getElementsByTagName('th')){
                if (headerCell.dataset.sort !== undefined){
                    sortColumn = Object.keys(this.state.data)[i];
                    sortColumnIndex = i;
                    sortReverse = headerCell.dataset.sort === 'desc';
                    break
                }
                i++;
            }
        }

        // Now actually replace the data in the table
        this.tableHeader.innerHTML = '';
        this.tableBody.innerHTML = '';

        let numRows = 0;
        let columnValues: TableValue[][] = [];
        let columnAlignments: string[] = [];

        let headerRow = document.createElement('tr');
        this.tableHeader.appendChild(headerRow);

        for (let [columnName, values] of Object.entries(data)) {
            let headerCell = document.createElement('th');
            headerCell.addEventListener('click', this.onHeaderClick.bind(this, columnName));
            headerRow.appendChild(headerCell);

            let headerText = document.createElement('span');
            headerText.innerText = columnName;
            headerCell.appendChild(headerText);

            let sortIndicator = document.createElement('span');
            headerCell.appendChild(sortIndicator);

            numRows = Math.max(numRows, values.length);
            columnValues.push(values);

            if (values.length === 0 || typeof values[0] === 'number') {
                columnAlignments.push('right');
            } else {
                columnAlignments.push('left');
            }
        }
        
        for (let row = 0; row < numRows; row++) {
            let rowElement = document.createElement('tr');

            for (let [i, values] of columnValues.entries()) {
                let cellElement = document.createElement('td');
                cellElement.innerText = values[row].toString();
                cellElement.style.textAlign = columnAlignments[i];
                rowElement.appendChild(cellElement);
            }

            this.tableBody.appendChild(rowElement);
        }

        // Restore the sorting
        // TODO: Sorting by just 1 column isn't enough to reproduce the same
        // order we've had before. Sorting by Y is not the same thing as sorting
        // by X and then by Y. We would have to keep track of all the sorting
        // the user has done.
        if (!preserveSort){
            return;
        }

        let headerCell = this.tableHeader.getElementsByTagName('th')[sortColumnIndex];
        this.applySort(data, sortColumn!, headerCell, sortReverse);
    }

    private onHeaderClick(columnName: string, event: MouseEvent): void {
        let clickedHeader = event.target as HTMLElement;
        if (clickedHeader.tagName !== 'TH') {
            clickedHeader = clickedHeader.parentElement!;
        }

        let reverse = clickedHeader.dataset.sort === 'asc';
        
        this.applySort(this.state.data, columnName, clickedHeader, reverse)
    }

    private applySort(data: {string: TableValue[]}, columnName: string, headerCell: HTMLElement, reverse: boolean): void {
        // Remove the `data-sort` attribute from all other headers
        for (let th of this.tableHeader.getElementsByTagName('th')) {
            delete th.dataset.sort;
        }
        headerCell.dataset.sort = reverse? 'desc' : 'asc';

        // If the sort order was toggled, we will still sort the rows and not
        // just reverse them. This ensures that the sort order is stable.
        let indices = argsort(data[columnName], reverse);

        for (let [columnName, values] of Object.entries(data)){
            data[columnName] = indices.map(i => values[i]);
        }

        let rows = [...this.tableBody.getElementsByTagName('tr')];
        for (let i of indices) {
            this.tableBody.appendChild(rows[i]);
        }
    }
}

function argsort(values: any[], reverse: boolean = false): number[] {
    if (values.length === 0) {
        return [];
    }

    let cmp: (i: number, j: number) => number;
    if (typeof values[0] === 'number') {
        cmp = (i, j) => values[i] - values[j];
    } else {
        cmp = (i, j) => values[i].localeCompare(values[j]);
    }

    let realCmp = reverse? (i: number, j: number) => -cmp(i, j) : cmp;

    let indices = [...values.keys()];
    indices.sort(realCmp);
    return indices;
}
