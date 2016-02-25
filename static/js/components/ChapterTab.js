import React from 'react';
import Table from 'material-ui/lib/table/table';
import TableBody from 'material-ui/lib/table/table-body';
import TableHeader from 'material-ui/lib/table/table-header';
import TableHeaderColumn from 'material-ui/lib/table/table-header-column';
import TableRow from 'material-ui/lib/table/table-row';
import TableRowColumn from 'material-ui/lib/table/table-row-column';
import { formatDollars } from '../util/util';

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
      course,
      buyTab
    } = this.props;

    let rows = [];

    if (course) {
      rows = course.modules.map(module => {
        let selected = false;
        if (buyTab !== undefined &&
          buyTab.selectedChapters.find(uuid => uuid === module.uuid) !== undefined) {
          selected = true;
        }

        if (selectable === true) {
          return <TableRow key={module.uuid} selected={selected}>
            <TableRowColumn>{module.title}</TableRowColumn>
            <TableRowColumn>{formatDollars(module.price_without_tax)} / seat</TableRowColumn>
          </TableRow>;
        } else {
          return <TableRow key={module.uuid} selected={selected}>
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
    const { course, updateSelectedChapters } = this.props;
    // dispatch action to update global state with the currently selected modules, number of seats
    let uuids = [], allRowsSelected = false;

    if (selectedRows === 'all') {
      allRowsSelected = true;
      uuids = Array.from(course.modules, child => child.uuid);
    } else {
      // Workaround for material-ui quirk
      selectedRows = selectedRows.filter(i => i !== undefined);
      uuids = selectedRows.map(i => course.modules[i].uuid);
    }
    updateSelectedChapters(uuids, allRowsSelected);
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
  course: React.PropTypes.object.isRequired,
};
