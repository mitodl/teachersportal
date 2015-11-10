export const HELLO_WORLD_CHANGE_TEXT = 'HELLO_WORLD_CHANGE_TEXT';

export function updateText(text) {
  return {
    type: HELLO_WORLD_CHANGE_TEXT,
    text: text
  };
}