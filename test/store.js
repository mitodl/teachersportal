// Create a store for running tests against
import { createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import rootReducer from '../static/js/reducers';

const createStoreWithMiddleware = applyMiddleware(
  thunkMiddleware
)(createStore);

export default function configureStore(initialState) {
  return createStoreWithMiddleware(rootReducer, initialState);
}
