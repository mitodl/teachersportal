import { HELLO_WORLD_CHANGE_TEXT } from '../actions/hello_world';
import Immutable from 'immutable';

const initialState = Immutable.Map({
  text: "World"
});

export default function helloWorld(state = initialState, action) {
  switch (action.type) {
    case HELLO_WORLD_CHANGE_TEXT:
      return state.set("text", action.text);
    default:
      return state;
  }
}
