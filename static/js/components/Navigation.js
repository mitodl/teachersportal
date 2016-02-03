import React from 'react';
import FlatButton from 'material-ui/lib/flat-button';
import RaisedButton from 'material-ui/lib/raised-button';
import IconMenu from 'material-ui/lib/menus/icon-menu';
import MenuItem from 'material-ui/lib/menus/menu-item';
import IconButton from 'material-ui/lib/icon-button';
import MenuIcon from 'material-ui/lib/svg-icons/navigation/menu';
import { Link } from 'react-router';

class Navigation extends React.Component {
  render() {
    const { onShowSignIn, onSignOut, authentication } = this.props;

    let loginButton;

    if (authentication.isAuthenticated) {
      loginButton = <div className="login-info">
        {authentication.name}
        <IconMenu
          className="user-settings"
          iconButtonElement={<IconButton><MenuIcon /></IconButton>}>
          <MenuItem primaryText="Sign Out" onClick={onSignOut} />
        </IconMenu>
        </div>;
    } else {
      loginButton = <RaisedButton label="Sign In or Register" onClick={onShowSignIn} secondary={true}/>;
    }

    return <div id="navigation">
      <div className="left-nav">
      <h1 className="logo"><Link to="/">MIT Courseware Marketplace</Link></h1>
      <Link to="/courses" className="nav-link">Courses</Link>
      </div>
      <div className="right-nav">
        {loginButton}
      </div>
      </div>;
  }
}

Navigation.propTypes = {
  onShowSignIn: React.PropTypes.func.isRequired,
  onSignOut: React.PropTypes.func.isRequired,
  authentication: React.PropTypes.object.isRequired
};

export default Navigation;
