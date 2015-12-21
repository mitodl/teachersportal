import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { connect } from 'react-redux';

import {
  showLogin,
  hideLogin,
  logout,
  login,
  loginFailure,
  register,
  registerFailure,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';

class App extends React.Component {
  render() {
    const {
      authentication,
      registration,
      loginModal,
      dispatch
    } = this.props;

    let content;

    if (registration.status === FETCH_FAILURE) {
      content = "An error occurred registering the user.";
    } else if (registration.status === FETCH_SUCCESS) {
      content = "User registered successfully! Check your email for an activation link.";
    } else {
      content = this.props.children;
    }

    return <div>
      <Header
        showSignIn={() => dispatch(showLogin())}
        hideSignIn={() => dispatch(hideLogin())}
        onSignOut={() => dispatch(logout())}
        signIn={this.signIn.bind(this)}
        register={this.register.bind(this)}
        authentication={authentication}
        reportLoginError={error => dispatch(loginFailure(error))}
        reportRegisterError={error => dispatch(registerFailure(error))}
        registration={registration}
        loginModal={loginModal}
      />
        {content}
      <Footer/>
    </div>;
  }

  signIn(username, password) {
    const { dispatch } = this.props;

    dispatch(login(username, password));
  }

  register(fullName, email, organization, password, redirect) {
    const { dispatch } = this.props;

    dispatch(register(fullName, email, organization, password, redirect));
  }
}

const mapStateToProps = (state) => {
  return {
    authentication: state.authentication,
    registration: state.registration,
    loginModal: state.loginModal,
  };
};

export default connect(mapStateToProps)(App);