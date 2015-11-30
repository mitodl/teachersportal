import React from 'react';
import Dialog from 'material-ui/lib/dialog';
import TextField from 'material-ui/lib/text-field';
import RaisedButton from 'material-ui/lib/raised-button';

class LoginModal extends React.Component {
  render() {
    const { onHideLoginModal, isOpen } = this.props;

    // TODO(abrahms): Get login actually hooked into actions / store.

    return <Dialog title="Sign in"
      open={isOpen}
      onRequestClose={onHideLoginModal}>
      <TextField hintText="Username" />
      <TextField hintText="Password" />
      <RaisedButton label="Sign In" primary={true}/>
      <RaisedButton label="Cancel" secondary={true} onClick={onHideLoginModal}/>
      </Dialog>;
  }
};

LoginModal.propTypes = {
  isOpen: React.PropTypes.bool.isRequired,
  onHideLoginModal: React.PropTypes.func.isRequired
};

export default LoginModal;
