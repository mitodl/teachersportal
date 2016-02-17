/* global SETTINGS:false */
import {
  RECEIVE_COURSE_SUCCESS,
  RECEIVE_COURSE_FAILURE,
  REQUEST_COURSE,
  RECEIVE_COURSE_LIST_SUCCESS,
  RECEIVE_COURSE_LIST_FAILURE,
  REQUEST_COURSE_LIST,
  CLEAR_COURSE,
  SHOW_LOGIN,
  HIDE_LOGIN,
  SHOW_SNACKBAR,
  HIDE_SNACKBAR,
  FETCH_FAILURE,
  FETCH_PROCESSING,
  FETCH_SUCCESS,
  LOGIN_FAILURE,
  LOGIN_SUCCESS,
  LOGOUT,
  CLEAR_AUTHENTICATION_ERROR,
  CLEAR_REGISTRATION_ERROR,
  REGISTER_SUCCESS,
  REGISTER_FAILURE,
  ACTIVATE_SUCCESS,
  ACTIVATE_FAILURE,
  ACTIVATE,
  CLEAR_ACTIVATION,
  CLEAR_CART,
  CLEAR_INVALID_CART_ITEMS,
  UPDATE_CART_ITEMS,
  UPDATE_SELECTED_CHAPTERS,
  UPDATE_SEAT_COUNT,
  UPDATE_CART_VISIBILITY,
  RESET_BUYTAB,
} from '../actions/index_page';
import { filterCart } from '../util/util';
import { handleActions } from 'redux-actions';

// Helper function to avoid a commonly repeated pattern where we merge
// state with something computed solely from the actions. Accepts a
// function that will get the action, and should return the value to
// be merged with the existing state.
function payloadMerge(fn) {
  return (state, action) => {
    return Object.assign({}, state, fn(action));
  };
}

const INITIAL_SNACKBAR_STATE = {
  message: "",
  open: false
};

export const snackBar = handleActions({
  SHOW_SNACKBAR: payloadMerge((action) => ({
    message: action.payload.message,
    open: true
  })),
  HIDE_SNACKBAR: payloadMerge((action) => ({
    open: false
  })),
  CHECKOUT_SUCCESS: payloadMerge(action => ({
    message: "Course successfully purchased!",
    open: true
  })),
  CHECKOUT_FAILURE: payloadMerge(action => ({
    message: "There was an error purchasing the course.",
    open: true
  }))
}, INITIAL_SNACKBAR_STATE);

const INITIAL_COURSE_STATE = {
  courseList: []
};

export const course = handleActions({
  REQUEST_COURSE: payloadMerge((action) => ({courseStatus: FETCH_PROCESSING})),
  RECEIVE_COURSE_SUCCESS: payloadMerge((action) => ({
    courseStatus: FETCH_SUCCESS,
    course: action.payload.course
  })),

  RECEIVE_COURSE_FAILURE: payloadMerge((action) => ({
    courseStatus: FETCH_FAILURE
  })),

  REQUEST_COURSE_LIST: payloadMerge((action) => ({
    courseListStatus: FETCH_PROCESSING
  })),

  RECEIVE_COURSE_LIST_SUCCESS: payloadMerge((action) => ({
    courseListStatus: FETCH_SUCCESS,
    courseList: action.payload.courseList
  })),

  RECEIVE_COURSE_LIST_FAILURE: payloadMerge((action) => ({
    courseListStatus: FETCH_FAILURE
  })),

  CLEAR_COURSE: (state, action) => INITIAL_COURSE_STATE
}, INITIAL_COURSE_STATE);

const INITIAL_LOGIN = {visible: false};
export const loginModal = handleActions({
  SHOW_LOGIN: (state, action) => ({ visible: true, message: action.payload.message }),
  HIDE_LOGIN: () => ({ visible: false })
}, INITIAL_LOGIN);

export const authentication = handleActions({
  LOGIN_FAILURE: (state, action) => ({
    error: action.payload.error,
    isAuthenticated: false,
    name: ""
  }),
  LOGIN_SUCCESS: (state, action) => ({
    error: "",
    isAuthenticated: true,
    name: action.payload.name
  }),
  LOGOUT: (state, action) => ({
    error: "",
    isAuthenticated: false,
    name: ""
  }),
  CLEAR_AUTHENTICATION_ERROR: payloadMerge((action) => ({error: ""}))
}, {
  isAuthenticated: SETTINGS.isAuthenticated,
  name: SETTINGS.name,
  error: ""
});

export const registration = handleActions({
  REGISTER_SUCCESS: (state, action) => ({
    error: "",
    status: FETCH_SUCCESS
  }),
  REGISTER_FAILURE: (state, action) => ({
    error: action.payload.error,
    status: FETCH_FAILURE
  }),
  CLEAR_REGISTRATION_ERROR: payloadMerge((action) => ({error: ""}))
}, { error: "", status: null });

const INITIAL_ACTIVATION_STATUS = { status: null };
export const activation = handleActions({
  ACTIVATE_SUCCESS: () => ({ status: FETCH_SUCCESS }),
  ACTIVATE_FAILURE: () => ({ status: FETCH_FAILURE }),
  CLEAR_ACTIVATION: () => INITIAL_ACTIVATION_STATUS
}, INITIAL_ACTIVATION_STATUS);

export const cart = handleActions({
  RECEIVE_COURSE_LIST_SUCCESS: payloadMerge((action) => ({
    courseList: action.payload.courseList
  })),

  UPDATE_CART_ITEMS: (state, action) => {
    const { uuids, seats, courseUuid } = action.payload;
    let newCart = state.cart.filter(item => item.courseUuid !== courseUuid);
    if (uuids.length > 0) {
      newCart = newCart.concat({uuids, seats, courseUuid});
    }

    return Object.assign({}, state, {
      cart: newCart
    });
  },

  CLEAR_CART: payloadMerge((action) => ({cart: []})),

  CLEAR_INVALID_CART_ITEMS: (state, action) =>
    Object.assign({}, state, {
      cart: filterCart(state.cart, state.courseList)
    })
}, {
  courseList: [],
  cart: []
});

const INITIAL_BUYTAB_STATE = {
  seats: 20,
  allRowsSelected: false,
  selectedChapters: [],
  cartVisibility: false
};

export const buyTab = handleActions({
  UPDATE_SELECTED_CHAPTERS: payloadMerge((action) => ({
    selectedChapters: action.payload.uuids,
    allRowsSelected: action.payload.allRowsSelected
  })),
  UPDATE_SEAT_COUNT: payloadMerge((action) => ({
    seats: action.payload.seats
  })),
  UPDATE_CART_VISIBILITY: payloadMerge((action) => ({
    cartVisibility: action.payload.visibility
  })),
  RESET_BUYTAB: () => INITIAL_BUYTAB_STATE
}, INITIAL_BUYTAB_STATE);
