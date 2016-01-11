/* global SETTINGS:false */
import '../global_init';
import assert from 'assert';
import { calculateTotal, filterCart, getProduct } from './util';
import { CART_WITH_ITEM, PRODUCT_RESPONSE } from './../constants';

describe('utility functions', () => {
  it('calculates the total of an empty cart', () => {
    assert.equal(calculateTotal([], []), 0);
  });

  it('calculates the total of a cart', () => {
    let sum = CART_WITH_ITEM[0].seats * PRODUCT_RESPONSE.children[0].price_without_tax;
    assert.equal(
      calculateTotal(CART_WITH_ITEM, [PRODUCT_RESPONSE]),
      sum
    );
  });

  it('skips items which are missing from the product list when calculating the total', () => {
    const cart = [{
      upc: "some other upc",
      seats: 3
    }];

    assert.deepEqual(
      calculateTotal(cart, [PRODUCT_RESPONSE]),
      0
    );
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
    assert.deepEqual(
      getProduct("missing", [PRODUCT_RESPONSE]),
      undefined
    );
  });

  it('filters out missing items from a cart', () => {
    assert.deepEqual(
      filterCart(CART_WITH_ITEM, [PRODUCT_RESPONSE]),
      CART_WITH_ITEM
    );
    // No products, so all items filtered out
    assert.deepEqual(
      filterCart(CART_WITH_ITEM, []),
      []
    );
  });
});
