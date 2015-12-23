import { combineReducers } from 'redux';
import { courses, loginModal, authentication } from './index_page';

export default combineReducers({
  courses,
  loginModal,
  authentication,
});
