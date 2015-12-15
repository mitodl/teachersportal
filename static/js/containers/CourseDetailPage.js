import React from 'react';
import Header from '../components/Header';
import CourseDetail from '../components/CourseDetail';
import Footer from '../components/Footer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import {
  fetchCourse,
  fetchModules,
  showLogin,
  hideLogin,
  FETCH_FAILURE
} from '../actions/index_page';

class CourseDetailPage extends React.Component {

  componentDidMount() {
    const { dispatch, params: { uuid } } = this.props;

    dispatch(fetchCourse(uuid));
    dispatch(fetchModules(uuid));
  }

  render() {
    const {
      course,
      modules,
      courseFetchStatus,
      modulesFetchStatus,
      isLoginModalShowing,
      dispatch
      } = this.props;

    let error;

    if (courseFetchStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about this course.";
    } else if (modulesFetchStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about the course's modules.";
    }

    let detail;

    if (error !== undefined) {
      detail = <CourseDetail error={error} />;
    } else if (course !== undefined && modules !== undefined) {
      detail = <CourseDetail course={course} modules={modules} />;
    }

    return <div>
      <Header
        isLoginModalShowing={isLoginModalShowing}
        showSignIn={() => dispatch(showLogin())}
        hideSignIn={() => dispatch(hideLogin())}
      />
      {detail}
      <Footer/>
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
    isLoginModalShowing: state.showLoginModal
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
