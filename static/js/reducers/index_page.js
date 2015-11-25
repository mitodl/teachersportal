
import {
  SHOW_LOGIN,
  RECEIVE_COURSES,
  REQUEST_COURSES,
  UPDATE_COURSE_SELECTION,
  UPDATE_COURSE_SELECT_ALL
} from '../actions/index_page';

import Immutable from 'immutable';

export function courses(state = Immutable.Map(), action) {
  switch (action.type) {
  case REQUEST_COURSES:
    return state.set("isFetching", true);
  case RECEIVE_COURSES:
    return state.
      set("isFetching", false).
      set("courses", action.courses);
  case UPDATE_COURSE_SELECTION:
    let selectedCourses = state.get("selectedCourses", Immutable.Set());

    if (action.selected) {
      selectedCourses = selectedCourses.add(action.course);
    } else {
      selectedCourses = selectedCourses.delete(action.course);
    }
    return state.set("selectedCourses", selectedCourses);
  case UPDATE_COURSE_SELECT_ALL:
    return state.set("selectedCourses", Immutable.Set(state.get("courses")));
  default:
    return state;
  }
}

export function showLoginModal(state = false, action) {
  return action.type === SHOW_LOGIN;
}
