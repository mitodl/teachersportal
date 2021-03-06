/* global require:false, module:false */
import { compose, createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import createLogger from 'redux-logger';
import rootReducer from '../reducers';
import { persistState as devToolsPersistState, devTools } from 'redux-devtools';
import localStoragePersistState from 'redux-localstorage';

let createStoreWithMiddleware;
if (process.env.NODE_ENV !== "production") {
  createStoreWithMiddleware = compose(
    applyMiddleware(
      thunkMiddleware,
      createLogger()
    ),
    localStoragePersistState("cart"),
    devTools(),
    devToolsPersistState(window.location.href.match(/[?&]debug_session=([^&]+)\b/))
  )(createStore);
} else {
  createStoreWithMiddleware = compose(
    applyMiddleware(
      thunkMiddleware
    ),
    localStoragePersistState("cart")
  )(createStore);
}

export default function configureStore(initialState) {
  const store = createStoreWithMiddleware(rootReducer, initialState);

  if (module.hot) {
    // Enable Webpack hot module replacement for reducers
    module.hot.accept('../reducers', () => {
      const nextRootReducer = require('../reducers');

      store.replaceReducer(nextRootReducer);
    });
  }

  return store;
}
