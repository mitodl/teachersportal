import { combineReducers } from 'redux';
import {
  loginModal,
  snackBar,
  authentication,
  registration,
  activation,
  product,
  cart,
  buyTab,
} from './index_page';

export default combineReducers({
  product,
  loginModal,
  snackBar,
  authentication,
  registration,
  activation,
  cart,
  buyTab,
});
