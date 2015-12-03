import React from 'react';
import Button from 'elemental/lib/components/Button';

class Navigation extends React.Component {
  render() {
    const { onShowSignIn } = this.props;

    return <div id="navigation">
    <button className="mdl-button mdl-js-button mdl-js-ripple-effect">Courses</button>
    <button className="mdl-button mdl-js-button mdl-js-ripple-effect">MIT's Pedagogy</button>
    <button className="mdl-button mdl-js-button mdl-js-ripple-effect">Resources & Teaching Guides</button>
    <button className="mdl-button mdl-js-button mdl-js-ripple-effect">About</button>
    <button className="mdl-button mdl-js-button mdl-button--raised mdl-button--colored mdl-js-ripple-effect" onClick={this.toggleModal}>Sign in</button>
    </div>;
  }
}

export default Navigation;
