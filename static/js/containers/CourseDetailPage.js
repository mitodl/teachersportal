import React from 'react';
import CourseDetail from '../components/CourseDetail';
import Card from 'material-ui/lib/card/card';
import LinearProgress from 'material-ui/lib/linear-progress';
import {
  fetchCourse,
  fetchCourseList,
  clearInvalidCartItems,
  showSnackBar,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseDetailPage extends React.Component {

  componentDidMount() {
    this.fetchCourse.call(this);
    this.handleError.call(this);
  }

  componentDidUpdate() {
    this.fetchCourse.call(this);
    this.handleError.call(this);
  }

  fetchCourse() {
    const {
      course,
      authentication,
      dispatch,
      params: { uuid }
    } = this.props;

    if (authentication.isAuthenticated) {
      // When user is authenticated and we haven't fetched courses and modules
      // yet, fetch them now. This might execute the fetch action twice if
      // this component is refreshed before action has a chance to dispatch,
      // but that shouldn't cause any problems

      if (course.courseStatus === undefined) {
        dispatch(fetchCourse(uuid));
      }
      if (course.courseListStatus === undefined) {
        dispatch(fetchCourseList()).then(() => {
          return dispatch(clearInvalidCartItems());
        });
      }
    }
  }

  render() {
    const {
      course
    } = this.props;

    let detail;
    if (course.course === undefined) {
      detail = <div id="course-body">
        <Card id="course-content">
          <LinearProgress mode="indeterminate" size="1" className="progress" />
        </Card>
      </div>;
    } else {
      detail = <CourseDetail
        course={course.course}
        courseList={course.courseList}
      />;
    }

    return <div>
      {detail}
      </div>
      ;
  }


  handleError() {
    const { course, dispatch, authentication } = this.props;

    let error;

    if (course.courseStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about this course.";
    } else if (course.courseListStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about other courses.";
    } else if (!authentication.isAuthenticated) {
      error = "Please log in to view the course information.";
    }
    if (error) {
      dispatch(showSnackBar({ message: error }));
    }
  }
}

CourseDetailPage.propTypes = {
  course: React.PropTypes.object.isRequired,
  authentication: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  params: React.PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    course: state.course,
    authentication: state.authentication
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
