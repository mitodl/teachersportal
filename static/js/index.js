import HelloWorld from './hello_world';
import React from 'react';
import ReactDOM from 'react-dom';

main();

function main() {
  ReactDOM.render(
    <HelloWorld />,
    document.getElementById("container")
  );
}
