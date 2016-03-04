import {
  showLogin,
  hideLogin,
  hideSnackBar,
  logout,
  loginFailure,
  loginSuccess,
  login,
  register,
  activate,
  clearActivation,
  checkout,
  checkoutSuccess,
  checkoutFailure,
  updateCartItems,
  fetchCourse,
  fetchCourseList,
  updateCartVisibility,
  updateSeatCount,
  updateSelectedChapters,
  clearInvalidCartItems,
  receiveCourseListSuccess,
  receiveCourseListFailure,
  receiveCourseFailure,
  registerSuccess,
  registerFailure,
  removeCartItem,

  REQUEST_COURSE,
  RECEIVE_COURSE_SUCCESS,
  RECEIVE_COURSE_FAILURE,
  REQUEST_COURSE_LIST,
  RECEIVE_COURSE_LIST_SUCCESS,
  RECEIVE_COURSE_LIST_FAILURE,
  SHOW_LOGIN,
  HIDE_LOGIN,
  HIDE_SNACKBAR,
  CHECKOUT_SUCCESS,
  CHECKOUT_FAILURE,
  CLEAR_CART,
  CLEAR_INVALID_CART_ITEMS,
  LOGIN_SUCCESS,
  LOGIN_FAILURE,
  LOGOUT,
  REGISTER_SUCCESS,
  REGISTER_FAILURE,
  ACTIVATE_SUCCESS,
  ACTIVATE_FAILURE,
  CLEAR_ACTIVATION,
  UPDATE_CART_ITEMS,
  UPDATE_CART_VISIBILITY,
  UPDATE_SEAT_COUNT,
  UPDATE_SELECTED_CHAPTERS,
  RESET_BUYTAB,
  REMOVE_CART_ITEM,

  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import * as api from '../util/api';
import { COURSE_RESPONSE1, COURSE_LIST } from '../constants';

import configureTestStore from '../store/configureStore_test';
import assert from 'assert';
import sinon from 'sinon';

describe('reducers', () => {

  let sandbox, store, courseStub, courseListStub, loginStub, logoutStub,
    registerStub, activateStub, checkoutStub, dispatchThen;
  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    courseStub = sandbox.stub(api, 'getCourse');
    courseListStub = sandbox.stub(api, 'getCourseList');
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

  describe('course reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.course);
    });

    it('should have an empty default state', done => {
      dispatchThen({type: 'unknown'}, ['unknown']).then(state => {
        assert.deepEqual(state, {
          courseList: []
        });
        done();
      });
    });

    it('should fetch a course successfully', done => {
      courseStub.returns(Promise.resolve("data"));

      dispatchThen(fetchCourse("uuid"), [REQUEST_COURSE, RECEIVE_COURSE_SUCCESS]).then(courseState => {
        assert.equal(courseState.course, "data");
        assert.equal(courseState.courseStatus, FETCH_SUCCESS);

        done();
      });
    });

    it('should fail to fetch a course', done => {
      courseStub.returns(Promise.reject());

      dispatchThen(fetchCourse("uuid"), [REQUEST_COURSE, RECEIVE_COURSE_FAILURE]).then(courseState => {
        assert.equal(courseState.courseStatus, FETCH_FAILURE);

        done();
      });
    });

    it('should fetch a list of courses successfully', done => {
      courseListStub.returns(Promise.resolve(["data"]));

      dispatchThen(fetchCourseList(), [REQUEST_COURSE_LIST, RECEIVE_COURSE_LIST_SUCCESS]).then(courseState => {
        assert.deepEqual(courseState.courseList, ["data"]);
        assert.equal(courseState.courseListStatus, FETCH_SUCCESS);

        done();
      });
    });

    it('should fail to fetch a list of courses', done => {
      courseListStub.returns(Promise.reject());

      dispatchThen(fetchCourseList(), [REQUEST_COURSE_LIST, RECEIVE_COURSE_LIST_FAILURE]).then(courseState => {
        assert.equal(courseState.courseListStatus, FETCH_FAILURE);

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
      dispatchThen({type: "unknown"}, ['unknown']).then(state => {
        assert.deepEqual(state, {
          visible: false
        });
        done();
      });
    });

    it('should set login state to show when triggered', done => {
      dispatchThen(showLogin("message"), [SHOW_LOGIN]).then(state => {
        assert.deepEqual(state, {
          visible: true,
          message: "message"
        });
        done();
      });
    });

    it('should set login state to hide when triggered', done => {
      dispatchThen(hideLogin(), [HIDE_LOGIN]).then(state => {
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
      dispatchThen({type: "unknown"}, ['unknown']).then(state => {
        assert.deepEqual(state, {
          message: "",
          open: false
        });
        done();
      });
    });

    it('messages the snackbar on checkout success', done => {
      dispatchThen(checkoutSuccess(), [CHECKOUT_SUCCESS]).then(state => {
        assert.equal(state.message, "Course successfully purchased!");
        assert.ok(state.open);
        done();
      });
    });

    it('messages the snackbar on checkout failure', done => {
      dispatchThen(checkoutFailure(), [CHECKOUT_FAILURE]).then(state => {
        assert.equal(state.message, "There was an error purchasing the course.");
        assert.ok(state.open);
        done();
      });
    });

    it('shows a success message after registration', done => {
      dispatchThen(registerSuccess(), [REGISTER_SUCCESS]).then(state => {
        assert.equal(
          state.message,
          "User registered successfully! Check your email for an activation link."
        );
        assert.ok(state.open);
        done();
      });
    });

    it('shows a failure message after registration', done => {
      dispatchThen(registerFailure(), [REGISTER_FAILURE]).then(state => {
        assert.equal(
          state.message,
          "An error occurred registering the user."
        );
        assert.ok(state.open);
        done();
      });
    });

    it('shows an error after failing to load the course', done => {
      dispatchThen(receiveCourseFailure(), [RECEIVE_COURSE_FAILURE]).then(state => {
        assert.equal(
          state.message,
          "An error occurred fetching information about this course."
        );
        assert.ok(state.open);
        done();
      });
    });

    it('shows an error after failing to load the course list', done => {
      dispatchThen(receiveCourseListFailure(), [RECEIVE_COURSE_LIST_FAILURE]).then(state => {
        assert.equal(
          state.message,
          "An error occurred fetching information about other courses."
        );
        assert.ok(state.open);
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
      dispatchThen({type: "unknown"}, ['unknown']).then(state => {
        assert.deepEqual(state, {
          error: "",
          isAuthenticated: false,
          name: ""
        });
        done();
      });
    });

    it('should clear authentication and show an error message if failed to log in', done => {
      dispatchThen(
        loginFailure("Error logging in inside test"),
        [LOGIN_FAILURE]
      ).then(state => {
        assert.deepEqual(state, {
          isAuthenticated: false,
          error: "Error logging in inside test",
          name: ""
        });
        done();
      });
    });

    it('should set isAuthenticated to true if logged in successfully', done => {
      dispatchThen(loginSuccess({name: "Darth Vader"}), [LOGIN_SUCCESS]).then(state => {
        assert.deepEqual(state, {
          isAuthenticated: true,
          error: "",
          name: "Darth Vader"
        });
        done();
      });
    });

    it('should login and logout successfully', done => {
      logoutStub.returns(Promise.resolve());
      loginStub.returns(Promise.resolve({name: "Darth Vader"}));

      // ERROR
      dispatchThen(login("user", "pass"), [LOGIN_SUCCESS]).then(loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: true,
          error: "",
          name: "Darth Vader"
        });

        dispatchThen(logout(), [LOGOUT]).then(logoutState => {
          assert.deepEqual(logoutState, {
            isAuthenticated: false,
            error: "",
            name: ""
          });

          done();
        });
      });
    });

    it('should error if login fails', done => {
      logoutStub.returns(Promise.resolve());
      loginStub.returns(Promise.reject());

      dispatchThen(login("user", "pass"), [LOGIN_FAILURE]).then(loginState => {
        assert.deepEqual(loginState, {
          isAuthenticated: false,
          error: "Unable to log in",
          name: ""
        });

        done();
      });

    });

    it('should error if logout fails', done => {
      logoutStub.returns(Promise.reject());
      loginStub.returns(Promise.resolve({name: "Darth Vader"}));

      let expectedState = {
        isAuthenticated: true,
        error: "",
        name: "Darth Vader"
      };

      dispatchThen(login("user", "pass"), [LOGIN_SUCCESS]).then(loginState => {
        assert.deepEqual(loginState, expectedState);

        return dispatchThen(logout(), []);
      }).then(logoutState => {
        // On logout error no state should change
        assert.deepEqual(logoutState, expectedState);
        done();
      });

    });
  });

  describe('registration reducers', () => {
    beforeEach(() => {
      dispatchThen = store.createDispatchThen(state => state.registration);
    });

    it('successfully registers', done => {
      registerStub.returns(Promise.resolve());

      dispatchThen(
        register("name", "email", "org", "pass", "redirect"),
        [REGISTER_SUCCESS]
      ).then(registrationState => {
        assert.deepEqual(registrationState, {
          error: "",
          status: FETCH_SUCCESS
        });

        done();
      });
    });

    it('fails to register', done => {
      registerStub.returns(Promise.reject());

      dispatchThen(
        register("name", "email", "org", "pass", "redirect"),
        [REGISTER_FAILURE]
      ).then(registrationState => {
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

      dispatchThen(activate("token"), [ACTIVATE_SUCCESS]).then(activationState => {
        assert.deepEqual(activationState, {
          status: FETCH_SUCCESS
        });

        done();
      });
    });

    it('fails to activate', done => {
      activateStub.returns(Promise.reject());

      dispatchThen(activate("token"), [ACTIVATE_FAILURE]).then(activationState => {
        assert.deepEqual(activationState, {
          status: FETCH_FAILURE
        });

        done();
      });
    });

    it('clears activation status', done => {
      store.dispatch({type: ACTIVATE_SUCCESS});

      dispatchThen(clearActivation(), [CLEAR_ACTIVATION]).then(activationState => {
        assert.deepEqual(activationState, {
          status: null
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
      dispatchThen(
        updateCartItems(['uuid'], 3, 'courseUuid'),
        [UPDATE_CART_ITEMS]
      ).then(cartState => {
        assert.deepEqual(cartState, {
          cart: [{
            uuids: ['uuid'],
            seats: 3,
            courseUuid: 'courseUuid'
          }],
          courseList: []
        });

        // Update cart with item in it, which removes the other items in cart
        dispatchThen(
          updateCartItems(['newUuid'], 5, 'courseUuid'),
          [UPDATE_CART_ITEMS]
        ).then(cartState => {
          assert.deepEqual(cartState, {
            cart: [{
              uuids: ['newUuid'],
              seats: 5,
              courseUuid: 'courseUuid'
            }],
            courseList: []
          });

          // Update cart with a different courseUuid, ignoring existing items with a different courseUuid
          dispatchThen(
            updateCartItems(['uuid'], 4, 'othercourseUuid'),
            [UPDATE_CART_ITEMS]
          ).then(cartState => {
            assert.deepEqual(cartState, {
              cart: [{
                uuids: ['newUuid'],
                seats: 5,
                courseUuid: 'courseUuid'
              }, {
                uuids: ['uuid'],
                seats: 4,
                courseUuid: 'othercourseUuid'
              }],
              courseList: []
            });
            done();
          });
        });
      });
    });

    it('checks out the cart', done => {
      checkoutStub.returns(Promise.resolve());

      dispatchThen(
        updateCartItems(['uuid'], 5, 'courseUuid'),
        [UPDATE_CART_ITEMS]
      ).then(cartState => {
        let expectedCart = [{
          uuids: ['uuid'],
          seats: 5,
          courseUuid: 'courseUuid'
        }];
        assert.deepEqual(cartState, {
          cart: expectedCart,
          courseList: []
        });

        return dispatchThen(
          checkout(expectedCart, "token", 500),
          [CHECKOUT_SUCCESS, CLEAR_CART, RESET_BUYTAB]
        );
      }).then(cartState => {
        assert.deepEqual(cartState, {
          cart: [],
          courseList: []
        });

        done();
      });
    });

    it('fails to checkout the cart', done => {
      checkoutStub.returns(Promise.reject());

      dispatchThen(
        updateCartItems(['uuid'], 5, 'courseUuid'),
        [UPDATE_CART_ITEMS]
      ).then(cartState => {
        let expectedCart = [{
          uuids: ['uuid'],
          seats: 5,
          courseUuid: 'courseUuid'
        }];
        assert.deepEqual(cartState, {
          cart: expectedCart,
          courseList: []
        });

        dispatchThen(
          checkout(expectedCart, "token", 500),
          [CHECKOUT_FAILURE]
        ).then(cartState => {
          assert.deepEqual(cartState, {
            cart: expectedCart,
            courseList: []
          });

          done();
        });
      });
    });

    it('clears the items from the cart which are missing', done => {
      let uuid = COURSE_RESPONSE1.modules[0].uuid;
      let courseUuid = COURSE_RESPONSE1.uuid;
      let expectedCart = [{
        uuids: [uuid],
        seats: 5,
        courseUuid: courseUuid
      }];
      dispatchThen(
        updateCartItems([uuid], 5, courseUuid),
        [UPDATE_CART_ITEMS]
      ).then(cartState => {
        assert.deepEqual(cartState, {
          cart: expectedCart,
          courseList: []
        });

        // update course list
        return dispatchThen(
          receiveCourseListSuccess([COURSE_RESPONSE1]),
          [RECEIVE_COURSE_LIST_SUCCESS]
        );
      }).then(() => {
        // don't filter anything since all cart items match some module
        return dispatchThen(
          clearInvalidCartItems(),
          [CLEAR_INVALID_CART_ITEMS]
        );
      }).then(cartState => {
        assert.deepEqual(cartState, {
          cart: expectedCart,
          courseList: [COURSE_RESPONSE1]
        });

        // clear course list
        return dispatchThen(
          receiveCourseListSuccess([]),
          [RECEIVE_COURSE_LIST_SUCCESS]
        );
      }).then(() => {

        // filter everything since no cart items match any module
        return dispatchThen(
          clearInvalidCartItems(),
          [CLEAR_INVALID_CART_ITEMS]
        );
      }).then(cartState => {
        assert.deepEqual(cartState, {
          cart: [],
          courseList: []
        });

        done();
      });
    });

    it('removes an item from the cart', done => {
      let uuid = COURSE_RESPONSE1.modules[0].uuid;
      let courseUuid = COURSE_RESPONSE1.uuid;
      store.dispatch(updateCartItems([uuid], 5, courseUuid));
      let expectedCart = [{
        uuids: [uuid],
        seats: 5,
        courseUuid: courseUuid
      }];

      // If course uuid doesn't match, no item is removed
      dispatchThen(removeCartItem("missing"), [REMOVE_CART_ITEM]).then(cartState => {
        assert.deepEqual(cartState.cart, expectedCart);

        // If course uuid matches, item is removed
        return dispatchThen(removeCartItem(courseUuid), [REMOVE_CART_ITEM]);
      }).then(cartState => {
        assert.deepEqual(cartState.cart, []);

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
      dispatchThen(updateCartVisibility(true), [UPDATE_CART_VISIBILITY]).then(cartState => {
        assert.equal(cartState.cartVisibility, true);
        done();
      });
    });

    it('updates selected chapters', done => {
      assert.deepEqual(store.getState().buyTab.selectedChapters, []);
      assert.equal(store.getState().buyTab.allRowsSelected, false);

      dispatchThen(
        updateSelectedChapters(['a', 'b', 'c'], true),
        [UPDATE_SELECTED_CHAPTERS]
      ).then(cartState => {
        assert.deepEqual(cartState.selectedChapters, ['a', 'b', 'c']);
        assert.equal(cartState.allRowsSelected, true);

        done();
      });
    });

    it('updates seat count', done => {
      assert.equal(store.getState().buyTab.seats, 20);

      dispatchThen(
        updateSeatCount(200),
        [UPDATE_SEAT_COUNT]
      ).then(cartState => {
        assert.equal(cartState.seats, 200);
        done();
      });
    });
  });
});
