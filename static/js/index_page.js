import React from 'react';
import ReactDOM from 'react-dom';
import reducer from './reducers';
import '../sass/layout.scss';
import App from './containers/App';
import { Provider } from 'react-redux';
import { createStore, applyMiddleware } from 'redux';

const store = createStore(reducer);

ReactDOM.render(
  <Provider store={store}>
      <App />
    </Provider>,
  document.getElementById("inner")
);
