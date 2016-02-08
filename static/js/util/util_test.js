/* global SETTINGS:false */
import '../global_init';
import assert from 'assert';
import { calculateTotal, filterCart, getModule, getCourse } from './util';
import { CART, COURSE_RESPONSE1, COURSE_LIST } from './../constants';

describe('utility functions', () => {
  it('calculates the total of an empty cart', () => {
    assert.equal(calculateTotal([], []), 0);
  });

  it('calculates the total of a cart', () => {
    let sum = 0;
    for (let item of CART) {
      for (let uuid of item.uuids) {
        let module = getModule(uuid, COURSE_LIST);
        sum += item.seats * module.price_without_tax;
      }
    }
    assert.equal(
      calculateTotal(CART, COURSE_LIST),
      sum
    );
  });

  it('skips items which are missing from the course list when calculating the total', () => {
    const cart = [Object.assign({}, CART[0], {
      uuids: ["some other uuid"]
    })];

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

  it('looks up a course', () => {
    assert.deepEqual(
      getCourse(COURSE_RESPONSE1.uuid, COURSE_LIST),
      COURSE_RESPONSE1
    );
    // No modules in course lookup
    assert.deepEqual(
      getCourse(COURSE_RESPONSE1.modules[0].uuid, COURSE_LIST),
      undefined
    );
  });

  it('fails to get a course if it is missing', () => {
    assert.deepEqual(
      getCourse("missing", COURSE_LIST),
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

  describe('invalid items in a cart', () => {
    it('filters invalid types from a cart', () => {
      // Unless there is at least one valid item, return an empty list
      for (let input of [[], {}, null, "", 3]) {
        assert.deepEqual(filterCart(input, COURSE_LIST), []);
      }
    });

    it('filters items with missing or invalid keys', () => {
      for (let key of ["uuids", "courseUuid", "seats"]) {
        let item = Object.assign({}, CART[0]);
        delete item[key];
        assert.deepEqual(filterCart([item], COURSE_LIST), []);
      }
    });

    it('filters items with invalid keys', () => {
      for (let key of ["uuids", "courseUuid", "seats"]) {
        let item = Object.assign({}, CART[0]);
        item[key] = 'invalid';
        assert.deepEqual(filterCart([item], COURSE_LIST), []);
      }
    });

    it('filters out only modules that don\'t match up', () => {
      let item = Object.assign({}, CART[0], {
        uuids: ["invalid"].concat(CART[0].uuids)
      });
      assert.deepEqual(filterCart([item], COURSE_LIST), [CART[0]]);
    });

    it('filters out courses where all modules don\'t match up', () => {
      let item = Object.assign({}, CART[0], {
        uuids: ["invalid"]
      });
      assert.deepEqual(filterCart([item], COURSE_LIST), []);
    });
  });
});
