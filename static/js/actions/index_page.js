import { getCourses } from '../util/api';

export const REQUEST_COURSES = 'REQUEST_COURSES';
export const RECEIVE_COURSES = 'RECEIVE_COURSES';

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

export function fetchCourses() {
  return dispatch => {
    dispatch(requestCourses());
    return getCourses().
      then(json => dispatch(receiveCourses(json)));
  };
}
