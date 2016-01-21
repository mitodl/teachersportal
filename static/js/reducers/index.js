import { combineReducers } from 'redux';
import {
  loginModal,
  snackBar,
  authentication,
  registration,
  activation,
  course,
  cart,
  buyTab,
} from './index_page';

export default combineReducers({
  course,
  loginModal,
  snackBar,
  authentication,
  registration,
  activation,
  cart,
  buyTab,
});
