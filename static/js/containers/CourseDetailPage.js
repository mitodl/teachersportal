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
  logout,
  login,
  FETCH_FAILURE,
} from '../actions/index_page';

class CourseDetailPage extends React.Component {

  componentDidMount() {
    const {
      dispatch,
      authentication,
      params: { uuid }
    } = this.props;

    if (authentication.isAuthenticated) {
      dispatch(fetchCourse(uuid));
      dispatch(fetchModules(uuid));
    }
  }

  render() {
    const {
      course,
      modules,
      courseFetchStatus,
      modulesFetchStatus,
      loginModal,
      authentication,
      dispatch
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
      <Header
        showSignIn={() => dispatch(showLogin())}
        hideSignIn={() => dispatch(hideLogin())}
        onSignOut={() => dispatch(logout())}
        signIn={this.signIn.bind(this)}
        authentication={authentication}

        loginModal={loginModal}
      />
      {detail}
      <Footer/>
      </div>
      ;
  }

  signIn(username, password) {
    const {
      dispatch,
      courseFetchStatus,
      modulesFetchStatus,
      params: { uuid }
    } = this.props;

    dispatch(login(username, password)).
      then(() => {
        if (courseFetchStatus === undefined) {
          dispatch(fetchCourse(uuid));
        }
        if (modulesFetchStatus === undefined) {
          dispatch(fetchModules(uuid));
        }
      });
  }
}

const mapStateToProps = (state) => {
  return {
    course: state.courses.course,
    modules: state.courses.modules,
    courseFetchStatus: state.courses.courseFetchStatus,
    modulesFetchStatus: state.courses.modulesFetchStatus,
    authentication: state.authentication,
    loginModal: state.loginModal,
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
