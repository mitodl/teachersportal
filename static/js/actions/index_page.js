import * as api from '../util/api';
import { createAction } from 'redux-actions';
import { sendGoogleAnalyticsEvent, sendGoogleEcommerceTransaction } from '../util/util';

// action type constants
export const REQUEST_COURSE = 'REQUEST_COURSE';
export const RECEIVE_COURSE_SUCCESS = 'RECEIVE_COURSE_SUCCESS';
export const RECEIVE_COURSE_FAILURE = 'RECEIVE_COURSE_FAILURE';
export const REQUEST_COURSE_LIST = 'REQUEST_COURSE_LIST';
export const RECEIVE_COURSE_LIST_SUCCESS = 'RECEIVE_COURSE_LIST_SUCCESS';
export const RECEIVE_COURSE_LIST_FAILURE = 'RECEIVE_COURSE_LIST_FAILURE';
export const CLEAR_COURSE = 'CLEAR_COURSE';

export const SHOW_LOGIN = 'SHOW_LOGIN';
export const HIDE_LOGIN = 'HIDE_LOGIN';

export const SHOW_SNACKBAR = 'SHOW_SNACKBAR';
export const HIDE_SNACKBAR = 'HIDE_SNACKBAR';

export const LOGIN_FAILURE = 'LOGIN_FAILURE';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGOUT = 'LOGOUT';
export const CLEAR_AUTHENTICATION_ERROR = 'CLEAR_AUTHENTICATION_ERROR';

export const REGISTER_SUCCESS = 'REGISTER_SUCCESS';
export const REGISTER_FAILURE = 'REGISTER_FAILURE';
export const CLEAR_REGISTRATION_ERROR = 'CLEAR_REGISTRATION_ERROR';

export const ACTIVATE_SUCCESS = 'ACTIVATE_SUCCESS';
export const ACTIVATE_FAILURE = 'ACTIVATE_FAILURE';
export const CLEAR_ACTIVATION = 'CLEAR_ACTIVATION';

export const UPDATE_CART_ITEMS = 'UPDATE_CART_ITEMS';
export const CLEAR_CART = 'CLEAR_CART';
export const CHECKOUT_SUCCESS = 'CHECKOUT_SUCCESS';
export const CHECKOUT_FAILURE = 'CHECKOUT_FAILURE';
export const CLEAR_INVALID_CART_ITEMS = 'CLEAR_INVALID_CART_ITEMS';
export const RESET_BUYTAB = 'RESET_BUYTAB';

export const UPDATE_SELECTED_CHAPTERS = 'UPDATE_SELECTED_CHAPTERS';
export const UPDATE_SEAT_COUNT = 'UPDATE_SEAT_COUNT';
export const UPDATE_CART_VISIBILITY = 'UPDATE_CART_VISIBILITY';

// constants for fetch status (these are not action types)
export const FETCH_FAILURE = 'FETCH_FAILURE';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_PROCESSING = 'FETCH_PROCESSING';

const requestCourse = createAction(REQUEST_COURSE);

export const receiveCourseSuccess = createAction(
  RECEIVE_COURSE_SUCCESS, (course) => {return {course};});

const receiveCourseFailure = createAction(RECEIVE_COURSE_FAILURE);
const requestCourseList = createAction(REQUEST_COURSE_LIST);

export const receiveCourseListSuccess = createAction(
  RECEIVE_COURSE_LIST_SUCCESS, (courseList) => {return {courseList};});

const receiveCourseListFailure = createAction(RECEIVE_COURSE_LIST_FAILURE);

export const showLogin = createAction(SHOW_LOGIN, message => ({message}));

export const showSnackBar = createAction(SHOW_SNACKBAR);
export const hideSnackBar = createAction(HIDE_SNACKBAR);

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

export function fetchCourse(uuid) {
  return dispatch => {
    dispatch(requestCourse());
    return api.getCourse(uuid).
      then(json => dispatch(receiveCourseSuccess(json))).
      catch(() => dispatch(receiveCourseFailure()));
  };
}

export function fetchCourseList() {
  return dispatch => {
    dispatch(requestCourseList());
    return api.getCourseList().
      then(json => dispatch(receiveCourseListSuccess(json))).
      catch(() => dispatch(receiveCourseListFailure()));
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
        type: CLEAR_COURSE
      });
    });
  };
}

export function login(username, password) {
  return dispatch => {
    return api.login(username, password).
      then((data) => {
        dispatch({
          type: CLEAR_COURSE
        });
        return dispatch(loginSuccess(data));
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
export const clearActivation = createAction(CLEAR_ACTIVATION);

export function activate(token) {
  return dispatch => {
    return api.activate(token).
      then(() => {
        dispatch(activateSuccess());
        sendGoogleAnalyticsEvent("User", "Activation", "Success");
      }).catch(e => {
        dispatch(activateFailure());
        sendGoogleAnalyticsEvent("User", "Activation", "Failure");
        // let anything afterwards catch the error too
        return Promise.reject(e);
      });
  };
}

export const updateCartItems = createAction(
  UPDATE_CART_ITEMS, (uuids, seats, courseUuid) => { return {uuids, seats, courseUuid}; });

export const clearCart = createAction(CLEAR_CART);
export const checkoutSuccess = createAction(CHECKOUT_SUCCESS);
export const checkoutFailure = createAction(CHECKOUT_FAILURE);
export const resetBuyTab = createAction(RESET_BUYTAB);

export function checkout(cart, token, total) {
  return dispatch => {
    return api.checkout(cart, token, total).
      then(() => {
        dispatch(checkoutSuccess());
        dispatch(clearCart());
        dispatch(resetBuyTab());
        sendGoogleEcommerceTransaction(token, total);
      }).
      catch(e => {
        dispatch(checkoutFailure());
        sendGoogleAnalyticsEvent("Purchase", "Rejected", "Failure", total);
        return Promise.reject(e);
      });
  };
}

export const updateSelectedChapters = createAction(
  UPDATE_SELECTED_CHAPTERS, (uuids, allRowsSelected)  => { return {uuids, allRowsSelected}; });

export const updateSeatCount = createAction(
  UPDATE_SEAT_COUNT, (seats) => { return { seats }; });
