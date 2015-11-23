/* global SETTINGS:false, fetch: false */
// For mocking purposes we need to use 'fetch' defined as a global instead of importing as a local.
import 'isomorphic-fetch';
import Immutable from 'immutable';
const { ccxconApi } = SETTINGS;

export function getCourses() {
  return fetch(`${ccxconApi}api/v1/coursexs/`).
    then(response => Immutable.fromJS(response.json()));
}
