/* global SETTINGS:false, fetch: false */
// For mocking purposes we need to use 'fetch' defined as a global instead of importing as a local.
import 'isomorphic-fetch';
import _ from 'lodash';

function getCookie(name) {
  let cookieValue = null;

  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';');

    for (var i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim();

      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + '=') {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function csrfSafeMethod(method) {
  // these HTTP methods do not require CSRF protection
  return /^(GET|HEAD|OPTIONS|TRACE)$/.test(method);
}

/**
 * Calls to fetch but does a few other things:
 *  - turn cookies on for this domain
 *  - set headers to handle JSON properly
 *  - handle CSRF
 *  - non 2xx status codes will reject the promise returned
 *  - response JSON is returned in place of response
 *
 * @param {string} input URL of fetch
 * @param {Object} init Settings to pass to fetch
 * @returns {Promise} The promise with JSON of the response
 */
function fetchJSONWithCSRF(input, init) {
  if (init === undefined) {
    init = {};
  }
  init.headers = init.headers || {};
  _.defaults(init.headers, {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  });

  let method = init.method || 'GET';

  if (!csrfSafeMethod(method)) {
    init.headers['X-CSRFToken'] = getCookie('csrftoken');
  }
  // turn on cookies for this domain
  init.credentials = 'same-origin';

  return fetch(input, init).then(response => {
    // Not using response.json() here since it doesn't handle empty responses
    // Also note that text is a promise here, not a string
    let text = response.text();

    // For non 2xx status codes reject the promise
    if (response.status < 200 || response.status >= 300) {
      return Promise.reject(text);
    }
    return text;
  }).then(text => {
    if (text.length !== 0) {
      return JSON.parse(text);
    } else {
      return "";
    }
  });
}

export function getProduct(upc) {
  return fetchJSONWithCSRF(`/api/v1/products/${upc}/`);
}

export function getProductList() {
  return fetchJSONWithCSRF('/api/v1/products/');
}

export function login(username, password) {
  return fetchJSONWithCSRF('/api/v1/login/', {
    method: 'POST',
    body: JSON.stringify({
      username: username,
      password: password
    })
  });
}

export function logout() {
  return fetchJSONWithCSRF('/api/v1/logout/', {
    method: 'POST'
  });
}

export function register(fullName, email, organization, password, redirect) {
  return fetchJSONWithCSRF('/api/v1/register/', {
    method: 'POST',
    body: JSON.stringify({
      "full_name": fullName,
      "email": email,
      "organization": organization,
      "password": password,
      "redirect": redirect
    })
  });
}

export function activate(token) {
  return fetchJSONWithCSRF('/api/v1/activate/', {
    method: 'POST',
    body: JSON.stringify({
      token
    })
  });
}

export function checkout(cart, token) {
  return fetchJSONWithCSRF('/api/v1/checkout/', {
    method: 'POST',
    body: JSON.stringify({
      cart: cart,
      token: token
    })
  });
}
