import React, { PropTypes, Component } from 'react';

export default class Courses extends Component {
  render() {
    return <ul>
      {this.props.courses.map(course =>
        <li key={course.uuid}>{course.title}</li>
      )}
    </ul>;
  }
}

Courses.propTypes = {
  courses: PropTypes.array.isRequired
};
