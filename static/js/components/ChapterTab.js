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
      height
    } = this.props;

    return <Table
      height={this.props.height}
      fixedHeader={this.props.fixedHeader}
      fixedFooter={this.props.fixedFooter}
      selectable={selectable}
      multiSelectable={selectable}
      onRowSelection={this._onRowSelection}>
      <TableHeader
        adjustForCheckbox={selectable}
        displaySelectAll={selectable}
        enableSelectAll={selectable}>
        <TableRow>
          <TableHeaderColumn colSpan="2" style={{textAlign: 'left'}}>
            &nbsp;
          </TableHeaderColumn>
        </TableRow>
      </TableHeader>
      <TableBody
        style={{textAlign: 'left'}}
        deselectOnClickaway={this.props.deselectOnClickaway}
        displayRowCheckbox={selectable}
        showRowHover={this.props.showRowHover}
        stripedRows={this.props.stripedRows}>
        <TableRow>
          <TableRowColumn>0: Introduction</TableRowColumn>
        </TableRow>
        <TableRow>
          <TableRowColumn>1: Newton's Laws of Motion</TableRowColumn>
        </TableRow>
        <TableRow>
          <TableRowColumn>2: Interactions and Forces</TableRowColumn>
        </TableRow>
        <TableRow>
          <TableRowColumn>3: Applying Newton's Laws</TableRowColumn>
        </TableRow>
        <TableRow>
          <TableRowColumn>4: Kinematics, the Mathematical Description of Motion</TableRowColumn>
        </TableRow>
      </TableBody>
    </Table>
    ;
  }
}

export default ChapterTab;
