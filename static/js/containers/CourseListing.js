import React from 'react';
import Card from 'material-ui/lib/card/card';
import CourseCard from '../components/CourseCard';
import CourseList from '../components/CourseList';
import {
  fetchCourseList,
  clearInvalidCartItems,
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseListing extends React.Component {
  render() {
    const { dispatch, course } = this.props;

    return <Card id="course-listing">
      <CourseList dispatch={dispatch} course={course} />
      </Card>;
  }
}

CourseListing.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  course: React.PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    course: state.course
  };
};

export default connect(mapStateToProps)(CourseListing);
