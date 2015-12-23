import {
  showLogin,
  hideLogin,
  logout,
  loginFailure,
  loginSuccess,
  login,
} from '../static/js/actions/index_page';
import * as api from '../static/js/util/api';
import { createDispatchThen } from './util';

import configureStore from './store';
import assert from 'assert';
import sinon from 'sinon';
import jsdom from 'mocha-jsdom';

let loginStub;
let logoutStub;
let store;


describe('reducers', () => {
  beforeEach(() => {
    logoutStub = sinon.stub(api, 'logout');
    loginStub = sinon.stub(api, 'login');

    store = configureStore();
  });

  afterEach(() => {
    logoutStub.restore();
    loginStub.restore();

    store = null;
  });

  describe('loginModal reducers', () => {
    jsdom();
    /**
     * Helper function for dispatch and assert pattern
     */
    let dispatchThen = createDispatchThen(() => store, state => state.loginModal);

    it('should have visible = false as a default state', done => {
      // dispatch empty action to look at default state
      dispatchThen({type: "unknown"}, state => {
        assert.deepEqual(state, {
          visible: false
        });
        done();
      });
    });

    it('should set login state to show when triggered', done => {
      dispatchThen(showLogin(), state => {
        assert.deepEqual(state, {
          visible: true
        });
        done();
      });
    });

    it('should set login state to hide when triggered', done => {
      dispatchThen(hideLogin(), 2, state => {
        assert.deepEqual(state, {
          visible: false
        });
        done();
      });
    });
  });

  describe('authentication reducers', () => {
    jsdom();
    /**
     * Helper function for dispatch and assert pattern
     */
    let dispatchThen = createDispatchThen(() => store, state => state.authentication);

    it('should have an empty error message and unauthenticated as a default state', done => {
      // dispatch empty action to look at default state
      dispatchThen({type: "unknown"}, state => {
        assert.deepEqual(state, {
          error: "",
          isAuthenticated: false,
        });
        done();
      });
    });

    it('should clear authentication and show an error message if failed to log in', done => {
      dispatchThen(loginFailure(), state => {
        assert.deepEqual(state, {
          isAuthenticated: false,
          error: "Unable to log in"
        });
        done();
      });
    });

    it('should set isAuthenticated to true if logged in successfully', done => {
      dispatchThen(loginSuccess(), state => {
        assert.deepEqual(state, {
          isAuthenticated: true,
          error: ""
        });
        done();
      });
    });

    it('should login and logout successfully', done => {
      logoutStub.returns(new Promise((resolve, reject) => {
        resolve();
      }));
      loginStub.returns(new Promise((resolve, reject) => {
        resolve();
      }));

      dispatchThen(login("user", "pass"), 3, loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: true,
          error: ""
        });

        dispatchThen(logout(), 2, logoutState => {
          assert.deepEqual(logoutState, {
            isAuthenticated: false,
            error: ""
          });

          done();
        });
      });
    });

    it('should error if login fails', done => {
      logoutStub.returns(new Promise((resolve, reject) => {
        resolve();
      }));
      loginStub.returns(new Promise((resolve, reject) => {
        reject();
      }));

      dispatchThen(login("user", "pass"), loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: false,
          error: "Unable to log in"
        });

        done();
      });

    });

    it('should error if logout fails', done => {
      logoutStub.returns(new Promise((resolve, reject) => {
        reject();
      }));
      loginStub.returns(new Promise((resolve, reject) => {
        resolve();
      }));

      dispatchThen(login("user", "pass"), 3, loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: true,
          error: ""
        });

        dispatchThen(logout(), 0, logoutState => {
          // On logout error no state should change
          assert.deepEqual(logoutState, {
            isAuthenticated: true,
            error: ""
          });

          done();
        });
      });
    });
  });
});