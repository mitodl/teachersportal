/* global SETTINGS:false */
import '../global_init';
import assert from 'assert';
import { calculateTotal, filterCart, getModule } from './util';
import { CART_WITH_ITEM, COURSE_RESPONSE } from './../constants';

describe('utility functions', () => {
  it('calculates the total of an empty cart', () => {
    assert.equal(calculateTotal([], []), 0);
  });

  it('calculates the total of a cart', () => {
    let sum = CART_WITH_ITEM[0].seats * COURSE_RESPONSE.modules[0].price_without_tax;
    assert.equal(
      calculateTotal(CART_WITH_ITEM, [COURSE_RESPONSE]),
      sum
    );
  });

  it('skips items which are missing from the course list when calculating the total', () => {
    const cart = [{
      uuid: "some other uuid",
      seats: 3
    }];

    assert.deepEqual(
      calculateTotal(cart, [COURSE_RESPONSE]),
      0
    );
  });

  it('looks up a module', () => {
    assert.deepEqual(
      getModule(COURSE_RESPONSE.modules[0].uuid, [COURSE_RESPONSE]),
      COURSE_RESPONSE.modules[0]
    );
    // No courses in module lookup
    assert.deepEqual(
      getModule(COURSE_RESPONSE.uuid, [COURSE_RESPONSE]),
      undefined
    );
  });

  it('fails to look up a module if it is missing', () => {
    assert.deepEqual(
      getModule("missing", [COURSE_RESPONSE]),
      undefined
    );
  });

  it('filters out missing items from a cart', () => {
    assert.deepEqual(
      filterCart(CART_WITH_ITEM, [COURSE_RESPONSE]),
      CART_WITH_ITEM
    );
    // No courses, so all items filtered out
    assert.deepEqual(
      filterCart(CART_WITH_ITEM, []),
      []
    );
  });
});
