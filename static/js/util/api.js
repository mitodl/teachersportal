/* global SETTINGS:false, fetch: false */
// For mocking purposes we need to use 'fetch' defined as a global instead of importing as a local.
import 'isomorphic-fetch';
const { ccxconApi } = SETTINGS;

export function getCourse(courseUuid) {
  return fetch(`${ccxconApi}v1/coursexs/${courseUuid}/`).
    then(response => {
      if (response.status < 200 || response.status >= 300) {
        throw response.json();
      }
      return response.json();
    });
}

export function getModules(courseUuid) {
  return fetch(`${ccxconApi}v1/coursexs/${courseUuid}/modules/`).
    then(response => {
      if (response.status < 200 || response.status >= 300) {
        throw response.json();
      }
      return response.json();
    });
}
