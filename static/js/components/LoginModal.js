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
      message
    } = this.props;

    let messageBox;
    if (message !== undefined) {
      messageBox = <div className="alert-message">{message}</div>;
    }

    // Note that we don't store the password in the redux state to avoid
    // accidentally logging it via redux logger
    return <Dialog
      open={isOpen}
      onRequestClose={onHideLoginModal}>
      <div className="login-container">
        {messageBox}
        <div ref="signin" className="login">
          <CardTitle
            title={"Sign In"}
          />
          <p>{loginError}</p>
          <div><TextField
            autoFocus
            hintText="Email"
            className="email"
            onKeyDown={e => {
              if (e.key === "Enter") {
                this.refs.signinPassword.focus();
              }
            }}
          /></div>
          <div><TextField
            hintText="Password"
            type="password"
            className="password"
            ref="signinPassword"
            onKeyDown={e => {
              if (e.key === "Enter") {
                this.onSignIn.call(this);
              }
            }}
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
        <div ref="register" className="register">
          <CardTitle
            title={"Register"}
          />
          <p>{registerError}</p>
          <div><TextField
            hintText="Full Name"
            className="full-name"
            onKeyDown={e => {
              if (e.key === "Enter") {
                this.refs.registerEmail.focus();
              }
            }}
          /></div>
          <div><TextField
            hintText="Email"
            className="email"
            ref="registerEmail"
            onKeyDown={e => {
              if (e.key === "Enter") {
                this.refs.organization.focus();
              }
            }}
          /></div>
          <div><TextField
            hintText="Organization"
            className="organization"
            ref="organization"
            onKeyDown={e => {
              if (e.key === "Enter") {
                this.refs.registerPassword.focus();
              }
            }}
          /></div>
          <div><TextField
            hintText="Password"
            type="password"
            className="password"
            ref="registerPassword"
            onKeyDown={e => {
              if (e.key === "Enter") {
                this.refs.registerConfirmPassword.focus();
              }
            }}
          /></div>
          <div><TextField
            hintText="Confirm password"
            type="password"
            className="confirm-password"
            ref="registerConfirmPassword"
            onKeyDown={e => {
              if (e.key === "Enter") {
                this.onRegister.call(this);
              }
            }}
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
    let redirect = window.location.pathname + window.location.search + window.location.hash;

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
