function makeModuleLookup(courses) {
  let moduleLookup = {};

  for (let course of courses) {
    for (let child of course.modules) {
      moduleLookup[child.uuid] = child;
    }
  }

  return moduleLookup;
}

export function calculateTotal(cart, courses) {
  let total = 0;

  let moduleLookup = makeModuleLookup(courses);

  for (let item of cart) {
    let module = moduleLookup[item.uuid];
    if (module !== undefined) {
      total += item.seats * module.price_without_tax;
    }
  }

  return total;
}

export function getModule(moduleUuid, courses) {
  let moduleLookup = makeModuleLookup(courses);
  return moduleLookup[moduleUuid];
}

export function filterCart(cart, courses) {
  let moduleLookup = makeModuleLookup(courses);

  return cart.filter(item => moduleLookup[item.uuid] !== undefined);
}
