import React from 'react';
import Header from '../components/Header';
import Body from '../components/Body';
import Footer from '../components/Footer';
import Immutable from 'immutable';
import { connect } from 'react-redux';

import {
  showLogin,
  hideLogin,
  fetchCourses,
  updateCourseSelection,
  updateCourseSelectAll
} from '../actions/index_page';

class Page extends React.Component {
  render() {
    const { courses, selectedCourses, dispatch, isLoginModalShowing} = this.props;

    return <div>
      <Header
        isLoginModalShowing={isLoginModalShowing}
        showSignIn={() => dispatch(showLogin())}
        hideSignIn={() => dispatch(hideLogin())}
      />
      <Body
        updateCoursesIfAbsent={this.updateCoursesIfAbsent.bind(this)}
        courses={courses}
        updateCourseSelection={(course, selected) => dispatch(updateCourseSelection(course, selected))}
        selectedCourses={selectedCourses}
        updateCourseSelectAll={(selected) => dispatch(updateCourseSelectAll(selected))}
      />
      <Footer/>
      </div>
      ;
  }

  updateCoursesIfAbsent() {
    const { hasCourses, isFetching, dispatch } = this.props;

    if (!hasCourses && !isFetching) {
      dispatch(fetchCourses()).
        then(() => dispatch(updateCourseSelectAll(true)));
    }
  }
}

const mapStateToProps = (state) => {
  return {
    isLoginModalShowing: state.showLoginModal,
    courses: state.courses.get("courses", Immutable.List()),
    hasCourses: state.courses.has("courses"),
    isFetching: state.courses.get("isFetching"),
    selectedCourses: state.courses.get("selectedCourses", Immutable.List())
  };
};

export default connect(mapStateToProps)(Page);
