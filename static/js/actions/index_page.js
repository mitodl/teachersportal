import Immutable from 'immutable';
import { getCourses } from '../util/api';

export const REQUEST_COURSES = 'REQUEST_COURSES';
export const RECEIVE_COURSES = 'RECEIVE_COURSES';

export const SHOW_LOGIN = 'SHOW_LOGIN';
export const HIDE_LOGIN = 'HIDE_LOGIN';

export const UPDATE_COURSE_SELECTION = 'UPDATE_COURSE_SELECTION';
export const UPDATE_COURSE_SELECT_ALL = 'UPDATE_COURSE_SELECT_ALL';


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
      then(json => dispatch(receiveCourses(Immutable.fromJS(json))));
  };
}

export function updateCourseSelection(course, selected) {
  return {
    type: UPDATE_COURSE_SELECTION,
    course: course,
    selected: selected
  };
}

export function updateCourseSelectAll(selected) {
  return {
    type: UPDATE_COURSE_SELECT_ALL,
    selected: selected
  };
}
