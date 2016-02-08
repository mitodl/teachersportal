import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Snackbar from 'material-ui/lib/snackbar';
import RaisedButton from 'material-ui/lib/raised-button';
import { connect } from 'react-redux';

import {
  showSnackBar,
  hideSnackBar,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';

class App extends React.Component {

  componentDidMount() {
    this.handleMessage.call(this);
  }

  componentDidUpdate() {
    this.handleMessage.call(this);
  }

  handleMessage() {
    const {
      registration,
      dispatch,
      snackBar,
    } = this.props;

    let message;

    if (registration.status === FETCH_FAILURE) {
      message = "An error occurred registering the user.";
    } else if (registration.status === FETCH_SUCCESS) {
      message = "User registered successfully! Check your email for an activation link.";
    }

    // If message is already displayed don't display it again to avoid recursion
    if (message !== undefined && message !== snackBar.message) {
      dispatch(showSnackBar({message: message}));
    }
  }

  render() {
    const {
      authentication,
      registration,
      loginModal,
      snackBar,
      dispatch
    } = this.props;

    let content = this.props.children;

    return <div>
      <Header
        dispatch={dispatch}
        authentication={authentication}
        registration={registration}
        loginModal={loginModal}
      />
        {content}
      <Snackbar
        open={snackBar.open}
        message={snackBar.message}
        autoHideDuration={3000}
        onActionTouchTap={() => dispatch(hideSnackBar())}
        onRequestClose={() => dispatch(hideSnackBar())}
        bodyStyle={{ 'backgroundColor': 'rgba(100, 100, 100, 0.9)' }}
      />
      <Footer/>
    </div>;
  }
}

App.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  authentication: React.PropTypes.object.isRequired,
  registration: React.PropTypes.object.isRequired,
  loginModal: React.PropTypes.object.isRequired,
  snackBar: React.PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    authentication: state.authentication,
    registration: state.registration,
    loginModal: state.loginModal,
    snackBar: state.snackBar
  };
};

export default connect(mapStateToProps)(App);
