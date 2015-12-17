import React from 'react';
import ReactDOM from 'react-dom';
import Dialog from 'material-ui/lib/dialog';
import TextField from 'material-ui/lib/text-field';
import RaisedButton from 'material-ui/lib/raised-button';

class LoginModal extends React.Component {
  render() {
    const {
      onHideLoginModal,
      isOpen,
      error,
    } = this.props;

    let errorMessage = <p>{error}</p>;

    return <Dialog title="Sign in"
      open={isOpen}
      onRequestClose={onHideLoginModal} ref="dialog">
      {errorMessage}
      <TextField hintText="Username" className="username" />
      <TextField hintText="Password" type="password" className="password" />
      <RaisedButton
        label="Sign In"
        primary={true}
        onClick={this.onSignIn.bind(this)}
      />
      <RaisedButton label="Cancel" secondary={true} onClick={onHideLoginModal}/>
      </Dialog>;
  }

  onSignIn() {
    const { signIn } = this.props;

    let node = ReactDOM.findDOMNode(this.refs.dialog);
    let username = node.querySelector(".username input").value;
    let password = node.querySelector(".password input").value;

    signIn(username, password);
  }
}

LoginModal.propTypes = {
  isOpen: React.PropTypes.bool.isRequired,
  onHideLoginModal: React.PropTypes.func.isRequired
};

export default LoginModal;
