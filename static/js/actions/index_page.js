import {
  getCourse,
  getModules,
  login as apiLogin,
  logout as apiLogout,
} from '../util/api';

export const REQUEST_COURSE = 'REQUEST_COURSE';
export const RECEIVE_COURSE_SUCCESS = 'RECEIVE_COURSE_SUCCESS';
export const RECEIVE_COURSE_FAILURE = 'RECEIVE_COURSE_FAILURE';
export const REQUEST_MODULES = 'REQUEST_MODULES';
export const RECEIVE_MODULES_SUCCESS = 'RECEIVE_MODULES_SUCCESS';
export const RECEIVE_MODULES_FAILURE = 'RECEIVE_MODULES_FAILURE';
export const CLEAR_COURSES_AND_MODULES = 'CLEAR_COURSES_AND_MODULES';

export const SHOW_LOGIN = 'SHOW_LOGIN';
export const HIDE_LOGIN = 'HIDE_LOGIN';

export const FETCH_FAILURE = 'FETCH_FAILURE';
export const FETCH_SUCCESS = 'FETCH_SUCCESS';
export const FETCH_PROCESSING = 'FETCH_PROCESSING';

export const LOGIN_FAILURE = 'LOGIN_FAILURE';
export const LOGIN_SUCCESS = 'LOGIN_SUCCESS';
export const LOGOUT = 'LOGOUT';
export const CLEAR_AUTHENTICATION_ERROR = 'CLEAR_AUTHENTICATION_ERROR';

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
  };
}

export function fetchCourse(courseUuid) {
  return dispatch => {
    dispatch(requestCourse());
    return getCourse(courseUuid).
      then(json => dispatch(receiveCourseSuccess(json))).
      catch(() => dispatch(receiveCourseFailure()));
  };
}

export function fetchModules(courseUuid) {
  return dispatch => {
    dispatch(requestModules());
    return getModules(courseUuid).
      then(json => dispatch(receiveModulesSuccess(json))).
      catch(() => dispatch(receiveModulesFailure()));
  };
}

export function loginFailure() {
  return {
    type: LOGIN_FAILURE
  };
}

export function loginSuccess() {
  return {
    type: LOGIN_SUCCESS
  };
}

export function logout() {
  return dispatch => {
    return apiLogout().then(() => {
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
    return apiLogin(username, password).
      then(() => {
        dispatch(loginSuccess());
        dispatch(hideLogin());
      }).
      catch((e) => {
        dispatch(loginFailure());
        // let anything afterwards catch the error too
        return new Promise((resolve, reject) => {
          reject(e);
        });
      });
  };
}
