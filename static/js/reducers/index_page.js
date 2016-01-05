/* global SETTINGS:false */
import {
  RECEIVE_PRODUCT_SUCCESS,
  RECEIVE_PRODUCT_FAILURE,
  REQUEST_PRODUCT,
  CLEAR_PRODUCT,
  SHOW_LOGIN,
  HIDE_LOGIN,
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
  UPDATE_CART_ITEMS,
  UPDATE_SELECTED_CHAPTERS,
  UPDATE_SEAT_COUNT,
  UPDATE_CART_VISIBILITY,
} from '../actions/index_page';

export function product(state = {}, action) {
  switch (action.type) {

  case REQUEST_PRODUCT:
    return Object.assign({}, state, {
      status: FETCH_PROCESSING
    });
  case RECEIVE_PRODUCT_SUCCESS:
    return Object.assign({}, state, {
      status: FETCH_SUCCESS,
      product: action.product
    });
  case RECEIVE_PRODUCT_FAILURE:
    return Object.assign({}, state, {
      status: FETCH_FAILURE
    });

  case CLEAR_PRODUCT:
    return {};

  default:
    return state;
  }
}

const INITIAL_LOGIN_MODAL_STATE = {
  visible: false
};

export function loginModal(state = INITIAL_LOGIN_MODAL_STATE, action) {
  switch (action.type) {
  case SHOW_LOGIN:
    return Object.assign({}, state, {
      visible: true
    });
  case HIDE_LOGIN:
    return Object.assign({}, state, {
      visible: false
    });
  default:
    return state;
  }
}

const INITIAL_AUTHENTICATION_STATE = {
  isAuthenticated: SETTINGS.isAuthenticated,
  error: ""
};

export function authentication(state = INITIAL_AUTHENTICATION_STATE, action) {
  switch (action.type) {
  case LOGIN_FAILURE:
    return Object.assign({}, state, {
      isAuthenticated: false,
      error: action.error
    });
  case LOGIN_SUCCESS:
    return Object.assign({}, state, {
      error: "",
      isAuthenticated: true
    });
  case LOGOUT:
    return Object.assign({}, state, {
      error: "",
      isAuthenticated: false
    });
  case CLEAR_AUTHENTICATION_ERROR:
    return Object.assign({}, state, {
      error: ""
    });
  default:
    return state;
  }
}

const INITIAL_REGISTRATION_STATE = {
  error: ""
};

export function registration(state = INITIAL_REGISTRATION_STATE, action) {
  switch (action.type) {
  case REGISTER_SUCCESS:
    return Object.assign({}, state, {
      error: "",
      status: FETCH_SUCCESS
    });
  case REGISTER_FAILURE:
    return Object.assign({}, state, {
      error: action.error,
      status: FETCH_FAILURE
    });
  case CLEAR_REGISTRATION_ERROR:
    return Object.assign({}, state, {
      error: ""
    });
  default:
    return state;
  }
}

const INITIAL_ACTIVATION_STATE = {};

export function activation(state = INITIAL_ACTIVATION_STATE, action) {
  switch (action.type) {
  case ACTIVATE_SUCCESS:
    return Object.assign({}, state, {
      status: FETCH_SUCCESS
    });
  case ACTIVATE_FAILURE:
    return Object.assign({}, state, {
      status: FETCH_FAILURE
    });
  default:
    return state;
  }
}

const INITIAL_CART_STATE = {
  cart: []
};
export function cart(state = INITIAL_CART_STATE, action) {
  switch (action.type) {
  case UPDATE_CART_ITEMS:
    const { upcs, seats, courseUpc } = action;
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
  case CLEAR_CART:
    return Object.assign({}, state, {
      cart: []
    });
  default:
    return state;
  }
}

const INITIAL_BUYTAB_STATE = {
  seats: 20,
  allRowsSelected: false,
  selectedChapters: [],
  cartVisibility: false
};

export function buyTab(state = INITIAL_BUYTAB_STATE, action) {
  switch (action.type) {
  case UPDATE_SELECTED_CHAPTERS:
    return Object.assign({}, state, {
      selectedChapters: action.upcs,
      allRowsSelected: action.allRowsSelected
    });
  case UPDATE_SEAT_COUNT:
    return Object.assign({}, state, {
      seats: action.seats
    });
  case UPDATE_CART_VISIBILITY:
    return Object.assign({}, state, {
      cartVisibility: action.visibility
    });
  default:
    return state;
  }
}
