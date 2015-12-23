/* global SETTINGS:false */
import {
  RECEIVE_COURSE_SUCCESS,
  RECEIVE_COURSE_FAILURE,
  REQUEST_COURSE,
  RECEIVE_MODULES_SUCCESS,
  RECEIVE_MODULES_FAILURE,
  REQUEST_MODULES,
  CLEAR_COURSES_AND_MODULES,
  SHOW_LOGIN,
  HIDE_LOGIN,
  FETCH_FAILURE,
  FETCH_PROCESSING,
  FETCH_SUCCESS,
  LOGIN_FAILURE,
  LOGIN_SUCCESS,
  LOGOUT,
  CLEAR_AUTHENTICATION_ERROR,
} from '../actions/index_page';

export function courses(state = {}, action) {
  switch (action.type) {

  case REQUEST_COURSE:
    return Object.assign({}, state, {
      courseFetchStatus: FETCH_PROCESSING
    });
  case RECEIVE_COURSE_SUCCESS:
    return Object.assign({}, state, {
      courseFetchStatus: FETCH_SUCCESS,
      course: action.course
    });
  case RECEIVE_COURSE_FAILURE:
    return Object.assign({}, state, {
      courseFetchStatus: FETCH_FAILURE
    });

  case REQUEST_MODULES:
    return Object.assign({}, state, {
      modulesFetchStatus: FETCH_PROCESSING
    });
  case RECEIVE_MODULES_SUCCESS:
    return Object.assign({}, state, {
      modulesFetchStatus: FETCH_SUCCESS,
      modules: action.modules
    });
  case RECEIVE_MODULES_FAILURE:
    return Object.assign({}, state, {
      modulesFetchStatus: FETCH_FAILURE
    });
  case CLEAR_COURSES_AND_MODULES:
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
      error: "Unable to log in"
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