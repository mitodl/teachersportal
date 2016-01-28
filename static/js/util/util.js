import ga from 'react-ga';

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

export function sendGoogleAnalyticsEvent(category, action, label, value) {
  let event = {
    category: category,
    action: action,
    label: label,
  };
  if (value !== undefined) {
    event.value = value;
  }
  ga.event(event);
}

export function sendGoogleEcommerceTransaction(id, revenue) {
  ga.plugin.require('ecommerce');
  ga.plugin.execute('ecommerce', 'addTransaction', {
    'Transaction ID': id,
    'revenue': revenue
  });
  ga.plugin.execute('ecommerce', 'send');
}
