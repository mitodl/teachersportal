import React from 'react';
import FlatButton from 'material-ui/lib/flat-button';
import RaisedButton from 'material-ui/lib/raised-button';

class Navigation extends React.Component {
  render() {
    const { onShowSignIn, onSignOut, authentication } = this.props;

    let loginButton;

    if (authentication.isAuthenticated) {
      loginButton = <RaisedButton label="Sign Out" onClick={onSignOut} secondary={true}/>;
    } else {
      loginButton = <RaisedButton label="Sign In or Register" onClick={onShowSignIn} secondary={true}/>;
    }

    return <div id="navigation">
        <FlatButton label="Courses" />
        <FlatButton label="MIT's Pedagogy" />
        <FlatButton label="Resources and Teaching Guides" />
        <FlatButton label="About" />
      {loginButton}
      </div>;
  }
}

export default Navigation;
