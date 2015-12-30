/**
 * Created by george on 12/21/15.
 */

/**
 * Helper function to aid in async dispatch testing.
 * @param {Function} storeFunc When called, returns the store
 * @param {Function} stateFunc When called, returns the part of the state we care about
 * @returns {Function} Returns a function which will dispatch an action and take a callback
 * to be executed after the store updates its state. Can be either:
 *   (action, callback)
 * or
 *   (action, expectedCalls, callback)
 * where expectedCalls is the number of actions to expect to be called (default: 1)
 */
export function createDispatchThen(storeFunc, stateFunc) {
  let unsubscribe;

  return (action, expectedCallsArg, callbackArg) => {
    let expectedCalls = 1;
    let callback;

    // If user passed only two args, treat them as (action, callback)
    if (callbackArg !== undefined) {
      expectedCalls = expectedCallsArg;
      callback = callbackArg;
    } else {
      callback = expectedCallsArg;
    }

    let count = 0;
    let store = storeFunc();

    // If we called this twice unsubscribe the old instance from the store
    if (unsubscribe !== undefined) {
      unsubscribe();
    }
    if (expectedCalls === 0) {
      // No actions expected, run callback now
      callback(stateFunc(store.getState()));
      count++;
    }
    unsubscribe = store.subscribe(() => {
      if (count + 1 < expectedCalls) {
        count++;
      } else if (count + 1 === expectedCalls) {
        callback(stateFunc(store.getState()));
        count++;
      } else {
        throw `Expected ${expectedCalls} calls but got at least one extra call`;
      }
    });

    store.dispatch(action);
  };
}
