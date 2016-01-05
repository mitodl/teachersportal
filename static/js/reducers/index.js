import { combineReducers } from 'redux';
import {
  loginModal,
  authentication,
  registration,
  activation,
  product,
  cart,
} from './index_page';

export default combineReducers({
  product,
  loginModal,
  authentication,
  registration,
  activation,
  cart,
});
