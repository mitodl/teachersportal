import React from 'react';
import Snackbar from 'material-ui/lib/snackbar';

class SnackbarWrapper extends React.Component {
  shouldComponentUpdate(nextProps, nextState) {
    if (nextProps.message === this.props.message && nextProps.open) {
      // Message has already been seen
      return false;
    }
    return true;
  }

  render() {
    return <Snackbar {...this.props} />;
  }
}

export default SnackbarWrapper;
