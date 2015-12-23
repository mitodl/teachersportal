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
      onSignOut,
      signIn,
    } = this.props;

    return <div id="header">
      <img src="/static/images/mit-white.png" className="logo" />
      <Navigation onShowSignIn={showSignIn} onSignOut={onSignOut} authentication={authentication} />

      <LoginModal
        isOpen={loginModal.visible}
        onHideLoginModal={hideSignIn}
        signIn={signIn}
        error={authentication.error}
      />
      </div>;
  }
}

export default Header;
