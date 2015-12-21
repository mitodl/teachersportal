import * as api from '../util/api';

// action type constants
export const REQUEST_COURSE = 'REQUEST_COURSE';
export const RECEIVE_COURSE_SUCCESS = 'RECEIVE_COURSE_SUCCESS';
export const RECEIVE_COURSE_FAILURE = 'RECEIVE_COURSE_FAILURE';
export const REQUEST_MODULES = 'REQUEST_MODULES';
export const RECEIVE_MODULES_SUCCESS = 'RECEIVE_MODULES_SUCCESS';
export const RECEIVE_MODULES_FAILURE = 'RECEIVE_MODULES_FAILURE';
export const CLEAR_COURSES_AND_MODULES = 'CLEAR_COURSES_AND_MODULES';

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

// constants for fetch status (these are not action types)
export const FETCH_FAILURE = 'FETCH_FAILURE';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_PROCESSING = 'FETCH_PROCESSING';

function requestCourse() {
  return {
    type: REQUEST_COURSE
  };
}

function receiveCourseSuccess(json) {
  return {
    type: RECEIVE_COURSE_SUCCESS,
    course: json
  };
}

function receiveCourseFailure() {
  return {
    type: RECEIVE_COURSE_FAILURE
  };
}

function requestModules() {
  return {
    type: REQUEST_MODULES
  };
}

function receiveModulesSuccess(json) {
  return {
    type: RECEIVE_MODULES_SUCCESS,
    modules: json
  };
}

function receiveModulesFailure() {
  return {
    type: RECEIVE_MODULES_FAILURE
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

export function fetchCourse(courseUuid) {
  return dispatch => {
    dispatch(requestCourse());
    return api.getCourse(courseUuid).
      then(json => dispatch(receiveCourseSuccess(json))).
      catch(() => dispatch(receiveCourseFailure()));
  };
}

export function fetchModules(courseUuid) {
  return dispatch => {
    dispatch(requestModules());
    return api.getModules(courseUuid).
      then(json => dispatch(receiveModulesSuccess(json))).
      catch(() => dispatch(receiveModulesFailure()));
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
        type: CLEAR_COURSES_AND_MODULES
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