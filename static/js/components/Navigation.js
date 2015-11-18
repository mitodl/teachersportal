import React from 'react';
import FlatButton from 'material-ui/lib/flat-button';

class Navigation extends React.Component {
  render() {
    return <div id="navigation">
        <FlatButton label="Courses" />
        <FlatButton label="MIT's Pedagogy" />
        <FlatButton label="Resources and Teaching Guides" />
        <FlatButton label="About" />
      </div>;
  }
}

export default Navigation;
