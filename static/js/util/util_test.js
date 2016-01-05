/* global SETTINGS:false */
import '../global_init';
import assert from 'assert';
import { calculateTotal } from './util';
import { PRODUCT_RESPONSE } from './../constants';

describe('utility functions', () => {
  it('calculates the total of an empty cart', () => {
    assert.equal(calculateTotal([], []), 0);
  });

  it('calculates the price per seat of a cart', () => {
    const cart = [{
      upc: PRODUCT_RESPONSE.children[0].upc,
      seats: 3
    }];

    assert.equal(calculateTotal(cart, [PRODUCT_RESPONSE]), 99);
  });

  it('errors if a product is missing from the product list', () => {
    const cart = [{
      upc: "some other upc",
      seats: 3
    }];

    assert.throws(() => {
      calculateTotal(cart, [PRODUCT_RESPONSE]);
    }, /Missing product/);
  });
});
