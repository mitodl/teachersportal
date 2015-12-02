import { RECEIVE_COURSES, REQUEST_COURSES, SHOW_LOGIN } from '../actions/index_page';

export function courses(state = {}, action) {
  switch (action.type) {
  case REQUEST_COURSES:
    return Object.assign({}, state, {
      isFetching: true
    });
  case RECEIVE_COURSES:
    return Object.assign({}, state, {
      isFetching: false,
      courses: action.courses
    });
  default:
    return state;
  }
}

export function showLoginModal(state = false, action) {
  return action.type === SHOW_LOGIN;
}
