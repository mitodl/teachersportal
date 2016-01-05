import * as api from '../util/api';

// action type constants
export const REQUEST_PRODUCT = 'REQUEST_PRODUCT';
export const RECEIVE_PRODUCT_SUCCESS = 'RECEIVE_PRODUCT_SUCCESS';
export const RECEIVE_PRODUCT_FAILURE = 'RECEIVE_PRODUCT_FAILURE';
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

export const ADD_OR_UPDATE_CART_ITEM = 'ADD_OR_UPDATE_CART_ITEM';
export const REMOVE_CART_ITEM = 'REMOVE_CART_ITEM';
export const CLEAR_CART = 'CLEAR_CART';
export const CHECKOUT_SUCCESS = 'CHECKOUT_SUCCESS';
export const CHECKOUT_FAILURE = 'CHECKOUT_FAILURE';

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

export function fetchProduct(upc) {
  return dispatch => {
    dispatch(requestProduct());
    return api.getProduct(upc).
      then(json => dispatch(receiveProductSuccess(json))).
      catch(() => dispatch(receiveProductFailure()));
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

export function addOrUpdateCartItem(upc, seats) {
  return {
    type: ADD_OR_UPDATE_CART_ITEM,
    upc,
    seats
  };
}

export function removeCartItem(upc) {
  return {
    type: REMOVE_CART_ITEM,
    upc
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
