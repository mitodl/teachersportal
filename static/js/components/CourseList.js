import React from 'react';
import Card from 'material-ui/lib/card/card';
import CourseCard from '../components/CourseCard';
import {
  fetchCourseList,
  clearInvalidCartItems,
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseList extends React.Component {

  componentDidMount() {
    this.fetchCourseList();
  }

  componentDidUpdate() {
    this.fetchCourseList();
  }

  fetchCourseList() {
    const { course, dispatch } = this.props;
    if (course.courseListStatus === undefined) {
      dispatch(fetchCourseList()).then(() => {
        return dispatch(clearInvalidCartItems());
      });
    }
  }

  render() {
    const { course } = this.props;

    let list = course.courseList.map((course) => {
      return <li className="course-card-item" key={course.uuid}>
        <CourseCard course={course} />
      </li>;
    });

    return <div className="course-list-container">
        <ul className="course-listing">
          {list}
        </ul>
      </div>;
  }
};

CourseList.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  course: React.PropTypes.object.isRequired
};

export default CourseList;
