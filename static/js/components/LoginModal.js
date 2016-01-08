import React from 'react';
import ReactDOM from 'react-dom';
import Dialog from 'material-ui/lib/dialog';
import TextField from 'material-ui/lib/text-field';
import RaisedButton from 'material-ui/lib/raised-button';
import Card from 'material-ui/lib/card/card';
import CardTitle from 'material-ui/lib/card/card-title';

class LoginModal extends React.Component {
  render() {
    const {
      onHideLoginModal,
      isOpen,
      loginError,
      registerError,
    } = this.props;

    // Note that we don't store the password in the redux state to avoid
    // accidentally logging it via redux logger
    return <Dialog
      open={isOpen}
      onRequestClose={onHideLoginModal}>
      <div className="login-container">
        <div ref="signin">
          <CardTitle
            title={"Sign In"}
          />
          <p>{loginError}</p>
          <div><TextField
            autoFocus
            hintText="Email"
            className="email"
            onEnterKeyDown={() => this.refs.signinPassword.focus()}
          /></div>
          <div><TextField
            hintText="Password"
            type="password"
            className="password"
            ref="signinPassword"
            onEnterKeyDown={this.onSignIn.bind(this)}
          /></div>
          <div>
            <RaisedButton
              label="Sign In"
              primary={true}
              onClick={this.onSignIn.bind(this)}
            />
            <RaisedButton
              label="Cancel"
              secondary={true}
              onClick={onHideLoginModal}/>
          </div>
        </div>
        <div ref="register">
          <CardTitle
            title={"Register"}
          />
          <p>{registerError}</p>
          <div><TextField
            hintText="Full Name"
            className="full-name"
            onEnterKeyDown={() => this.refs.registerEmail.focus()}
          /></div>
          <div><TextField
            hintText="Email"
            className="email"
            ref="registerEmail"
            onEnterKeyDown={() => this.refs.organization.focus()}
          /></div>
          <div><TextField
            hintText="Organization"
            className="organization"
            ref="organization"
            onEnterKeyDown={() => this.refs.registerPassword.focus()}
          /></div>
          <div><TextField
            hintText="Password"
            type="password"
            className="password"
            ref="registerPassword"
            onEnterKeyDown={() => this.refs.registerConfirmPassword.focus()}
          /></div>
          <div><TextField
            hintText="Confirm password"
            type="password"
            className="confirm-password"
            ref="registerConfirmPassword"
            onEnterKeyDown={this.onRegister.bind(this)}
          /></div>
          <div>
            <RaisedButton
              label="Register"
              primary={true}
              onClick={this.onRegister.bind(this)}
            />
            <RaisedButton
              label="Cancel"
              secondary={true}
              onClick={onHideLoginModal} />
          </div>
        </div>
      </div>
      </Dialog>;
  }

  onSignIn() {
    const { signIn, reportLoginError } = this.props;

    let node = ReactDOM.findDOMNode(this.refs.signin);
    // username is email for login purposes
    let email = node.querySelector(".email input").value;
    let password = node.querySelector(".password input").value;

    if (email === "") {
      reportLoginError("Email must not be blank");
    } else if (password === "") {
      reportLoginError("Password must not be blank");
    } else {
      signIn(email, password);
    }
  }

  onRegister() {
    const { register, reportRegisterError } = this.props;

    let node = ReactDOM.findDOMNode(this.refs.register);

    let fullName = node.querySelector(".full-name input").value;
    let email = node.querySelector(".email input").value;
    let organization = node.querySelector(".organization input").value;
    let password = node.querySelector(".password input").value;
    let confirmPassword = node.querySelector(".confirm-password input").value;
    let redirect = window.location.toString();

    if (email === "") {
      reportRegisterError("Email must not be blank");
    } else if (organization === "") {
      reportRegisterError("Organization must not be blank");
    } else if (fullName === "") {
      reportRegisterError("Full Name must not be blank");
    } else if (password === "") {
      reportRegisterError("Password must not be blank");
    } else if (confirmPassword === "") {
      reportRegisterError("Confirmation password must not be blank");
    } else if (password !== confirmPassword) {
      reportRegisterError("Password and confirmation password do not match");
    } else {
      register(fullName, email, organization, password, redirect);
    }
  }
}

LoginModal.propTypes = {
  isOpen: React.PropTypes.bool.isRequired,
  onHideLoginModal: React.PropTypes.func.isRequired,
  loginError: React.PropTypes.string,
  registerError: React.PropTypes.string,
  signIn: React.PropTypes.func.isRequired,
  reportLoginError: React.PropTypes.func.isRequired,
  register: React.PropTypes.func.isRequired,
  reportRegisterError: React.PropTypes.func.isRequired
};

export default LoginModal;
