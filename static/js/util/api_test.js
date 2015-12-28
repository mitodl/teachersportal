/* global SETTINGS */
import '../global_init';
import assert from 'assert';
import ReactTestUtils from 'react-addons-test-utils';
import ReactDOM from 'react-dom';
import React from 'react';
import jsdom from 'mocha-jsdom';
import fetchMock from 'fetch-mock/src/server';
import {
  getProduct,
  login,
  logout,
  register,
  activate,
} from './api';

const PRODUCT_RESPONSE = {
  "upc": "Course_7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
  "title": "Course 7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
  "description": "Course description here",
  "external_pk": "7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
  "product_type": "Course",
  "price_without_tax": null,
  "parent_upc": null,
  "info": {
    "overview": "overview",
    "image_url": "http://youtube.com/",
    "description": "description",
    "author_name": "author",
    "title": "title"
  },
  "children": [
    {
      "info": {
        "subchapters": [],
        "title": "other course"
      },
      "parent_upc": "Course_7560bd21-7b1d-4c2f-8103-acc93b6c40b1",
      "product_type": "Module",
      "title": "Module ed99737e-d5bf-4b95-a467-bf4ecf31f7b0",
      "external_pk": "ed99737e-d5bf-4b95-a467-bf4ecf31f7b0",
      "children": [],
      "upc": "Module_ed99737e-d5bf-4b95-a467-bf4ecf31f7b0",
      "price_without_tax": 33.0
    }
  ]
};


describe('common api functions', function() {
  jsdom();

  it('gets a product', done => {
    const upc = PRODUCT_RESPONSE.upc;

    fetchMock.mock(`/api/v1/products/${upc}/`, PRODUCT_RESPONSE);
    getProduct(upc).then(receivedCourse => {
      assert.deepEqual(receivedCourse, PRODUCT_RESPONSE);

      done();
    });
  });

  it('fails to get a product', done => {
    const upc = PRODUCT_RESPONSE.upc;

    fetchMock.mock(`/api/v1/products/${upc}/`, {
      body: PRODUCT_RESPONSE,
      status: 400
    });
    getProduct(upc).catch(() => {
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

  afterEach(function() {
    fetchMock.restore();
  });
});
