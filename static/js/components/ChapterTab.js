import React from 'react';
import Table from 'material-ui/lib/table/table';
import TableBody from 'material-ui/lib/table/table-body';
import TableHeader from 'material-ui/lib/table/table-header';
import TableHeaderColumn from 'material-ui/lib/table/table-header-column';
import TableRow from 'material-ui/lib/table/table-row';
import TableRowColumn from 'material-ui/lib/table/table-row-column';

class ChapterTab extends React.Component {

  render() {
    const { selectable,
      fixedHeader,
      fixedFooter,
      stripedRows,
      showRowHover,
      deselectOnClickaway,
      height,
      product
    } = this.props;

    let rows = [];

    if (product) {
      rows = product.children.map((module, i) =>
        <TableRow key={module.upc}>
          <TableRowColumn>{i}: {module.title}</TableRowColumn>
        </TableRow>
      );
    }

    return <Table
      height={height}
      fixedHeader={fixedHeader}
      fixedFooter={fixedFooter}
      selectable={selectable}
      multiSelectable={selectable}
      onRowSelection={this._onRowSelection}>
      <TableHeader
        adjustForCheckbox={selectable}
        displaySelectAll={selectable}
        enableSelectAll={selectable}>
        <TableRow>
          <TableHeaderColumn colSpan="2" style={{textAlign: 'left'}}>
            Chapters
          </TableHeaderColumn>
        </TableRow>
      </TableHeader>
      <TableBody
        style={{textAlign: 'left'}}
        deselectOnClickaway={deselectOnClickaway}
        displayRowCheckbox={selectable}
        showRowHover={showRowHover}
        stripedRows={stripedRows}>
        {rows}
      </TableBody>
    </Table>
    ;
  }
}

export default ChapterTab;

ChapterTab.propTypes = {
  selectable: React.PropTypes.bool.isRequired,
  fixedHeader: React.PropTypes.bool,
  fixedFooter: React.PropTypes.bool,
  stripedRows: React.PropTypes.bool,
  showRowHover: React.PropTypes.bool,
  deselectOnClickaway: React.PropTypes.bool,
  height: React.PropTypes.string,
  product: React.PropTypes.object.isRequired
};
