import * as api from '../util/api';
import { createAction } from 'redux-actions';

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

const requestProduct = createAction(REQUEST_PRODUCT);

const receiveProductSuccess = createAction(
  RECEIVE_PRODUCT_SUCCESS, (product) => {return {product};});

const receiveProductFailure = createAction(RECEIVE_PRODUCT_FAILURE);
const requestProductList = createAction(REQUEST_PRODUCT_LIST);

export const receiveProductListSuccess = createAction(
  RECEIVE_PRODUCT_LIST_SUCCESS, (productList) => {return {productList};});

const receiveProductListFailure = createAction(RECEIVE_PRODUCT_LIST_FAILURE);

export const showLogin = createAction(SHOW_LOGIN);

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

export const updateCartVisibility = createAction(
  UPDATE_CART_VISIBILITY, (visibility) => { return {visibility}; });

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

export const clearInvalidCartItems = createAction(CLEAR_INVALID_CART_ITEMS);
export const loginFailure = createAction(LOGIN_FAILURE, (error) => {return {error}; });
export const loginSuccess = createAction(LOGIN_SUCCESS);

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

export const registerSuccess = createAction(REGISTER_SUCCESS);
export const registerFailure = createAction(
  REGISTER_FAILURE, (error) => { return {error}; });

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

export const activateSuccess = createAction(ACTIVATE_SUCCESS);
export const activateFailure = createAction(ACTIVATE_FAILURE);

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

export const updateCartItems = createAction(
  UPDATE_CART_ITEMS, (upcs, seats, courseUpc) => { return {upcs, seats, courseUpc}; });

export const clearCart = createAction(CLEAR_CART);
export const checkoutSuccess = createAction(CHECKOUT_SUCCESS);
export const checkoutFailure = createAction(CHECKOUT_FAILURE);

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

export const updateSelectedChapters = createAction(
  UPDATE_SELECTED_CHAPTERS, (upcs, allRowsSelected)  => { return {upcs, allRowsSelected}; });

export const updateSeatCount = createAction(
  UPDATE_SEAT_COUNT, (seats) => { return { seats }; });
