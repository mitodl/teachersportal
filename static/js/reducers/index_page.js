import { RECEIVE_COURSES, REQUEST_COURSES } from '../actions/index_page';
import Immutable from 'immutable';

export function courses(state = Immutable.Map(), action) {
  switch (action.type) {
  case REQUEST_COURSES:
    return state.set("isFetching", true);
  case RECEIVE_COURSES:
    return state.
      set("isFetching", false).
      set("courses", action.courses);
  default:
    return state;
  }
}
