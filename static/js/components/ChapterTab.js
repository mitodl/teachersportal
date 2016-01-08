import React from 'react';
import Table from 'material-ui/lib/table/table';
import TableBody from 'material-ui/lib/table/table-body';
import TableHeader from 'material-ui/lib/table/table-header';
import TableHeaderColumn from 'material-ui/lib/table/table-header-column';
import TableRow from 'material-ui/lib/table/table-row';
import TableRowColumn from 'material-ui/lib/table/table-row-column';

class ChapterTab extends React.Component {

  render() {
    const {
      className,
      selectable,
      fixedHeader,
      fixedFooter,
      stripedRows,
      showRowHover,
      deselectOnClickaway,
      height,
      product,
      buyTab
    } = this.props;

    let rows = [];

    if (product) {
      rows = product.children.map((module, i) => {
        let selected = false;
        if (buyTab !== undefined &&
          buyTab.selectedChapters.find(upc => upc === module.upc) !== undefined) {
          selected = true;
        }

        if (selectable === true) {
          return <TableRow key={module.upc} selected={selected}>
            <TableRowColumn>{module.title}</TableRowColumn>
            <TableRowColumn>${module.price_without_tax} / seat</TableRowColumn>
          </TableRow>;
        } else {
          return <TableRow key={module.upc} selected={selected}>
            <TableRowColumn>{module.title}</TableRowColumn>
          </TableRow>;
        }
      });
    }

    let allRowsSelected = false;
    if (buyTab !== undefined) {
      allRowsSelected = buyTab.allRowsSelected;
    }

    return <Table
      height={height}
      className={className}
      fixedHeader={fixedHeader}
      fixedFooter={fixedFooter}
      selectable={selectable}
      multiSelectable={selectable}
      onRowSelection={this._onRowSelection.bind(this)}
      allRowsSelected={allRowsSelected}
    >
      <TableHeader
        adjustForCheckbox={selectable}
        displaySelectAll={selectable}
        enableSelectAll={selectable}>
        <TableRow>
          <TableHeaderColumn colSpan="3"></TableHeaderColumn>
        </TableRow>
      </TableHeader>
      <TableBody
        deselectOnClickaway={deselectOnClickaway}
        displayRowCheckbox={selectable}
        showRowHover={showRowHover}
        stripedRows={stripedRows}>
        {rows}
      </TableBody>
    </Table>
    ;
  }

  _onRowSelection(selectedRows) {
    const { product, updateSelectedChapters } = this.props;
    // dispatch action to update global state with the currently selected modules, number of seats
    let upcs = [], allRowsSelected = false;

    if (selectedRows === 'all') {
      allRowsSelected = true;
      upcs = Array.from(product.children, child => child.upc);
    } else {
      // Workaround for material-ui quirk
      selectedRows = selectedRows.filter(i => i !== undefined);
      upcs = selectedRows.map(i => product.children[i].upc);
    }
    updateSelectedChapters(upcs, allRowsSelected);
  }
}

export default ChapterTab;

ChapterTab.propTypes = {
  selectable: React.PropTypes.bool.isRequired,
  buyTab: React.PropTypes.object,  // Only exists if selectable=true
  updateSelectedChapters: React.PropTypes.func,  // Only exists if selectable=true
  fixedHeader: React.PropTypes.bool,
  fixedFooter: React.PropTypes.bool,
  stripedRows: React.PropTypes.bool,
  showRowHover: React.PropTypes.bool,
  deselectOnClickaway: React.PropTypes.bool,
  height: React.PropTypes.string,
  product: React.PropTypes.object.isRequired,
};
