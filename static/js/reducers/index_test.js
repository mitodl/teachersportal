import {
  showLogin,
  hideLogin,
  logout,
  loginFailure,
  loginSuccess,
  login,
  register,
  activate,
  fetchProduct,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import * as api from '../util/api';
import { createDispatchThen } from './util';

import configureStore from '../store/configureStore_test';
import assert from 'assert';
import sinon from 'sinon';
import jsdom from 'mocha-jsdom';

let productStub;
let loginStub;
let logoutStub;
let registerStub;
let activateStub;
let store;


describe('reducers', () => {
  beforeEach(() => {
    productStub = sinon.stub(api, 'getProduct');
    logoutStub = sinon.stub(api, 'logout');
    loginStub = sinon.stub(api, 'login');
    registerStub = sinon.stub(api, 'register');
    activateStub = sinon.stub(api, 'activate');

    store = configureStore();
  });

  afterEach(() => {
    productStub.restore();
    logoutStub.restore();
    loginStub.restore();
    registerStub.restore();
    activateStub.restore();

    store = null;
  });

  describe('product reducers', () => {
    jsdom();
    /**
     * Helper function for dispatch and assert pattern
     */
    let dispatchThen = createDispatchThen(() => store, state => state.product);

    it('should have an empty default state', done => {
      dispatchThen({type: 'unknown'}, state => {
        assert.deepEqual(state, {});
        done();
      });
    });

    it('should fetch products successfully', done => {
      productStub.returns(Promise.resolve("data"));

      dispatchThen(fetchProduct("upc"), 2, productState => {
        assert.deepEqual(productState, {
          product: "data",
          status: FETCH_SUCCESS
        });

        done();
      });
    });

    it('should fail to fetch products', done => {
      productStub.returns(Promise.reject());

      dispatchThen(fetchProduct("upc"), 2, productState => {
        assert.deepEqual(productState, {
          status: FETCH_FAILURE
        });

        done();
      });
    });
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
      dispatchThen(hideLogin(), 3, state => {
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
      dispatchThen(loginFailure("Error logging in inside test"), state => {
        assert.deepEqual(state, {
          isAuthenticated: false,
          error: "Error logging in inside test"
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
      logoutStub.returns(Promise.resolve());
      loginStub.returns(Promise.resolve());

      dispatchThen(login("user", "pass"), 4, loginState => {
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
      logoutStub.returns(Promise.resolve());
      loginStub.returns(Promise.reject());

      dispatchThen(login("user", "pass"), loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: false,
          error: "Unable to log in"
        });

        done();
      });

    });

    it('should error if logout fails', done => {
      logoutStub.returns(Promise.reject());
      loginStub.returns(Promise.resolve());

      dispatchThen(login("user", "pass"), 4, loginState => {
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

  describe('registration reducers', () => {
    jsdom();
    /**
     * Helper function for dispatch and assert pattern
     */
    let dispatchThen = createDispatchThen(() => store, state => state.registration);

    it('successfully registers', done => {
      registerStub.returns(Promise.resolve());

      dispatchThen(register("name", "email", "org", "pass", "redirect"), 4, registrationState => {
        assert.deepEqual(registrationState, {
          error: "",
          status: FETCH_SUCCESS
        });

        done();
      });
    });

    it('fails to register', done => {
      registerStub.returns(Promise.reject());

      dispatchThen(register("name", "email", "org", "pass", "redirect"), registrationState => {
        assert.deepEqual(registrationState, {
          error: "Unable to register",
          status: FETCH_FAILURE
        });

        done();
      });
    });
  });

  describe('activation reducers', () => {
    jsdom();
    /**
     * Helper function for dispatch and assert pattern
     */
    let dispatchThen = createDispatchThen(() => store, state => state.activation);

    it('successfully activates', done => {
      activateStub.returns(Promise.resolve());

      dispatchThen(activate("token"), activationState => {
        assert.deepEqual(activationState, {
          status: FETCH_SUCCESS
        });

        done();
      });
    });

    it('fails to activate', done => {
      activateStub.returns(Promise.reject());

      dispatchThen(activate("token"), activationState => {
        assert.deepEqual(activationState, {
          status: FETCH_FAILURE
        });

        done();
      });
    });
  });
});
