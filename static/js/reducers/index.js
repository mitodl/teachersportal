import { combineReducers } from 'redux';
import {
  loginModal,
  authentication,
  registration,
  activation,
  product,
} from './index_page';

export default combineReducers({
  product,
  loginModal,
  authentication,
  registration,
  activation,
});
