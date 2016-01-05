/* global SETTINGS:false */
import '../global_init';
import assert from 'assert';
import { calculateTotal, getProduct } from './util';
import { CART_WITH_ITEM, PRODUCT_RESPONSE } from './../constants';

describe('utility functions', () => {
  it('calculates the total of an empty cart', () => {
    assert.equal(calculateTotal([], []), 0);
  });

  it('calculates the total of a cart', () => {
    assert.equal(calculateTotal(CART_WITH_ITEM, [PRODUCT_RESPONSE]), 99);
  });

  it('fails to calculate the total if a product is missing from the product list', () => {
    const cart = [{
      upc: "some other upc",
      seats: 3
    }];

    assert.throws(() => {
      calculateTotal(cart, [PRODUCT_RESPONSE]);
    }, /Missing product/);
  });

  it('looks up a product', () => {
    assert.deepEqual(
      getProduct(PRODUCT_RESPONSE.children[0].upc, [PRODUCT_RESPONSE]),
      PRODUCT_RESPONSE.children[0]
    );
    assert.deepEqual(
      getProduct(PRODUCT_RESPONSE.upc, [PRODUCT_RESPONSE]),
      PRODUCT_RESPONSE
    );
  });

  it('fails to look up a product if it is missing', () => {
    assert.throws(() => {
      getProduct("missing", [PRODUCT_RESPONSE]);
    }, /Missing product/);
  });
});
