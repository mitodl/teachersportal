import {
  showLogin,
  hideLogin,
  logout,
  loginFailure,
  loginSuccess,
  login,
  register,
  activate,
  checkout,
  updateCartItems,
  fetchProduct,
  fetchProductList,
  updateCartVisibility,
  updateSeatCount,
  updateSelectedChapters,
  clearInvalidCartItems,
  receiveProductListSuccess,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import * as api from '../util/api';
import { PRODUCT_RESPONSE, CART_WITH_ITEM } from '../constants';
import { createDispatchThen } from './util';

import configureStore from '../store/configureStore_test';
import assert from 'assert';
import sinon from 'sinon';
import jsdom from 'mocha-jsdom';

let productStub;
let productListStub;
let loginStub;
let logoutStub;
let registerStub;
let activateStub;
let checkoutStub;
let store;


describe('reducers', () => {
  beforeEach(() => {
    productStub = sinon.stub(api, 'getProduct');
    productListStub = sinon.stub(api, 'getProductList');
    logoutStub = sinon.stub(api, 'logout');
    loginStub = sinon.stub(api, 'login');
    registerStub = sinon.stub(api, 'register');
    activateStub = sinon.stub(api, 'activate');
    checkoutStub = sinon.stub(api, 'checkout');

    store = configureStore();
  });

  afterEach(() => {
    productStub.restore();
    productListStub.restore();
    logoutStub.restore();
    loginStub.restore();
    registerStub.restore();
    activateStub.restore();
    checkoutStub.restore();

    store = null;
  });

  describe('product reducers', () => {
    /**
     * Helper function for dispatch and assert pattern
     */
    let dispatchThen = createDispatchThen(() => store, state => state.product);

    it('should have an empty default state', done => {
      dispatchThen({type: 'unknown'}, state => {
        assert.deepEqual(state, {
          productList: []
        });
        done();
      });
    });

    it('should fetch a product successfully', done => {
      productStub.returns(Promise.resolve("data"));

      dispatchThen(fetchProduct("upc"), 2, productState => {
        assert.equal(productState.product, "data");
        assert.equal(productState.productStatus, FETCH_SUCCESS);

        done();
      });
    });

    it('should fail to fetch a product', done => {
      productStub.returns(Promise.reject());

      dispatchThen(fetchProduct("upc"), 2, productState => {
        assert.equal(productState.productStatus, FETCH_FAILURE);

        done();
      });
    });

    it('should fetch a list of products successfully', done => {
      productListStub.returns(Promise.resolve(["data"]));

      dispatchThen(fetchProductList(), 2, productState => {
        assert.deepEqual(productState.productList, ["data"]);
        assert.equal(productState.productListStatus, FETCH_SUCCESS);

        done();
      });
    });

    it('should fail to fetch a list of products', done => {
      productListStub.returns(Promise.reject());

      dispatchThen(fetchProductList(), 2, productState => {
        assert.equal(productState.productListStatus, FETCH_FAILURE);

        done();
      });
    });
  });

  describe('loginModal reducers', () => {
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

  describe('cart reducers', () => {
    /**
     * Helper function for dispatch and assert pattern
     */
    let dispatchThen = createDispatchThen(() => store, state => state.cart);

    it('updates the cart', done => {
      // Add item to empty cart
      dispatchThen(updateCartItems(['upc'], 3, 'courseUpc'), cartState => {
        assert.deepEqual(cartState, {
          cart: [{
            upc: 'upc',
            seats: 3,
            courseUpc: 'courseUpc'
          }],
          productList: []
        });

        // Update cart with item in it, which removes the other items in cart
        dispatchThen(updateCartItems(['newUpc'], 5, 'courseUpc'), cartState => {
          assert.deepEqual(cartState, {
            cart: [{
              upc: 'newUpc',
              seats: 5,
              courseUpc: 'courseUpc'
            }],
            productList: []
          });

          // Update cart with a different courseUpc, ignoring existing items with a different courseUpc
          dispatchThen(updateCartItems(['upc'], 4, 'othercourseUpc'), cartState => {
            assert.deepEqual(cartState, {
              cart: [{
                upc: 'newUpc',
                seats: 5,
                courseUpc: 'courseUpc'
              }, {
                upc: 'upc',
                seats: 4,
                courseUpc: 'othercourseUpc'
              }],
              productList: []
            });
            done();
          });
        });
      });
    });

    it('checks out the cart', done => {
      checkoutStub.returns(Promise.resolve());

      dispatchThen(updateCartItems(['upc'], 5, 'courseUpc'), cartState => {
        let expectedCart = [{
          upc: 'upc',
          seats: 5,
          courseUpc: 'courseUpc'
        }];
        assert.deepEqual(cartState, {
          cart: expectedCart,
          productList: []
        });

        dispatchThen(checkout(expectedCart, "token"), 2, cartState => {
          assert.deepEqual(cartState, {
            cart: [],
            productList: []
          });

          done();
        });
      });
    });

    it('fails to checkout the cart', done => {
      checkoutStub.returns(Promise.reject());

      dispatchThen(updateCartItems(['upc'], 5, 'courseUpc'), cartState => {
        let expectedCart = [{
          upc: 'upc',
          seats: 5,
          courseUpc: 'courseUpc'
        }];
        assert.deepEqual(cartState, {
          cart: expectedCart,
          productList: []
        });

        dispatchThen(checkout(expectedCart, "token"), cartState => {
          assert.deepEqual(cartState, {
            cart: expectedCart,
            productList: []
          });

          done();
        });
      });
    });

    it('clears the items from the cart which are missing', done => {
      let upc = PRODUCT_RESPONSE.children[0].upc;
      let courseUpc = PRODUCT_RESPONSE.upc;
      dispatchThen(updateCartItems([upc], 5, courseUpc), cartState => {
        let expectedCart = [{
          upc: upc,
          seats: 5,
          courseUpc: courseUpc
        }];
        assert.deepEqual(cartState, {
          cart: expectedCart,
          productList: []
        });

        // update product list
        dispatchThen(receiveProductListSuccess([PRODUCT_RESPONSE]), () => {

          // don't filter anything since all cart items match some product
          dispatchThen(clearInvalidCartItems(), cartState => {
            assert.deepEqual(cartState, {
              cart: expectedCart,
              productList: [PRODUCT_RESPONSE]
            });

            // clear product list
            dispatchThen(receiveProductListSuccess([]), () => {

              // filter everything since no cart items match any product
              dispatchThen(clearInvalidCartItems(), cartState => {
                assert.deepEqual(cartState, {
                  cart: [],
                  productList: []
                });

                done();
              });
            });
          });
        });
      });
    });
  });

  describe('buyTab reducers', () => {
    let dispatchThen = createDispatchThen(() => store, state => state.buyTab);

    it('sets cart visibility', done => {
      assert.equal(store.getState().buyTab.cartVisibility, false);
      dispatchThen(updateCartVisibility(true), cartState => {
        assert.equal(cartState.cartVisibility, true);
        done();
      });
    });

    it('updates selected chapters', done => {
      assert.deepEqual(store.getState().buyTab.selectedChapters, []);
      assert.equal(store.getState().buyTab.allRowsSelected, false);

      dispatchThen(updateSelectedChapters(['a', 'b', 'c'], true), cartState => {
        assert.deepEqual(cartState.selectedChapters, ['a', 'b', 'c']);
        assert.equal(cartState.allRowsSelected, true);

        done();
      });
    });

    it('updates seat count', done => {
      assert.equal(store.getState().buyTab.seats, 20);

      dispatchThen(updateSeatCount(200), cartState => {
        assert.equal(cartState.seats, 200);
        done();
      });
    });
  });
});
