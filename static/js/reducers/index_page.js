/* global SETTINGS:false */
import {
  RECEIVE_PRODUCT_SUCCESS,
  RECEIVE_PRODUCT_FAILURE,
  REQUEST_PRODUCT,
  RECEIVE_PRODUCT_LIST_SUCCESS,
  RECEIVE_PRODUCT_LIST_FAILURE,
  REQUEST_PRODUCT_LIST,
  CLEAR_PRODUCT,
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
}, INITIAL_SNACKBAR_STATE);

const INITIAL_PRODUCT_STATE = {
  productList: []
};

export const product = handleActions({
  REQUEST_PRODUCT: payloadMerge((action) => ({productStatus: FETCH_PROCESSING})),
  RECEIVE_PRODUCT_SUCCESS: payloadMerge((action) => ({
    productStatus: FETCH_SUCCESS,
    product: action.payload.product
  })),

  RECEIVE_PRODUCT_FAILURE: payloadMerge((action) => ({
    productStatus: FETCH_FAILURE
  })),

  REQUEST_PRODUCT_LIST: payloadMerge((action) => ({
    productListStatus: FETCH_PROCESSING
  })),

  RECEIVE_PRODUCT_LIST_SUCCESS: payloadMerge((action) => ({
    productListStatus: FETCH_SUCCESS,
    productList: action.payload.productList
  })),

  RECEIVE_PRODUCT_LIST_FAILURE: payloadMerge((action) => ({
    productListStatus: FETCH_FAILURE
  })),

  CLEAR_PRODUCT: (state, action) => INITIAL_PRODUCT_STATE
}, INITIAL_PRODUCT_STATE);

export const loginModal = handleActions({
  SHOW_LOGIN: () => ({ visible: true }),
  HIDE_LOGIN: () => ({ visible: false })
}, {visible: false});

export const authentication = handleActions({
  LOGIN_FAILURE: (state, action) => ({
    error: action.payload.error,
    isAuthenticated: false
  }),
  LOGIN_SUCCESS: (state, action) => ({
    error: "",
    isAuthenticated: true
  }),
  LOGOUT: (state, action) => ({
    error: "",
    isAuthenticated: false
  }),
  CLEAR_AUTHENTICATION_ERROR: payloadMerge((action) => ({error: ""}))
}, {
  isAuthenticated: SETTINGS.isAuthenticated,
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

export const activation = handleActions({
  ACTIVATE_SUCCESS: () => ({ status: FETCH_SUCCESS }),
  ACTIVATE_FAILURE: () => ({ status: FETCH_FAILURE })
}, { status: null });

export const cart = handleActions({
  RECEIVE_PRODUCT_LIST_SUCCESS: payloadMerge((action) => ({
    productList: action.payload.productList
  })),

  UPDATE_CART_ITEMS: (state, action) => {
    const { upcs, seats, courseUpc } = action.payload;
    // Remove all items for this particular course
    let newCart = state.cart.filter(item => item.courseUpc !== courseUpc);
    let newItems = upcs.map(upc => ({
      upc: upc,
      seats: seats,
      courseUpc: courseUpc
    }));
    newCart = newCart.concat(newItems);

    return Object.assign({}, state, {
      cart: newCart
    });
  },

  CLEAR_CART: payloadMerge((action) => ({cart: []})),

  CLEAR_INVALID_CART_ITEMS: (state, action) =>
    Object.assign({}, state, {
      cart: filterCart(state.cart, state.productList)
    })
}, {
  productList: [],
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
    selectedChapters: action.payload.upcs,
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
