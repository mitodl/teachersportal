import React from 'react';
import Navigation from '../components/Navigation';
import LoginModal from '../components/LoginModal';

class Header extends React.Component {
  render() {
    const {
      showSignIn,
      hideSignIn,
      loginModal,
      authentication,
      registration,
      onSignOut,
      signIn,
      register,
      reportLoginError,
      reportRegisterError,
    } = this.props;

    return <div id="header">
      <img src="/static/images/mit-white.png" className="logo" />
      <Navigation onShowSignIn={showSignIn} onSignOut={onSignOut} authentication={authentication} />

      <LoginModal
        isOpen={loginModal.visible}
        onHideLoginModal={hideSignIn}
        signIn={signIn}
        register={register}
        reportLoginError={reportLoginError}
        reportRegisterError={reportRegisterError}
        loginError={authentication.error}
        registerError={registration.error}
      />
      </div>;
  }
}

export default Header;
