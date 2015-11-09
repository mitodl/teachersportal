import React from 'react';
import HelloWorld from '../components/HelloWorld';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import * as HelloWorldActions from '../actions/hello_world';

class HelloWorldContainer extends React.Component {
  render() {
    const { text } = this.props;

    return <HelloWorld
      text={text}
      onTextChange={(e) => this.props.updateText(e.target.value)}
    />;
  }
}

const mapStateToProps = (state) => {
  return {
    text: state.helloWorld.get("text")
  };
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators(HelloWorldActions, dispatch);
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(HelloWorldContainer);
