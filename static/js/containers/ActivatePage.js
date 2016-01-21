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
  }

  componentWillReceiveProps(nextProps) {
    const { location: { query } } = this.props;

    if (nextProps.activation.status === FETCH_SUCCESS &&
      this.props.activation.status !== nextProps.activation.status) {
      setTimeout(() => {
        // After 3 seconds redirect to page the user was on before.
        window.location = query.redirect;
      }, 3000);
    }
  }

  render() {
    const { activation, location: { query }, dispatch } = this.props;
    let message;

    if (activation.status === FETCH_SUCCESS) {
      message = <span>
        Activation succeeded! Click <a href={query.redirect}>here</a> to
        return to the page you were on, or wait a few seconds.
      </span>;
    } else if (activation.status === FETCH_PROCESSING) {
      message = "Activation processing...";
    } else if (activation.status === FETCH_FAILURE) {
      message = "Activation failed.";
    }
    if (message) {
      dispatch(showSnackBar({ message: message, open: true }));
    }

    return <MessagePage
      message={message}
      error=""
      explanation=""
    />;
  }
}

ActivatePage.propTypes = {
  location: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  activation: React.PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    activation: state.activation
  };
};

export default connect(mapStateToProps)(ActivatePage);
