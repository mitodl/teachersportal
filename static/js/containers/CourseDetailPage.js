import React from 'react';
import CourseDetail from '../components/CourseDetail';
import {
  fetchCourse,
  fetchModules,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseDetailPage extends React.Component {

  componentDidMount() {
    this.fetchCoursesAndModules.call(this);
  }

  componentDidUpdate() {
    this.fetchCoursesAndModules.call(this);
  }

  fetchCoursesAndModules() {
    const {
      courseFetchStatus,
      modulesFetchStatus,
      authentication,
      dispatch,
      params: { uuid }
    } = this.props;

    if (authentication.isAuthenticated) {
      // When user is authenticated and we haven't fetched courses and modules
      // yet, fetch them now. This might execute the fetch action twice if
      // this component is refreshed before action has a chance to dispatch,
      // but that shouldn't cause any problems
      if (courseFetchStatus === undefined) {
        dispatch(fetchCourse(uuid));
      }
      if (modulesFetchStatus === undefined) {
        dispatch(fetchModules(uuid));
      }
    }
  }

  render() {
    const {
      course,
      modules,
      courseFetchStatus,
      modulesFetchStatus,
      authentication,
      } = this.props;

    let error;

    if (courseFetchStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about this course.";
    } else if (modulesFetchStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about the course's modules.";
    } else if (!authentication.isAuthenticated) {
      error = "Please log in to view the course information.";
    }

    let detail = <CourseDetail error={error} course={course} modules={modules} />;

    return <div>
      {detail}
      </div>
      ;
  }

}

const mapStateToProps = (state) => {
  return {
    course: state.courses.course,
    modules: state.courses.modules,
    courseFetchStatus: state.courses.courseFetchStatus,
    modulesFetchStatus: state.courses.modulesFetchStatus,
    authentication: state.authentication,
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
