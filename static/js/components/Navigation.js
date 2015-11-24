import React from 'react';
import FlatButton from 'material-ui/lib/flat-button';
import RaisedButton from 'material-ui/lib/raised-button';

class Navigation extends React.Component {
  render() {
    const { onShowSignIn } = this.props;

    return <div id="navigation">
        <FlatButton label="Courses" />
        <FlatButton label="MIT's Pedagogy" />
        <FlatButton label="Resources and Teaching Guides" />
        <FlatButton label="About" />
        <RaisedButton label="Sign In" onClick={onShowSignIn} secondary={true}/>
      </div>;
  }
}

export default Navigation;
