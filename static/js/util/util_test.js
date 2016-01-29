/* global SETTINGS:false */
import '../global_init';
import assert from 'assert';
import { calculateTotal, filterCart, getModule } from './util';
import { CART, COURSE_RESPONSE1, COURSE_LIST } from './../constants';

describe('utility functions', () => {
  it('calculates the total of an empty cart', () => {
    assert.equal(calculateTotal([], []), 0);
  });

  it('calculates the total of a cart', () => {
    let sum = 0;
    for (let item of CART) {
      let module = getModule(item.uuid, COURSE_LIST);
      sum += item.seats * module.price_without_tax;
    }
    assert.equal(
      calculateTotal(CART, COURSE_LIST),
      sum
    );
  });

  it('skips items which are missing from the course list when calculating the total', () => {
    const cart = [{
      uuid: "some other uuid",
      seats: 3
    }];

    assert.deepEqual(
      calculateTotal(cart, COURSE_LIST),
      0
    );
  });

  it('looks up a module', () => {
    assert.deepEqual(
      getModule(COURSE_RESPONSE1.modules[0].uuid, COURSE_LIST),
      COURSE_RESPONSE1.modules[0]
    );
    // No courses in module lookup
    assert.deepEqual(
      getModule(COURSE_RESPONSE1.uuid, COURSE_LIST),
      undefined
    );
  });

  it('fails to look up a module if it is missing', () => {
    assert.deepEqual(
      getModule("missing", COURSE_LIST),
      undefined
    );
  });

  it('filters out missing items from a cart', () => {
    assert.deepEqual(
      filterCart(CART, COURSE_LIST),
      CART
    );
    // No courses, so all items filtered out
    assert.deepEqual(
      filterCart(CART, []),
      []
    );
  });
});
