import assert from 'assert';
import ReactTestUtils from 'react-addons-test-utils';
import ReactDOM from 'react-dom';
import React from 'react';

import HelloWorld from '../static/js/hello_world'

describe('hello world', function() {
  it('says Hello world', function(done) {

    let afterMount = function(component) {
      let text = ReactDOM.findDOMNode(
        ReactTestUtils.findRenderedDOMComponentWithTag(
          component, "h1"
        )
      ).innerHTML;
      assert.equal("Hello, world!", text);

      done();
    };

    ReactTestUtils.renderIntoDocument(
      <HelloWorld ref={afterMount} />
    );
  });
});
