/* global localStorage:true, document:false, window: false */
import '../global_init';
import { Provider } from 'react-redux';
import configureTestStore from '../store/configureStore_test';
import assert from 'assert';
import sinon from 'sinon';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';

import App from './App';
import CourseDetailPage from './CourseDetailPage';
import { COURSE_LIST, COURSE_RESPONSE1, COURSE_RESPONSE2 } from '../constants';
import * as api from '../util/api';
import { calculateTotal } from '../util/util';
import {
  receiveCourseListSuccess,
  receiveCourseSuccess,
  loginSuccess,
  updateSeatCount,
  updateSelectedChapters,
  checkout,
  updateCartItems,

  SHOW_LOGIN,
  HIDE_LOGIN,
  LOGIN_SUCCESS,
  CLEAR_AUTHENTICATION_ERROR,
  CLEAR_REGISTRATION_ERROR,
  REQUEST_COURSE,
  REQUEST_COURSE_LIST,
  RECEIVE_COURSE_SUCCESS,
  RECEIVE_COURSE_LIST_SUCCESS,
  CLEAR_INVALID_CART_ITEMS,
  UPDATE_SELECTED_CHAPTERS,
  UPDATE_CART_ITEMS,
  UPDATE_CART_VISIBILITY,
  CHECKOUT_SUCCESS,
  CLEAR_CART,
  RESET_BUYTAB,
  CHECKOUT_FAILURE,
} from '../actions/index_page';

describe('CourseDetailPage', () => {
  let store, sandbox, container, checkoutStub, listenForActions, dispatchThen;

  beforeEach(() => {
    // Fake getSelection so material-ui doesn't complain about not being
    // in a browser
    window.getSelection = () => ({
      removeAllRanges: () => {}
    });

    sandbox = sinon.sandbox.create();
    checkoutStub = sandbox.stub(api, 'checkout');

    store = configureTestStore();
    listenForActions = store.createListenForActions(state => state);
    dispatchThen = store.createDispatchThen(state => state);

    const body = document.getElementsByTagName("body")[0];
    container = document.createElement("div");
    body.appendChild(container);
  });

  afterEach(() => {
    store = null;
    listenForActions = null;
    dispatchThen = null;

    container.parentNode.removeChild(container);
    container = null;

    sandbox.restore();

    // Not set by default but might be set in the test
    global.StripeHandler = null;
  });

  // Helper function to render CourseDetailPage
  const renderCourseDetail = () => new Promise(resolve => {
    const uuid = COURSE_RESPONSE1.uuid;

    const afterMount = component => {
      resolve(component);
    };

    TestUtils.renderIntoDocument(
      <div>
        <Provider store={store}>
          <App ref={afterMount}>
            <CourseDetailPage
              params={{ uuid }}
            />
          </App>
        </Provider>
      </div>
    );
  });

  it('cannot see tabs if not logged in', done => {
    store.dispatch(receiveCourseListSuccess(COURSE_LIST));
    store.dispatch(receiveCourseSuccess(COURSE_RESPONSE1));

    renderCourseDetail().then(component => {
      let node = ReactDOM.findDOMNode(component);
      assert.ok(!node.innerHTML.includes("ABOUT"));
      assert.ok(!node.innerHTML.includes("CONTENT"));
      assert.ok(!node.innerHTML.includes("BUY"));
      assert.ok(node.innerHTML.includes("Please login for more info"));

      done();
    });
  });

  it('can check off items in the buy tab', done => {
    // Set up state as if we logged in already
    store.dispatch(loginSuccess({name: "Darth Vader"}));
    store.dispatch(receiveCourseListSuccess(COURSE_LIST));
    store.dispatch(receiveCourseSuccess(COURSE_RESPONSE1));

    renderCourseDetail().then(component => {
      const node = ReactDOM.findDOMNode(component);
      // Listen for two updates to the buyTab state
      return listenForActions([UPDATE_SELECTED_CHAPTERS, UPDATE_SELECTED_CHAPTERS], () => {
        const rows = node.querySelectorAll(".course-purchase-selector tbody tr");
        let rowCount = 0;
        for (let row of rows) {
          let cells = row.querySelectorAll("td");

          // Make sure we're in the right table by asserting its text
          let titleNode = cells[1];
          assert.equal(titleNode.textContent, COURSE_RESPONSE1.modules[rowCount].title);
          let priceNode = cells[2];
          assert.equal(priceNode.textContent, "$" +
            COURSE_RESPONSE1.modules[rowCount].price_without_tax + " / seat");

          // Technically the td still, but close enough
          let checkboxNode = ReactDOM.findDOMNode(cells[0]);
          // The idea to click firstChild comes from https://github.com/callemall/material-ui/issues/410
          TestUtils.Simulate.click(checkboxNode.firstChild);
          rowCount++;
        }
      });
    }).then(state => {
      // Assert that the buyTab state now has the chapters we selected, but the cart does not yet
      assert.deepEqual(state.buyTab.selectedChapters, COURSE_RESPONSE1.modules.map(child => child.uuid));
      assert.deepEqual(state.cart.cart, []);
      done();
    });
  });

  it('can add items to the cart', done => {
    // Alter state as if we logged in, selected all chapters and updated seat count
    const course1SeatCount = 77;
    const course2SeatCount = 88;
    const coursePairs = [{
      seatCount: course1SeatCount,
      course: COURSE_RESPONSE1
    }, {
      seatCount: course2SeatCount,
      course: COURSE_RESPONSE2
    }];
    // The current course is COURSE_RESPONSE2. COURSE_RESPONSE1 is already in cart
    store.dispatch(loginSuccess({name: "Darth Vader"}));
    store.dispatch(receiveCourseListSuccess(COURSE_LIST));
    store.dispatch(receiveCourseSuccess(COURSE_RESPONSE2));
    store.dispatch(updateSeatCount(course2SeatCount));
    store.dispatch(updateSelectedChapters(COURSE_RESPONSE2.modules.map(child => child.uuid), false));

    // Populate cart
    store.dispatch(updateCartItems(
      COURSE_RESPONSE1.modules.map(child => child.uuid), course1SeatCount, COURSE_RESPONSE1.uuid));


    let node;
    renderCourseDetail().then(component => {
      node = ReactDOM.findDOMNode(component);
      // Listen for UPDATE_CART_ITEMS and UPDATE_CART_VISIBILITY
      return listenForActions([UPDATE_CART_ITEMS, UPDATE_CART_VISIBILITY], () => {
        // Click the Update cart button
        let button = TestUtils.findRenderedDOMComponentWithClass(component, "add-to-cart");
        TestUtils.Simulate.click(button);
      });
    }).then(state => {
      let expectedCart = [];
      for (let pair of coursePairs) {
        let { seatCount, course } = pair;
        expectedCart.push({
          courseUuid: course.uuid,
          seats: seatCount,
          uuids: course.modules.map(module => module.uuid)
        });
      }
      assert.deepEqual(state.cart.cart, expectedCart);
      let expectedTotal = calculateTotal(state.cart.cart, state.course.courseList);

      assert.equal(
        node.querySelector(".cart-total").textContent,
        `$${expectedTotal}total cost`
      );

      done();
    });
  });

  it('shows items in the cart panel', done => {
    const course1SeatCount = 77;
    const course2SeatCount = 88;
    const coursePairs = [{
      seatCount: course1SeatCount,
      course: COURSE_RESPONSE1
    }, {
      seatCount: course2SeatCount,
      course: COURSE_RESPONSE2
    }];

    // Alter state as if we logged in, selected all chapters and updated seat count,
    // and updated the cart
    store.dispatch(loginSuccess({name: "Darth Vader"}));
    store.dispatch(receiveCourseListSuccess(COURSE_LIST));
    store.dispatch(receiveCourseSuccess(COURSE_RESPONSE1));
    // Cart will contain two courses
    for (let pair of coursePairs) {
      let { course, seatCount } = pair;
      store.dispatch(updateCartItems(
        course.modules.map(module => module.uuid), seatCount, course.uuid));
    }

    // We calculate the expected total after the component renders
    let component;
    renderCourseDetail().then(_component => {
      component = _component;
      let node = ReactDOM.findDOMNode(component);
      // Check that items show up properly

      let shoppingCartText = node.querySelector(".shopping-cart").textContent;
      for (let pair of coursePairs) {
        let { course, seatCount } = pair;
        assert.ok(shoppingCartText.includes(course.title));
        assert.ok(!shoppingCartText.includes(course.modules[0].title));
        assert.ok(shoppingCartText.includes("Seats: " + seatCount));
        assert.ok(!shoppingCartText.includes('No chapters selected'));
      }

      return listenForActions([UPDATE_CART_ITEMS, UPDATE_CART_ITEMS], () => {
        // Clear courses
        for (let pair of coursePairs) {
          let { course, seatCount } = pair;
          store.dispatch(updateCartItems([], seatCount, course.uuid));
        }
      });
    }).then(() => {
      component.forceUpdate(() => {
        let node = ReactDOM.findDOMNode(component);
        let shoppingCartText = node.querySelector(".shopping-cart").textContent;
        assert.ok(shoppingCartText.includes('No chapters selected'));

        done();
      });
    });
  });

  it('can checkout the cart', done => {
    const fakeToken = "FAKE_TOKEN";

    const course1SeatCount = 77;
    const course2SeatCount = 88;
    const coursePairs = [{
      seatCount: course1SeatCount,
      course: COURSE_RESPONSE1
    }, {
      seatCount: course2SeatCount,
      course: COURSE_RESPONSE2
    }];

    // Alter state as if we logged in, selected all chapters and updated seat count,
    // and updated the cart
    store.dispatch(loginSuccess({name: "Darth Vader"}));
    store.dispatch(receiveCourseListSuccess(COURSE_LIST));
    store.dispatch(receiveCourseSuccess(COURSE_RESPONSE1));
    // Cart will contain two courses
    for (let pair of coursePairs) {
      let { course, seatCount } = pair;
      store.dispatch(updateCartItems(
        course.modules.map(module => module.uuid), seatCount, course.uuid));
    }

    // We calculate the expected total after the component renders
    let expectedTotal, expectedNumCartItems;

    // Mock Stripe to immediately call the checkout api
    global.StripeHandler = {
      open: data => {
        assert.deepEqual(data, {
          name: "MIT Teacher's Portal",
          description: expectedNumCartItems + " course(s)",
          amount: Math.floor(expectedTotal * 100)
        });

        store.dispatch(checkout(store.getState().cart.cart, fakeToken));
      }
    };

    // Mock checkout api to succeed
    checkoutStub.returns(Promise.resolve());

    renderCourseDetail().then(component => {
      // Click Checkout.
      return listenForActions([UPDATE_CART_VISIBILITY, CHECKOUT_SUCCESS, CLEAR_CART, RESET_BUYTAB], () => {
        // Make sure the total shown in stripe is the same as what we calculate here
        let cart = store.getState().cart.cart;
        expectedTotal = calculateTotal(cart, store.getState().course.courseList);
        expectedNumCartItems = cart.length;

        let button = TestUtils.findRenderedDOMComponentWithClass(component, "checkout-button");
        TestUtils.Simulate.click(button);
      });
    }).then(state => {
      // Assert that things returned to initial state
      assert.deepEqual(state.cart.cart, []);
      assert.equal(state.buyTab.seats, 20);
      assert.deepEqual(state.buyTab.selectedChapters, []);

      assert.ok(checkoutStub.calledOnce);

      done();
    });
  });

  it('can checkout the cart with an empty price', done => {
    const zeroPriceCourse = Object.assign(COURSE_RESPONSE1,
      {
        modules: COURSE_RESPONSE1.modules.map(child =>
          Object.assign(child, {"price_without_tax": 0})
        )
      }
    );

    const uuids = zeroPriceCourse.modules.map(child => child.uuid);
    const newSeatCount = 40;

    // Alter state as if we logged in, selected all chapters and updated seat count,
    // and updated the cart
    store.dispatch(loginSuccess({name: "Darth Vader"}));
    store.dispatch(receiveCourseListSuccess([zeroPriceCourse]));
    store.dispatch(receiveCourseSuccess(zeroPriceCourse));
    store.dispatch(updateSeatCount(newSeatCount));
    store.dispatch(updateSelectedChapters(uuids, false));
    store.dispatch(updateCartItems(uuids, newSeatCount, zeroPriceCourse.uuid));

    // Note that we are not mocking StripeHandler here like in the other test
    // Mock checkout api to succeed
    checkoutStub.returns(Promise.resolve());

    renderCourseDetail().then(component => {
      // Click Checkout.
      return listenForActions([UPDATE_CART_VISIBILITY, CHECKOUT_SUCCESS, CLEAR_CART, RESET_BUYTAB], () => {
        let button = TestUtils.findRenderedDOMComponentWithClass(component, "checkout-button");
        TestUtils.Simulate.click(button);
      });
    }).then(state => {
      // Assert that things returned to initial state
      assert.deepEqual(state.cart.cart, []);
      assert.equal(state.buyTab.seats, 20);
      assert.deepEqual(state.buyTab.selectedChapters, []);

      assert.ok(checkoutStub.calledOnce);

      done();
    });
  });

  it('fails to checkout', done => {
    const zeroPriceCourse = Object.assign(COURSE_RESPONSE1,
      {
        modules: COURSE_RESPONSE1.modules.map(child =>
          Object.assign(child, {"price_without_tax": 0})
        )
      }
    );

    const uuids = zeroPriceCourse.modules.map(child => child.uuid);
    const newSeatCount = 30;

    // Alter state as if we logged in, selected all chapters and updated seat count,
    // and updated the cart
    store.dispatch(loginSuccess({name: "Darth Vader"}));
    store.dispatch(receiveCourseListSuccess([zeroPriceCourse]));
    store.dispatch(receiveCourseSuccess(zeroPriceCourse));
    store.dispatch(updateSeatCount(newSeatCount));
    store.dispatch(updateSelectedChapters(uuids, false));
    store.dispatch(updateCartItems(uuids, newSeatCount, zeroPriceCourse.uuid));

    // Mock checkout api to reject
    checkoutStub.returns(Promise.reject());

    const oldCart = store.getState().cart.cart;

    renderCourseDetail().then(component => {
      // Click Checkout.
      return listenForActions([UPDATE_CART_VISIBILITY, CHECKOUT_FAILURE], () => {
        let button = TestUtils.findRenderedDOMComponentWithClass(component, "checkout-button");
        TestUtils.Simulate.click(button);
      });
    }).then(state => {
      // Assert that things haven't changed in the UI
      assert.deepEqual(state.cart.cart, oldCart);
      assert.equal(state.buyTab.seats, newSeatCount);
      assert.deepEqual(state.buyTab.selectedChapters, uuids);

      assert.ok(checkoutStub.calledOnce);

      done();
    });
  });
});
