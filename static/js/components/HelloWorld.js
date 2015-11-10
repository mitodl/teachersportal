import React from "react";
import { connect } from 'react-redux';

class HelloWorld extends React.Component {
  render() {
    const { onTextChange, text } = this.props;

    return <h1>Hello, <input
      type="text" value={text}
      onChange={onTextChange}
    />!</h1>;
  }
}

export default HelloWorld;