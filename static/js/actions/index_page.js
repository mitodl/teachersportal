import { getCourses } from '../util/api';

export const REQUEST_COURSES = 'REQUEST_COURSES';
export const RECEIVE_COURSES = 'RECEIVE_COURSES';
export const SHOW_LOGIN = 'SHOW_LOGIN';
export const HIDE_LOGIN = 'HIDE_LOGIN';

export function requestCourses() {
  return {
    type: REQUEST_COURSES
  };
}

export function receiveCourses(json) {
  return {
    type: RECEIVE_COURSES,
    courses: json
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

export function fetchCourses() {
  return dispatch => {
    dispatch(requestCourses());
    return getCourses().
      then(json => dispatch(receiveCourses(json)));
  };
}
