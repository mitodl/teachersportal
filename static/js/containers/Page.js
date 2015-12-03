import React from 'react';
import Header from '../components/Header';
import Body from '../components/Body';
import Footer from '../components/Footer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { fetchCourses, showLogin, hideLogin } from '../actions/index_page';

class Page extends React.Component {
  render() {
    const {
      courses, dispatch, isLoginModalShowing
    } = this.props;

    return <div>
      <Header
        isLoginModalShowing={isLoginModalShowing}
        showSignIn={() => dispatch(showLogin())}
        hideSignIn={() => dispatch(hideLogin())}
      />
      <Body
        updateCourses={() => dispatch(fetchCourses())}
        courses={courses}
      />
      <Footer/>
      </div>
      ;
  }
}

const mapStateToProps = (state) => {
  return {
    courses: state.courses.courses,
    isLoginModalShowing: state.showLoginModal
  };
};

export default connect(mapStateToProps)(Page);
