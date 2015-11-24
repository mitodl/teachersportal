/* global describe:false, it:false */
import { showLoginModal } from '../static/js/reducers/index_page';
import { showLogin, hideLogin } from '../static/js/actions/index_page';
import assert from 'assert';

describe('login reducer', () => {
  it('should set login state to show when triggered', () => {
    assert(showLoginModal(null, showLogin()) == true);
  });

  it('should set login state to hide when triggered', () => {
    assert(showLoginModal(null, hideLogin()) == false);
  });
});
