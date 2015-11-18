import React from 'react';
import Navigation from '../components/Navigation';

class Header extends React.Component {
  render() {
    return <div id="header">
      <img src="/static/images/mit-white.png" className="logo" />
      <Navigation />
      </div>;
  }
}

export default Header;
