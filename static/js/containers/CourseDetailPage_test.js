/* global localStorage:true, document:false, window: false */
import '../global_init';
import { Provider } from 'react-redux';
import assert from 'assert';
import sinon from 'sinon';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';
import configureTestStore from 'redux-asserts';

import App from './App';
import CourseDetailPage from './CourseDetailPage';
import BuyTabContainer from './BuyTabContainer';
import { COURSE_LIST, COURSE_RESPONSE1, COURSE_RESPONSE2 } from '../constants';
import rootReducer from '../reducers';
import * as api from '../util/api';
import { calculateTotal } from '../util/util';
import {
  receiveCourseListSuccess,
  receiveCourseSuccess,
  receiveCourseListFailure,
  receiveCourseFailure,
  loginSuccess,
  updateSeatCount,
  updateSelectedChapters,
  checkout,
  updateCartItems,
  registerSuccess,
  registerFailure,

  SHOW_LOGIN,
  HIDE_LOGIN,
  LOGIN_SUCCESS,
  REQUEST_COURSE,
  REQUEST_COURSE_LIST,
  RECEIVE_COURSE_SUCCESS,
  RECEIVE_COURSE_FAILURE,
  RECEIVE_COURSE_LIST_SUCCESS,
  RECEIVE_COURSE_LIST_FAILURE,
  CLEAR_INVALID_CART_ITEMS,
  UPDATE_SELECTED_CHAPTERS,
  UPDATE_CART_ITEMS,
  UPDATE_CART_VISIBILITY,
  CHECKOUT_SUCCESS,
  CLEAR_CART,
  RESET_BUYTAB,
  CHECKOUT_FAILURE
} from '../actions/index_page';

describe('CourseDetailPage', () => {
  let store, sandbox, container, checkoutStub, listenForActions, dispatchThen;

  beforeEach(() => {
    sandbox = sinon.sandbox.create();
    checkoutStub = sandbox.stub(api, 'checkout');

    store = configureTestStore(rootReducer);
    listenForActions = store.createListenForActions();
    dispatchThen = store.createDispatchThen();

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

  // Helper function to render CourseDetailPage, mock course APIs and
  // assert actions
  const renderCourseDetail = (
    mockedCourse = COURSE_RESPONSE1,
    mockedCourseList = COURSE_LIST,
    extraTypesToAssert = []
  ) => new Promise(resolve => {
    let uuid = mockedCourse ? mockedCourse.uuid : "invalid";

    let expectedTypes = [REQUEST_COURSE, REQUEST_COURSE_LIST];
    let courseStub = sandbox.stub(api, 'getCourse');
    if (mockedCourse) {
      courseStub.returns(Promise.resolve(mockedCourse));
      expectedTypes.push(RECEIVE_COURSE_SUCCESS);
    } else {
      courseStub.returns(Promise.reject());
      expectedTypes.push(RECEIVE_COURSE_FAILURE);
    }

    let courseListStub = sandbox.stub(api, 'getCourseList');
    if (mockedCourseList) {
      courseListStub.returns(Promise.resolve(mockedCourseList));
      expectedTypes.push(RECEIVE_COURSE_LIST_SUCCESS, CLEAR_INVALID_CART_ITEMS);
    } else {
      courseListStub.returns(Promise.reject());
      expectedTypes.push(RECEIVE_COURSE_LIST_FAILURE, CLEAR_INVALID_CART_ITEMS);
    }

    expectedTypes.push(...extraTypesToAssert);

    let appComponent;
    const afterMount = component => {
      appComponent = component;
    };

    listenForActions(expectedTypes, () => {
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
    }).then(() => {
      resolve(appComponent);
    });
  });

  it('cannot see tabs if not logged in', done => {
    renderCourseDetail().then(component => {
      let node = ReactDOM.findDOMNode(component);
      assert.ok(!node.innerHTML.includes("ABOUT"), 'about missing');
      assert.ok(!node.innerHTML.includes("CONTENT"), 'content missing');
      assert.ok(!node.innerHTML.includes("BUY"), 'buy missing');
      assert.ok(node.innerHTML.includes("Please login for more info"), 'missing login prompt');

      done();
    });
  });

  it('can check off items in the buy tab', done => {
    // Set up state as if we logged in already
    store.dispatch(loginSuccess({name: "Darth Vader"}));

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
    store.dispatch(updateSeatCount(course2SeatCount));
    store.dispatch(updateSelectedChapters(COURSE_RESPONSE2.modules.map(child => child.uuid), false));

    // Populate cart
    store.dispatch(updateCartItems(
      COURSE_RESPONSE1.modules.map(child => child.uuid), course1SeatCount, COURSE_RESPONSE1.uuid));


    let node;
    renderCourseDetail(COURSE_RESPONSE2).then(component => {
      node = ReactDOM.findDOMNode(component);
      // Listen for UPDATE_CART_ITEMS and UPDATE_CART_VISIBILITY
      return listenForActions([UPDATE_CART_ITEMS, UPDATE_CART_VISIBILITY], () => {
        // Click the Update cart button
        let button = TestUtils.findRenderedDOMComponentWithClass(component, "add-to-cart");
        TestUtils.Simulate.click(button.firstChild);
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
        assert.ok(shoppingCartText.includes(course.modules[0].title));
        assert.ok(shoppingCartText.includes(seatCount + "Total Seats"));
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
      return listenForActions([
        UPDATE_CART_VISIBILITY,
        CHECKOUT_SUCCESS,
        CLEAR_CART,
        RESET_BUYTAB
      ], () => {
        // Click Checkout.
        // Make sure the total shown in stripe is the same as what we calculate here
        let cart = store.getState().cart.cart;
        expectedTotal = calculateTotal(cart, store.getState().course.courseList);
        expectedNumCartItems = cart.length;

        let button = TestUtils.findRenderedDOMComponentWithClass(component, "checkout-button");
        TestUtils.Simulate.click(button.firstChild);
      });
    }).then(() => {
      // Assert that things returned to initial state
      let state = store.getState();
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
    store.dispatch(updateSeatCount(newSeatCount));
    store.dispatch(updateSelectedChapters(uuids, false));
    store.dispatch(updateCartItems(uuids, newSeatCount, zeroPriceCourse.uuid));

    // Note that we are not mocking StripeHandler here like in the other test
    // Mock checkout api to succeed
    checkoutStub.returns(Promise.resolve());

    renderCourseDetail(zeroPriceCourse, [zeroPriceCourse]).then(component => {
      // Click Checkout.
      return listenForActions([
        UPDATE_CART_VISIBILITY,
        CHECKOUT_SUCCESS,
        CLEAR_CART,
        RESET_BUYTAB,
      ], () => {
        let button = TestUtils.findRenderedDOMComponentWithClass(component, "checkout-button");
        TestUtils.Simulate.click(button.firstChild);
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
    store.dispatch(updateSeatCount(newSeatCount));
    store.dispatch(updateSelectedChapters(uuids, false));
    store.dispatch(updateCartItems(uuids, newSeatCount, zeroPriceCourse.uuid));

    // Mock checkout api to reject
    checkoutStub.returns(Promise.reject());

    const oldCart = store.getState().cart.cart;

    renderCourseDetail(zeroPriceCourse, [zeroPriceCourse]).then(component => {
      // Click Checkout.
      return listenForActions([
        UPDATE_CART_VISIBILITY,
        CHECKOUT_FAILURE,
      ], () => {
        let button = TestUtils.findRenderedDOMComponentWithClass(component, "checkout-button");
        TestUtils.Simulate.click(button.firstChild);
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

  it('clears the buytab when leaving the course detail page', done => {
    let container = document.createElement("div");
    ReactDOM.render(
      <div>
        <Provider store={store}>
          <BuyTabContainer
            selectable={true}
            fixedHeader={true}
            fixedFooter={true}
            stripedRows={false}
            showRowHover={true}
            deselectOnClickaway={true}
            height={'auto'}
            course={COURSE_RESPONSE1}
            courseList={COURSE_LIST}
          />
        </Provider>
      </div>,
      container
    );

    listenForActions([RESET_BUYTAB], () => {
      let unmounted = ReactDOM.unmountComponentAtNode(container);
      assert.ok(unmounted);
    }).then(() => {
      done();
    });
  });
});
