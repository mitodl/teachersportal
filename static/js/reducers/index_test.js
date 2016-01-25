import {
  showLogin,
  hideLogin,
  showSnackBar,
  hideSnackBar,
  logout,
  loginFailure,
  loginSuccess,
  login,
  register,
  activate,
  checkout,
  checkoutSuccess,
  checkoutFailure,
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

import configureTestStore from '../store/configureStore_test';
import assert from 'assert';
import sinon from 'sinon';

describe('reducers', () => {

  let sandbox, store, productStub, productListStub, loginStub, logoutStub,
    registerStub, activateStub, checkoutStub, dispatchThen;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    productStub = sandbox.stub(api, 'getProduct');
    productListStub = sandbox.stub(api, 'getProductList');
    logoutStub = sandbox.stub(api, 'logout');
    loginStub = sandbox.stub(api, 'login');
    registerStub = sandbox.stub(api, 'register');
    activateStub = sandbox.stub(api, 'activate');
    checkoutStub = sandbox.stub(api, 'checkout');
    store = configureTestStore();
  });

  afterEach(() => {
    sandbox.restore();

    store = null;
    dispatchThen = null;
  });

  describe('product reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.product);
    });

    it('should have an empty default state', done => {
      dispatchThen({type: 'unknown'}).then(state => {
        assert.deepEqual(state, {
          productList: []
        });
        done();
      });
    });

    it('should fetch a product successfully', done => {
      productStub.returns(Promise.resolve("data"));

      dispatchThen(fetchProduct("upc"), 2).then(productState => {
        assert.equal(productState.product, "data");
        assert.equal(productState.productStatus, FETCH_SUCCESS);

        done();
      });
    });

    it('should fail to fetch a product', done => {
      productStub.returns(Promise.reject());

      dispatchThen(fetchProduct("upc"), 2).then(productState => {
        assert.equal(productState.productStatus, FETCH_FAILURE);

        done();
      });
    });

    it('should fetch a list of products successfully', done => {
      productListStub.returns(Promise.resolve(["data"]));

      dispatchThen(fetchProductList(), 2).then(productState => {
        assert.deepEqual(productState.productList, ["data"]);
        assert.equal(productState.productListStatus, FETCH_SUCCESS);

        done();
      });
    });

    it('should fail to fetch a list of products', done => {
      productListStub.returns(Promise.reject());

      dispatchThen(fetchProductList(), 2).then(productState => {
        assert.equal(productState.productListStatus, FETCH_FAILURE);

        done();
      });
    });
  });

  describe('loginModal reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.loginModal);
    });

    it('should have visible = false as a default state', done => {
      // dispatch empty action to look at default state
      dispatchThen({type: "unknown"}).then(state => {
        assert.deepEqual(state, {
          visible: false
        });
        done();
      });
    });

    it('should set login state to show when triggered', done => {
      dispatchThen(showLogin()).then(state => {
        assert.deepEqual(state, {
          visible: true
        });
        done();
      });
    });

    it('should set login state to hide when triggered', done => {
      dispatchThen(hideLogin(), 3).then(state => {
        assert.deepEqual(state, {
          visible: false
        });
        done();
      });
    });
  });

  describe('snackBar reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.snackBar);
    });

    it('should have open: false as a default state', done => {
      // dispatch empty action to look at default state
      dispatchThen({type: "unknown"}).then(state => {
        assert.deepEqual(state, {
          message: "",
          open: false
        });
        done();
      });
    });

    it('should set snackBar to open when triggered', done => {
      dispatchThen(showSnackBar({ message: "Snackbar is open for business!" })).then(state => {
        assert.deepEqual(state, {
          message: "Snackbar is open for business!",
          open: true
        });
        done();
      });
    });

    it('should set snackbar open to false when triggered', done => {
      let message = "Snackbar is open for business!";
      dispatchThen(showSnackBar({ message: message })).then(state => {
        assert.deepEqual(state, {
          message: message,
          open: true
        });

        dispatchThen(hideSnackBar()).then(state => {
          assert.deepEqual(state, {
            message: message,
            open: false
          });
          done();
        });
      });
    });

    it('messages the snackbar on checkout success', done => {
      dispatchThen(checkoutSuccess()).then(state => {
        assert.equal(state.message, "Course successfully purchased!");
        done();
      });
    });

    it('messages the snackbar on checkout failure', done => {
      dispatchThen(checkoutFailure()).then(state => {
        assert.equal(state.message, "There was an error purchasing the course.");
        done();
      });
    });
  });

  describe('authentication reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.authentication);
    });

    it('should have an empty error message and unauthenticated as a default state', done => {
      // dispatch empty action to look at default state
      dispatchThen({type: "unknown"}).then(state => {
        assert.deepEqual(state, {
          error: "",
          isAuthenticated: false,
        });
        done();
      });
    });

    it('should clear authentication and show an error message if failed to log in', done => {
      dispatchThen(loginFailure("Error logging in inside test")).then(state => {
        assert.deepEqual(state, {
          isAuthenticated: false,
          error: "Error logging in inside test"
        });
        done();
      });
    });

    it('should set isAuthenticated to true if logged in successfully', done => {
      dispatchThen(loginSuccess()).then(state => {
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

      dispatchThen(login("user", "pass"), 4).then(loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: true,
          error: ""
        });

        dispatchThen(logout(), 2).then(logoutState => {
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

      dispatchThen(login("user", "pass")).then(loginState => {
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

      dispatchThen(login("user", "pass"), 4).then(loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: true,
          error: ""
        });

        dispatchThen(logout(), 0).then(logoutState => {
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
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.registration);
    });

    it('successfully registers', done => {
      registerStub.returns(Promise.resolve());

      dispatchThen(register("name", "email", "org", "pass", "redirect"), 4).then(registrationState => {
        assert.deepEqual(registrationState, {
          error: "",
          status: FETCH_SUCCESS
        });

        done();
      });
    });

    it('fails to register', done => {
      registerStub.returns(Promise.reject());

      dispatchThen(register("name", "email", "org", "pass", "redirect")).then(registrationState => {
        assert.deepEqual(registrationState, {
          error: "Unable to register",
          status: FETCH_FAILURE
        });

        done();
      });
    });
  });

  describe('activation reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.activation);
    });

    it('successfully activates', done => {
      activateStub.returns(Promise.resolve());

      dispatchThen(activate("token")).then(activationState => {
        assert.deepEqual(activationState, {
          status: FETCH_SUCCESS
        });

        done();
      });
    });

    it('fails to activate', done => {
      activateStub.returns(Promise.reject());

      dispatchThen(activate("token")).then(activationState => {
        assert.deepEqual(activationState, {
          status: FETCH_FAILURE
        });

        done();
      });
    });
  });

  describe('cart reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.cart);
    });

    it('updates the cart', done => {
      // Add item to empty cart
      dispatchThen(updateCartItems(['upc'], 3, 'courseUpc')).then(cartState => {
        assert.deepEqual(cartState, {
          cart: [{
            upc: 'upc',
            seats: 3,
            courseUpc: 'courseUpc'
          }],
          productList: []
        });

        // Update cart with item in it, which removes the other items in cart
        dispatchThen(updateCartItems(['newUpc'], 5, 'courseUpc')).then(cartState => {
          assert.deepEqual(cartState, {
            cart: [{
              upc: 'newUpc',
              seats: 5,
              courseUpc: 'courseUpc'
            }],
            productList: []
          });

          // Update cart with a different courseUpc, ignoring existing items with a different courseUpc
          dispatchThen(updateCartItems(['upc'], 4, 'othercourseUpc')).then(cartState => {
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

      dispatchThen(updateCartItems(['upc'], 5, 'courseUpc')).then(cartState => {
        let expectedCart = [{
          upc: 'upc',
          seats: 5,
          courseUpc: 'courseUpc'
        }];
        assert.deepEqual(cartState, {
          cart: expectedCart,
          productList: []
        });

        dispatchThen(checkout(expectedCart, "token", 500), 2).then(cartState => {
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

      dispatchThen(updateCartItems(['upc'], 5, 'courseUpc')).then(cartState => {
        let expectedCart = [{
          upc: 'upc',
          seats: 5,
          courseUpc: 'courseUpc'
        }];
        assert.deepEqual(cartState, {
          cart: expectedCart,
          productList: []
        });

        dispatchThen(checkout(expectedCart, "token", 500)).then(cartState => {
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
      dispatchThen(updateCartItems([upc], 5, courseUpc)).then(cartState => {
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
        dispatchThen(receiveProductListSuccess([PRODUCT_RESPONSE])).then(() => {

          // don't filter anything since all cart items match some product
          dispatchThen(clearInvalidCartItems()).then(cartState => {
            assert.deepEqual(cartState, {
              cart: expectedCart,
              productList: [PRODUCT_RESPONSE]
            });

            // clear product list
            dispatchThen(receiveProductListSuccess([])).then(() => {

              // filter everything since no cart items match any product
              dispatchThen(clearInvalidCartItems()).then(cartState => {
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

    it('fetches a list of products and stores it in the cart', done => {
      productListStub.returns(Promise.resolve(["data"]));

      dispatchThen(fetchProductList(), 2).then(cartState => {
        assert.deepEqual(cartState.productList, ["data"]);

        done();
      });
    });
  });

  describe('buyTab reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.buyTab);
    });

    it('sets cart visibility', done => {
      assert.equal(store.getState().buyTab.cartVisibility, false);
      dispatchThen(updateCartVisibility(true)).then(cartState => {
        assert.equal(cartState.cartVisibility, true);
        done();
      });
    });

    it('updates selected chapters', done => {
      assert.deepEqual(store.getState().buyTab.selectedChapters, []);
      assert.equal(store.getState().buyTab.allRowsSelected, false);

      dispatchThen(updateSelectedChapters(['a', 'b', 'c'], true)).then(cartState => {
        assert.deepEqual(cartState.selectedChapters, ['a', 'b', 'c']);
        assert.equal(cartState.allRowsSelected, true);

        done();
      });
    });

    it('updates seat count', done => {
      assert.equal(store.getState().buyTab.seats, 20);

      dispatchThen(updateSeatCount(200)).then(cartState => {
        assert.equal(cartState.seats, 200);
        done();
      });
    });
  });
});
