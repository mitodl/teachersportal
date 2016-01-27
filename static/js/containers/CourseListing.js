import React from 'react';
import Card from 'material-ui/lib/card/card';
import CourseCard from '../components/CourseCard';
import {
  fetchCourseList,
  clearInvalidCartItems,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseListing extends React.Component {

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

    return <Card id="course-body" style={{ 'backgroundColor': "#eee" }}>
      <h2 className="course-listing-header">Use MIT's courses in your teachings</h2>
      <ul className="course-listing">
        {list}
      </ul>
      </Card>;
  }
}

CourseListing.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  course: React.PropTypes.object.isRequired,
};

const mapStateToProps = (state) => {
  return {
    course: state.course,
  };
};

export default connect(mapStateToProps)(CourseListing);
