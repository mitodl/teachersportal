import React from 'react';
import CourseDetail from '../components/CourseDetail';
import Card from 'material-ui/lib/card/card';
import LinearProgress from 'material-ui/lib/linear-progress';
import {
  fetchCourse,
  fetchCourseList,
  clearInvalidCartItems,
  FETCH_FAILURE,
  FETCH_SUCCESS
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseDetailPage extends React.Component {

  componentDidMount() {
    this.fetchCourse.call(this, true);
  }

  componentDidUpdate() {
    this.fetchCourse.call(this);
  }

  // forceFetchCourse will trigger a fetch of the course, regardless
  // of if it's already been fetched.
  fetchCourse(forceFetchCourse = false) {
    const {
      course,
      dispatch,
      params: { uuid }
    } = this.props;

    // When user is authenticated and we haven't fetched courses and modules
    // yet, fetch them now. This might execute the fetch action twice if
    // this component is refreshed before action has a chance to dispatch,
    // but that shouldn't cause any problems

    if (forceFetchCourse || course.courseStatus === undefined) {
      dispatch(fetchCourse(uuid));
    }
    if (course.courseListStatus === undefined) {
      dispatch(fetchCourseList()).then(() => {
        return dispatch(clearInvalidCartItems());
      });
    }
  }

  render() {
    const {
      course
    } = this.props;

    let detail;
    // We should show the loading page if the course isn't loaded or
    // if there is an error.
    if (course.courseStatus !== FETCH_SUCCESS) {
      detail = <div id="course-body">
        <Card id="course-content">
          <LinearProgress mode="indeterminate" size="1" className="progress" />
        </Card>
      </div>;
    } else {
      detail = <CourseDetail
        authenticated={this.props.authentication.isAuthenticated}
        course={course.course}
        courseList={course.courseList}
      />;
    }

    return <div>
      {detail}
      </div>
      ;
  }
}

CourseDetailPage.propTypes = {
  course: React.PropTypes.object.isRequired,
  authentication: React.PropTypes.object.isRequired,
  snackBar: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  params: React.PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    course: state.course,
    authentication: state.authentication,
    snackBar: state.snackBar
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
