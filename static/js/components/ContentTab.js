import React from 'react';

class ContentTab extends React.Component {
  constructor(props) {
    super(props);

    props.updateCoursesIfAbsent();
  }

  render() {
    const { courses, selectedCourses, updateCourseSelection } = this.props;

    let rows = courses.map(course => {
      const checked = selectedCourses.has(course);

      return <tr
        key={course.get('uuid')}
      >
        <td>{course.get('title')}</td>
        <td>{course.get('price_per_seat_cents')}</td>
        <td>
          <input type="checkbox" checked={checked} onChange={() => updateCourseSelection(course, !checked)} />
        </td>
        <td>$10</td>
        <td>

        </td>
      </tr>;
    });


    return <table style={{width: "100%"}}>
      <thead>
        <tr>
        <th className="pricing-column">
          Manage Pricing
        </th>
        <th>
          Published Price Per Seat
        </th>
        <th>
          Available<br />
          <a href="#" onClick={this.selectAllCourses.bind(this)}>Select All</a>
        </th>
        <th>
          Set Price
        </th>
        <th />
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>;
  }

  selectAllCourses(e) {
    e.preventDefault();

    this.props.updateCourseSelectAll(true);
  }
}

export default ContentTab;