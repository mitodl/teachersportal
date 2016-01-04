import { combineReducers } from 'redux';
import {
  courses,
  loginModal,
  authentication,
  registration,
  activation,
} from './index_page';

export default combineReducers({
  courses,
  loginModal,
  authentication,
  registration,
  activation,
});
