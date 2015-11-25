import React from 'react';
import ReactDOM from 'react-dom';
import '../sass/layout.scss';
import App from './containers/App';
import { Provider } from 'react-redux';
import configureStore from './store/configureStore';
import { Router, Route } from 'react-router';

// Make sure these are accessible everywhere
import 'react-mdl/extra/material.js';
import 'react-mdl/extra/material.css';

const store = configureStore();

ReactDOM.render(
  <Provider store={store}>
    <Router>
      <Route path="/" component={App}/>
    </Router>
  </Provider>,
  document.getElementById("container")
);
