import React from 'react';
import { connect } from 'react-redux';
import MessagePage from '../components/MessagePage';
import {
  FETCH_SUCCESS,
  FETCH_PROCESSING,
  FETCH_FAILURE,
  activate,
  showSnackBar
} from '../actions/index_page';

class ActivatePage extends React.Component {
  componentDidMount() {
    const { dispatch, location: { query } } = this.props;
    let token = query.token;

    dispatch(activate(token));
    this.handleMessage.call(this);
  }

  componentDidUpdate() {
    this.handleMessage.call(this);
  }

  componentWillReceiveProps(nextProps) {
    const { location: { query } } = this.props;

    if (nextProps.activation.status === FETCH_SUCCESS &&
      this.props.activation.status !== nextProps.activation.status) {
      window.location = query.redirect;
    }
  }

  handleMessage() {
    const { activation, location: { query }, dispatch } = this.props;
    let message;

    if (activation.status === FETCH_SUCCESS) {
      message = "Activation succeeded!";
    } else if (activation.status === FETCH_PROCESSING) {
      message = "Activation processing...";
    } else if (activation.status === FETCH_FAILURE) {
      message = "Activation failed.";
    }
    if (message) {
      dispatch(showSnackBar({ message: message }));
    }
  }

  render() {
    const { message, location: { query } } = this.props;

    let redirectLink = "<a href=" + query.redirect + ">here</a>";
    let explanation = "Click " + redirectLink + " to return to the page you were on, or wait a few seconds.";

    return <MessagePage
      message={message}
      error=""
      explanation={explanation}
    />;
  }
}

ActivatePage.propTypes = {
  location: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  activation: React.PropTypes.object.isRequired,
  message: React.PropTypes.string
};

const mapStateToProps = (state) => {
  return {
    activation: state.activation,
    message: state.snackBar.message
  };
};

export default connect(mapStateToProps)(ActivatePage);
