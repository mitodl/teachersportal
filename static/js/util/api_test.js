/* global SETTINGS:false */
import '../global_init';
import assert from 'assert';
import ReactTestUtils from 'react-addons-test-utils';
import ReactDOM from 'react-dom';
import React from 'react';
import fetchMock from 'fetch-mock/src/server';
import {
  getCourse,
  getCourseList,
  login,
  logout,
  register,
  activate,
  checkout,
} from './api';
import { COURSE_RESPONSE1 } from '../constants';


describe('common api functions', function() {
  this.timeout(5000);  // eslint-disable-line no-invalid-this

  it('gets a course', done => {
    const uuid = COURSE_RESPONSE1.uuid;

    fetchMock.mock(`/api/v1/courses/${uuid}/`, COURSE_RESPONSE1);
    getCourse(uuid).then(receivedCourse => {
      assert.deepEqual(receivedCourse, COURSE_RESPONSE1);

      done();
    });
  });

  it('fails to get a course', done => {
    const uuid = COURSE_RESPONSE1.uuid;

    fetchMock.mock(`/api/v1/courses/${uuid}/`, {
      body: COURSE_RESPONSE1,
      status: 400
    });
    getCourse(uuid).catch(() => {
      done();
    });
  });

  it('logs in successfully', done => {
    fetchMock.mock(`/api/v1/login/`, {
      status: 200
    });
    login("user", "pass").then(() => {
      done();
    });
  });

  it('fails to login', done => {
    fetchMock.mock(`/api/v1/login/`, {
      status: 400
    });
    login("user", "pass").catch(() => {
      done();
    });
  });

  it('logs out successfully', done => {
    fetchMock.mock(`/api/v1/logout/`, {
      status: 200
    });
    logout().then(() => {
      done();
    });
  });

  it('fails to log out', done => {
    fetchMock.mock(`/api/v1/logout/`, {
      status: 400
    });
    logout().catch(() => {
      done();
    });
  });

  it('registers successfully', done => {
    let expected = {
      "full_name": "full name",
      email: "email@example.com",
      password: "pass",
      organization: "org",
      redirect: "redirect"
    };

    fetchMock.mock(`/api/v1/register/`, function(url, opts) {
      assert.deepEqual(JSON.parse(opts.body), expected);
      return {
        body: {},
        status: 200
      };
    });

    register(
      expected["full_name"],
      expected.email,
      expected.organization,
      expected.password,
      expected.redirect
    ).then(() => {
      done();
    });
  });

  it('fails to register', done => {
    let expected = {
      "full_name": "full name",
      email: "email@example.com",
      password: "pass",
      organization: "org",
      redirect: "redirect"
    };

    fetchMock.mock(`/api/v1/register/`, function(url, opts) {
      assert.deepEqual(JSON.parse(opts.body), expected);
      return {
        status: 400
      };
    });

    register(
      expected["full_name"],
      expected.email,
      expected.organization,
      expected.password,
      expected.redirect
    ).catch(() => {
      done();
    });
  });

  it('activates successfully', done => {
    let expected = {
      token: "token"
    };

    fetchMock.mock(`/api/v1/activate/`, function(url, opts) {
      assert.deepEqual(JSON.parse(opts.body), expected);
      return {
        body: {},
        status: 200
      };
    });
    activate(expected.token).then(() => {
      done();
    });
  });

  it('fails to activate', done => {
    let expected = {
      token: "token"
    };

    fetchMock.mock(`/api/v1/activate/`, function(url, opts) {
      assert.deepEqual(JSON.parse(opts.body), expected);
      return {
        status: 400
      };
    });
    activate(expected.token).catch(() => {
      done();
    });
  });

  it('checks out successfully', done => {
    let input = {
      cart: [{
        uuids: ["uuid"],
        seats: 5,
        courseUuid: "courseUuid"
      }],
      token: "token",
      total: 500
    };
    let output = Object.assign({}, input, {
      cart: input.cart.map(item => ({
        uuids: item.uuids,
        seats: item.seats,
        course_uuid: item.courseUuid  // eslint-disable-line camelcase
      }))
    });

    fetchMock.mock('/api/v1/checkout/', (url, opts) => {
      assert.deepEqual(JSON.parse(opts.body), output);
      return {
        status: 200
      };
    });
    checkout(input.cart, input.token, input.total).then(() => {
      done();
    });
  });

  it('fails to checkout', done => {
    let input = {
      cart: [{
        uuids: ["uuid"],
        seats: 5,
        courseUuid: "courseUuid"
      }],
      token: "token",
      total: 500
    };
    let output = Object.assign({}, input, {
      cart: input.cart.map(item => ({
        uuids: item.uuids,
        seats: item.seats,
        course_uuid: item.courseUuid  // eslint-disable-line camelcase
      }))
    });

    fetchMock.mock('/api/v1/checkout/', (url, opts) => {
      assert.deepEqual(JSON.parse(opts.body), output);
      return {
        status: 400
      };
    });
    checkout(input.cart, input.token, input.total).catch(() => {
      done();
    });
  });

  it('gets a list of courses', done => {
    fetchMock.mock('/api/v1/courses/', () => {
      return {
        status: 200
      };
    });

    getCourseList().then(() => {
      done();
    });
  });

  it('fails to get a list of courses', done => {
    fetchMock.mock('/api/v1/courses/', () => {
      return {
        status: 400
      };
    });

    getCourseList().catch(() => {
      done();
    });
  });

  afterEach(function() {
    fetchMock.restore();
  });
});
