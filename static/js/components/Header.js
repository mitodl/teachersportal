import React from 'react';
import Navigation from '../components/Navigation';
import LoginModal from '../components/LoginModal';

class Header extends React.Component {
  render() {
    const { showSignIn, hideSignIn, isLoginModalShowing } = this.props;
    return <div id="header">
      <img src="/static/images/mit-white.png" className="logo" />
      <Navigation onShowSignIn={showSignIn} />
      <LoginModal />
      </div>;
  }
}

export default Header;
