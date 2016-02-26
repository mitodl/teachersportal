// Define globals we would usually get from Django
global.SETTINGS = {
  isAuthenticated: false,
  name: ""
};

// Make sure window and document are available for testing
require('jsdom-global')();
