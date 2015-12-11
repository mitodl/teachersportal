import {
  RECEIVE_COURSE_SUCCESS,
  RECEIVE_COURSE_FAILURE,
  REQUEST_COURSE,
  RECEIVE_MODULES_SUCCESS,
  RECEIVE_MODULES_FAILURE,
  REQUEST_MODULES,
  SHOW_LOGIN,
  FETCH_FAILURE,
  FETCH_PROCESSING,
  FETCH_SUCCESS
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

  default:
    return state;
  }
}

export function showLoginModal(state = false, action) {
  return action.type === SHOW_LOGIN;
}
