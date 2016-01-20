// Create a store for running tests against
import { createStore, applyMiddleware } from 'redux';
import thunkMiddleware from 'redux-thunk';
import rootReducer from '../reducers';

import _ from 'lodash';

/**
 * Helper function to aid in async dispatch testing.
 * @param {Store} store The redux store
 * @param {Function} stateFunc When called, returns the part of the state we care about
 * @returns {Function} Returns a function which will dispatch an action and take a callback
 * to be executed after the store updates its state. Looks like:
 *   (action, expectedCalls) => Promise
 * where
 *   action is an action to be dispatched (or falsey if no action)
 *   expectedCalls is the number of actions to listen for (default: 1)
 *   The returned Promise is executed after the number of actions in expectedCalls
 *   is met
 */
function createDispatchThen(store, stateFunc) {
  let unsubscribe;

  return (action, expectedCallsArg) => {
    return new Promise(resolve => {
      let expectedCalls = 1;
      if (expectedCallsArg !== undefined) {
        expectedCalls = expectedCallsArg;
      }

      let count = 0;

      // If we called this twice unsubscribe the old instance from the store
      if (unsubscribe !== undefined) {
        unsubscribe();
      }
      if (expectedCalls === 0) {
        // No actions expected, run callback now
        resolve(stateFunc(store.getState()));
        count++;
      }
      unsubscribe = store.subscribe(() => {
        if (count + 1 < expectedCalls) {
          count++;
        } else if (count + 1 === expectedCalls) {
          resolve(stateFunc(store.getState()));
          count++;
        } else {
          throw `Expected ${expectedCalls} calls but got at least one extra call`;
        }
      });
      if (action) {
        store.dispatch(action);
      }
    });
  };
}

/**
 * Listen for actions. After some actions have been processed execute
 * a callback so the user can verify state.
 *
 * @param {Store} store The redux store
 * @param {Function} stateFunc When called, returns the part of the state we care about
 * @param {Function} actionListFunc When called, returns the list of actions
 * @returns {Function} Returns a function:
 *   (expectedActionTypes, callback) => Promise
 * where
 *   expectedActionTypes is a list of actions that must be the only actions dispatched
 *     by the code in the callback,
 *   callback which runs the code that will dispatch actions indirectly
 * and returns a Promise that resolves after the expected actions have occurred.
 *
 * Example:
 *   const listenForActions = store.createListenForActions(state => state);
 *   listenForActions(['UPDATE_SELECTED_CHAPTERS', 'UPDATE_SEAT_COUNT'], () => {
 *     runFuncWhichDispatchesTwoActions();
 *   }).then(state => {
 *     assert.deepEqual(state, {
 *       ...
 *     });
 *   });
 */
function createListenForActions(store, stateFunc, actionListFunc) {
  let unsubscribe;

  return (actionTypes, callback) => {
    return new Promise(resolve => {
      // Note: we are not using Sets because we care about preserving duplicate values
      const startingActionListTypes = actionListFunc().map(action => action.type);
      const expectedActionTypes = Array.from(actionTypes).concat(startingActionListTypes).sort();

      // If we called this twice unsubscribe the old instance from the store
      let actionCount = 0;
      if (unsubscribe !== undefined) {
        unsubscribe();
      }

      unsubscribe = store.subscribe(() => {
        actionCount++;

        // Get current action list
        let actionListTypes = actionListFunc().map(action => action.type).sort();
        if (_.isEqual(actionListTypes, expectedActionTypes)) {
          resolve(stateFunc(store.getState()));
        } else if (actionListTypes.length > expectedActionTypes.length) {
          console.error("Expected actions vs actual", expectedActionTypes, actionListTypes);
          throw "Expected " + expectedActionTypes.length + " actions but got at least one more";
        }
      });

      callback();
    });
  };
}

// Keep a list of actions executed for testing purposes
const subscriber = subscribe => store => next => action => {
  if (subscribe !== undefined) {
    subscribe(action);
  }
  return next(action);
};

export default function configureTestStore(initialState) {
  let actionList = [];

  const createStoreWithMiddleware = applyMiddleware(
    thunkMiddleware,
    subscriber(action => {
      actionList = actionList.concat(action);
    })
  )(createStore);

  const store = createStoreWithMiddleware(rootReducer, initialState);
  store.createDispatchThen = stateFunc => createDispatchThen(store, stateFunc);
  store.createListenForActions = stateFunc => createListenForActions(store, stateFunc, () => actionList);
  return store;
}
