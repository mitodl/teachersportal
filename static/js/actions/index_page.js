import { getCourse, getModules } from '../util/api';

export const REQUEST_COURSE = 'REQUEST_COURSE';
export const RECEIVE_COURSE_SUCCESS = 'RECEIVE_COURSE_SUCCESS';
export const RECEIVE_COURSE_FAILURE = 'RECEIVE_COURSE_FAILURE';
export const REQUEST_MODULES = 'REQUEST_MODULES';
export const RECEIVE_MODULES_SUCCESS = 'RECEIVE_MODULES_SUCCESS';
export const RECEIVE_MODULES_FAILURE = 'RECEIVE_MODULES_FAILURE';
export const SHOW_LOGIN = 'SHOW_LOGIN';
export const HIDE_LOGIN = 'HIDE_LOGIN';

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
  return {
    type: HIDE_LOGIN
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
