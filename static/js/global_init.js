// Define globals we would usually get from Django
global.SETTINGS = {
  isAuthenticated: false,
  name: ""
};

// Make sure window and document are available for testing
require('jsdom-global')();
// Fake getSelection so material-ui doesn't complain about not being
// in a browser
window.getSelection = () => ({
  removeAllRanges: () => {}
});
