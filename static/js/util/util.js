function makeProductLookup(products) {
  let productLookup = {};

  for (let product of products) {
    productLookup[product.upc] = product;
    for (let child of product.children) {
      productLookup[child.upc] = child;
    }
  }

  return productLookup;
}

export function calculateTotal(cart, products) {
  let total = 0, productLookup = makeProductLookup(products);

  for (let item of cart) {
    let product = productLookup[item.upc];
    if (product !== undefined) {
      total += item.seats * product.price_without_tax;
    }
  }

  return total;
}

export function getProduct(upc, products) {
  let productLookup = makeProductLookup(products);
  return productLookup[upc];
}

export function filterCart(cart, products) {
  let productLookup = makeProductLookup(products);

  return cart.filter(item => productLookup[item.upc] !== undefined);
}
