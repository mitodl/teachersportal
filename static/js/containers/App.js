import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import SnackbarWrapper from '../components/SnackbarWrapper';
import RaisedButton from 'material-ui/lib/raised-button';
import { connect } from 'react-redux';

import {
  showLogin,
  hideLogin,
  showSnackBar,
  hideSnackBar,
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
      snackBar,
      dispatch,
    } = this.props;

    let content;
    let sbMessage;

    if (registration.status === FETCH_FAILURE) {
      sbMessage = "An error occurred registering the user.";
      dispatch(showSnackBar({ message: sbMessage }));
    } else if (registration.status === FETCH_SUCCESS) {
      sbMessage = "User registered successfully! Check your email for an activation link.";
      dispatch(showSnackBar({ message: sbMessage }));
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
      <SnackbarWrapper
        open={snackBar.open}
        message={snackBar.message}
        autoHideDuration={3000}
        onActionTouchTap={() => dispatch(hideSnackBar())}
        onRequestClose={() => dispatch(hideSnackBar())}
      />
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

App.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  authentication: React.PropTypes.object.isRequired,
  registration: React.PropTypes.object.isRequired,
  loginModal: React.PropTypes.object.isRequired,
  snackBar: React.PropTypes.object.isRequired,
};

const mapStateToProps = (state) => {
  return {
    authentication: state.authentication,
    registration: state.registration,
    loginModal: state.loginModal,
    snackBar: state.snackBar,
  };
};

export default connect(mapStateToProps)(App);
