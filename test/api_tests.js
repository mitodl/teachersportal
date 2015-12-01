/* global describe:false, it:false */
import './global_init';
import assert from 'assert';
import ReactTestUtils from 'react-addons-test-utils';
import ReactDOM from 'react-dom';
import React from 'react';
import jsdom from 'mocha-jsdom';
import fetchMock from 'fetch-mock/src/server';
import { getCourses } from '../static/js/util/api';

const COURSES_RESPONSE = [
  {
    "uuid": null,
    "title": "Introductory Physics: Classical Mechanics",
    "author": "David E. Pritchard",
    "video_url": null,
    "terms_url": null,
    "overview": "This is the course overview.",
    "description": "This is a college level Introductory Newtonian Mechanics",
    "resources": {
      "modules": null
    }
  }
];

describe('common api functions', function () {
  jsdom();

  it('gets courses', done => {
    const { ccxconApi } = SETTINGS;
    fetchMock.mock(`${ccxconApi}v1/coursexs/`, COURSES_RESPONSE);
    getCourses().then(receivedCourses => {
      assert(receivedCourses, COURSES_RESPONSE);

      done();
    });
  });

  afterEach(function() {
    fetchMock.reset();
  });
});
