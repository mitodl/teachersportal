/* global describe:false, it:false */
import './global_init';
import assert from 'assert';
import ReactTestUtils from 'react-addons-test-utils';
import ReactDOM from 'react-dom';
import React from 'react';
import jsdom from 'mocha-jsdom';
import fetchMock from 'fetch-mock/src/server';
import { getCourse, getModules } from '../static/js/util/api';

const COURSE_RESPONSE = {
  "uuid": "8cc92ca1-162d-4729-96fc-d1733ebc1a40",
  "title": "Course UUqGwgbPUZHF",
  "author_name": "Mr. Shannon Stoltenberg",
  "overview": "Sequi expedita aperiam assumenda sit et magnam.",
  "description": "At voluptatem et eveniet perspiciatis.",
  "image_url": "",
  "edx_instance": "https://edx.org/",
  "url": "https://localhost:8077/api/v1/coursexs/8cc92ca1-162d-4729-96fc-d1733ebc1a40/",
  "modules":
    "https://localhost:8077/api/v1/coursexs/8cc92ca1-162d-4729-96fc-d1733ebc1a40/modules/",
  "instructors": []
};

const MODULES_RESPONSE = [
  {
    "uuid": "74061e49-555f-4f66-91bd-80b1d1006f33",
    "title": "Module TltWJyznIOOC",
    "subchapters": [
      "Magni repudiandae dolor officiis nam sit eos minima.",
      "Est esse et nisi nostrum repudiandae temporibus quidem.",
      "Et ut illo sunt pariatur ducimus architecto id.",
      "Quasi ipsum quia eveniet nobis dolores fugit delectus.",
      "Ut similique repellendus veritatis necessitatibus id ut.",
      "Maiores laboriosam assumenda quia laudantium quis provident.",
      "Tenetur ab nesciunt cumque.",
      "Enim aut in debitis aliquam.",
      "Voluptatum aut expedita quo est.",
      "Harum nostrum inventore est eos eos sunt in.",
      "Vel aliquam et sed similique dolor voluptates fuga."
    ],
    "course": "https://localhost:8077/api/v1/coursexs/8cc92ca1-162d-4729-96fc-d1733ebc1a40/",
    "url": "https://localhost:8077/api/v1/coursexs/8cc92ca1-162d-4729-96fc-d1733ebc1a40" +
      "/modules/74061e49-555f-4f66-91bd-80b1d1006f33/"
  }
];

describe('common api functions', function () {
  jsdom();

  it('gets a course', done => {
    const { ccxconApi } = SETTINGS;
    const uuid = COURSE_RESPONSE.uuid;

    fetchMock.mock(`${ccxconApi}v1/coursexs/${uuid}/`, COURSE_RESPONSE);
    getCourse(uuid).then(receivedCourse => {
      assert.deepEqual(receivedCourse, COURSE_RESPONSE);

      done();
    });
  });

  it('fails to get a course', done => {
    const { ccxconApi } = SETTINGS;
    const uuid = COURSE_RESPONSE.uuid;

    fetchMock.mock(`${ccxconApi}v1/coursexs/${uuid}/`, {
      body: COURSE_RESPONSE,
      status: 400
    });
    getCourse(uuid).catch(() => {
      done();
    });
  });

  it('gets a course\'s modules', done => {
    const { ccxconApi } = SETTINGS;
    const uuid = COURSE_RESPONSE.uuid;

    fetchMock.mock(`${ccxconApi}v1/coursexs/${uuid}/modules/`, MODULES_RESPONSE);
    getModules(uuid).then(receivedModules => {
      assert.deepEqual(receivedModules, MODULES_RESPONSE);

      done();
    });
  });

  it('fails to get modules', done => {
    const { ccxconApi } = SETTINGS;
    const uuid = COURSE_RESPONSE.uuid;

    fetchMock.mock(`${ccxconApi}v1/coursexs/${uuid}/modules/`, {
      body: MODULES_RESPONSE,
      status: 400
    });
    getModules(uuid).catch(() => {
      done();
    });
  });

  afterEach(function() {
    fetchMock.restore();
  });
});
