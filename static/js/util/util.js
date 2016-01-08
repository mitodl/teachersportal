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
    if (product === undefined) {
      throw "Missing product " + item.upc;
    }
    total += item.seats * product.price_without_tax;
  }

  return total;
}

export function getProduct(upc, products) {
  let productLookup = makeProductLookup(products);
  let product = productLookup[upc];
  if (product === undefined) {
    throw "Missing product " + upc;
  }
  return product;
}
