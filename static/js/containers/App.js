import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import Snackbar from 'material-ui/lib/snackbar';
import RaisedButton from 'material-ui/lib/raised-button';
import { connect } from 'react-redux';

import {
  hideSnackBar,
  clearActivation,
  showLogin,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';

class App extends React.Component {

  componentDidMount() {
    this.showLoginAfterActivation.call(this);
  }

  componentDidUpdate() {
    this.showLoginAfterActivation.call(this);
  }

  showLoginAfterActivation() {
    const { dispatch, activation } = this.props;
    if (activation.status === FETCH_SUCCESS) {
      dispatch(clearActivation());
      dispatch(showLogin("Thanks for activating! You may now sign in."));
    }
  }

  render() {
    const {
      authentication,
      registration,
      loginModal,
      snackBar,
      history,
      dispatch
    } = this.props;

    let content = this.props.children;

    return <div>
      <Header
        dispatch={dispatch}
        authentication={authentication}
        registration={registration}
        loginModal={loginModal}
        history={history}
      />
      <div id="app-body">
        {content}
      </div>
      <Snackbar
        open={snackBar.open}
        message={snackBar.message}
        action="dismiss"
        autoHideDuration={0}
        onActionTouchTap={() => dispatch(hideSnackBar())}
        onRequestClose={() => dispatch(hideSnackBar())}
        bodyStyle={{ 'backgroundColor': 'rgba(100, 100, 100, 0.9)' }}
        className="snackbar"
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
    activation: state.activation,
    authentication: state.authentication,
    registration: state.registration,
    loginModal: state.loginModal,
    snackBar: state.snackBar
  };
};

export default connect(mapStateToProps)(App);
