import * as api from '../util/api';

// action type constants
export const REQUEST_PRODUCT = 'REQUEST_PRODUCT';
export const RECEIVE_PRODUCT_SUCCESS = 'RECEIVE_PRODUCT_SUCCESS';
export const RECEIVE_PRODUCT_FAILURE = 'RECEIVE_PRODUCT_FAILURE';
export const REQUEST_PRODUCT_LIST = 'REQUEST_PRODUCT_LIST';
export const RECEIVE_PRODUCT_LIST_SUCCESS = 'RECEIVE_PRODUCT_LIST_SUCCESS';
export const RECEIVE_PRODUCT_LIST_FAILURE = 'RECEIVE_PRODUCT_LIST_FAILURE';
export const CLEAR_PRODUCT = 'CLEAR_PRODUCT';

export const SHOW_LOGIN = 'SHOW_LOGIN';
export const HIDE_LOGIN = 'HIDE_LOGIN';

export const LOGIN_FAILURE = 'LOGIN_FAILURE';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGOUT = 'LOGOUT';
export const CLEAR_AUTHENTICATION_ERROR = 'CLEAR_AUTHENTICATION_ERROR';

export const REGISTER_SUCCESS = 'REGISTER_SUCCESS';
export const REGISTER_FAILURE = 'REGISTER_FAILURE';
export const CLEAR_REGISTRATION_ERROR = 'CLEAR_REGISTRATION_ERROR';

export const ACTIVATE_SUCCESS = 'ACTIVATE_SUCCESS';
export const ACTIVATE_FAILURE = 'ACTIVATE_FAILURE';
export const ACTIVATE = 'ACTIVATE';

export const UPDATE_CART_ITEMS = 'UPDATE_CART_ITEMS';
export const CLEAR_CART = 'CLEAR_CART';
export const CHECKOUT_SUCCESS = 'CHECKOUT_SUCCESS';
export const CHECKOUT_FAILURE = 'CHECKOUT_FAILURE';
export const CLEAR_INVALID_CART_ITEMS = 'CLEAR_INVALID_CART_ITEMS';

export const UPDATE_SELECTED_CHAPTERS = 'UPDATE_SELECTED_CHAPTERS';
export const UPDATE_SEAT_COUNT = 'UPDATE_SEAT_COUNT';
export const UPDATE_CART_VISIBILITY = 'UPDATE_CART_VISIBILITY';

// constants for fetch status (these are not action types)
export const FETCH_FAILURE = 'FETCH_FAILURE';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_PROCESSING = 'FETCH_PROCESSING';

function requestProduct() {
  return {
    type: REQUEST_PRODUCT
  };
}

function receiveProductSuccess(json) {
  return {
    type: RECEIVE_PRODUCT_SUCCESS,
    product: json
  };
}

function receiveProductFailure() {
  return {
    type: RECEIVE_PRODUCT_FAILURE
  };
}

function requestProductList() {
  return {
    type: REQUEST_PRODUCT_LIST
  };
}

export function receiveProductListSuccess(json) {
  return {
    type: RECEIVE_PRODUCT_LIST_SUCCESS,
    productList: json
  };
}

function receiveProductListFailure() {
  return {
    type: RECEIVE_PRODUCT_LIST_FAILURE
  };
}

export function showLogin() {
  return {
    type: SHOW_LOGIN
  };
}

export function hideLogin() {
  return dispatch => {
    dispatch({
      type: HIDE_LOGIN
    });
    dispatch({
      type: CLEAR_AUTHENTICATION_ERROR
    });
    dispatch({
      type: CLEAR_REGISTRATION_ERROR
    });
  };
}

export function updateCartVisibility(visibility) {
  return {
    type: UPDATE_CART_VISIBILITY,
    visibility
  };
}

export function fetchProduct(upc) {
  return dispatch => {
    dispatch(requestProduct());
    return api.getProduct(upc).
      then(json => dispatch(receiveProductSuccess(json))).
      catch(() => dispatch(receiveProductFailure()));
  };
}

export function fetchProductList() {
  return dispatch => {
    dispatch(requestProductList());
    return api.getProductList().
      then(json => dispatch(receiveProductListSuccess(json))).
      catch(() => dispatch(receiveProductListFailure()));
  };
}

export function clearInvalidCartItems() {
  return {
    type: CLEAR_INVALID_CART_ITEMS
  };
}

export function loginFailure(error) {
  return {
    type: LOGIN_FAILURE,
    error: error
  };
}

export function loginSuccess() {
  return {
    type: LOGIN_SUCCESS
  };
}

export function logout() {
  return dispatch => {
    return api.logout().then(() => {
      dispatch({
        type: LOGOUT
      });
      dispatch({
        type: CLEAR_PRODUCT
      });
    });
  };
}

export function login(username, password) {
  return dispatch => {
    return api.login(username, password).
      then(() => {
        dispatch(loginSuccess());
        dispatch(hideLogin());
      }).
      catch((e) => {
        dispatch(loginFailure("Unable to log in"));
        // let anything afterwards catch the error too
        return Promise.reject(e);
      });
  };
}

export function registerSuccess() {
  return {
    type: REGISTER_SUCCESS
  };
}

export function registerFailure(error) {
  return {
    type: REGISTER_FAILURE,
    error: error
  };
}

export function register(fullName, email, organization, password, redirect) {
  return dispatch => {
    return api.register(fullName, email, organization, password, redirect).
      then(() => {
        dispatch(registerSuccess());
        dispatch(hideLogin());
      }).
      catch(e => {
        dispatch(registerFailure("Unable to register"));
        // let anything afterwards catch the error too
        return Promise.reject(e);
      });
  };
}

export function activateSuccess() {
  return {
    type: ACTIVATE_SUCCESS
  };
}

export function activateFailure() {
  return {
    type: ACTIVATE_FAILURE
  };
}

export function activate(token) {
  return dispatch => {
    return api.activate(token).
      then(() => {
        dispatch(activateSuccess());
      }).catch(e => {
        dispatch(activateFailure());
        // let anything afterwards catch the error too
        return Promise.reject(e);
      });
  };
}

export function updateCartItems(upcs, seats, courseUpc) {
  return {
    type: UPDATE_CART_ITEMS,
    upcs,
    seats,
    courseUpc
  };
}

export function clearCart() {
  return {
    type: CLEAR_CART
  };
}

export function checkoutSuccess() {
  return {
    type: CHECKOUT_SUCCESS
  };
}

export function checkoutFailure() {
  return {
    type: CHECKOUT_FAILURE
  };
}

export function checkout(cart, token) {
  return dispatch => {
    return api.checkout(cart, token).
      then(() => {
        dispatch(checkoutSuccess());
        dispatch(clearCart());
      }).
      catch(e => {
        dispatch(checkoutFailure());
        return Promise.reject(e);
      });
  };
}

export function updateSelectedChapters(upcs, allRowsSelected) {
  return {
    type: UPDATE_SELECTED_CHAPTERS,
    upcs,
    allRowsSelected
  };
}

export function updateSeatCount(seats) {
  return {
    type: UPDATE_SEAT_COUNT,
    seats
  };
}
