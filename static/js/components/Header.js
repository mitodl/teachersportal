import React from 'react';
import Navigation from '../components/Navigation';
import LoginModal from '../components/LoginModal';
import {
  showLogin,
  hideLogin,
  logout,
  login,
  loginFailure,
  register,
  registerFailure,
} from '../actions/index_page';

class Header extends React.Component {
  render() {
    const {
      dispatch,
      loginModal,
      authentication,
      registration,
    } = this.props;

    return <div id="header">
      <img src="/static/images/mit-white.png" className="logo" />
      <Navigation
        onShowSignIn={() => dispatch(showLogin())}
        onSignOut={() => dispatch(logout())}
        authentication={authentication} />

      <LoginModal
        isOpen={loginModal.visible}
        onHideLoginModal={() => dispatch(hideLogin())}
        signIn={this.signIn.bind(this)}
        register={this.register.bind(this)}
        reportLoginError={error => dispatch(loginFailure(error))}
        reportRegisterError={error => dispatch(registerFailure(error))}
        loginError={authentication.error}
        registerError={registration.error}
      />
      </div>;
  }

  signIn(username, password) {
    const { dispatch } = this.props;

    dispatch(login(username, password)).then(() => {
      dispatch(hideLogin());
    });
  }

  register(fullName, email, organization, password, redirect) {
    const { dispatch } = this.props;

    dispatch(register(fullName, email, organization, password, redirect)).then(() => {
      dispatch(hideLogin());
    });
  }

}

export default Header;

Header.propTypes = {
  loginModal: React.PropTypes.object.isRequired,
  authentication: React.PropTypes.object.isRequired,
  registration: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired
};
