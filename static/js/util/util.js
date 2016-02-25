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

function makeCourseLookup(courses) {
  let courseLookup = {};

  for (let course of courses) {
    courseLookup[course.uuid] = course;
  }

  return courseLookup;
}

export function calculateTotal(cart, courses) {
  let total = 0;

  let moduleLookup = makeModuleLookup(courses);

  for (let item of cart) {
    for (let uuid of item.uuids) {
      let module = moduleLookup[uuid];
      if (module !== undefined) {
        total += item.seats * module.price_without_tax;
      }
    }
  }

  return total;
}

export function getModule(moduleUuid, courses) {
  let moduleLookup = makeModuleLookup(courses);
  return moduleLookup[moduleUuid];
}

export function getCourse(courseUuid, courses) {
  let courseLookup = makeCourseLookup(courses);
  return courseLookup[courseUuid];
}

/**
 * Validates a cart. If the input cart was invalid, an empty list is returned.
 * If a course uuid doesn't match, that course is excluded from the cart.
 * If a module uuid doesn't match, that module is excluded from the cart (and
 * maybe the course too if all modules from the course are missing).
 *
 * Because the cart is stored in localStorage, the user can't just refresh their page
 * if the state is corrupted. This function aims to sanitize this part of the state.
 *
 * @param {Array} cart The cart (probably from state.cart.cart)
 * @param {Array} courses The courses (probably from state.course.courseList)
 * @returns {Array} A copy of the cart with invalid items or modules filtered out
 */
export function filterCart(cart, courses) {
  let moduleLookup = makeModuleLookup(courses);
  let courseLookup = {};
  for (let course of courses) {
    courseLookup[course.uuid] = course;
  }

  if (!(cart instanceof Array)) {
    return [];
  }

  // Filter type for each item
  let filteredCart = cart.filter(item => {
    if (typeof item.seats !== 'number') {
      return false;
    }
    if (!(item.uuids instanceof Array)) {
      return false;
    }
    let course = courseLookup[item.courseUuid];
    if (course === undefined) {
      return false;
    }
    return true;
  });

  // Filter out missing modules
  filteredCart = filteredCart.map(item => Object.assign({}, item, {
    uuids: item.uuids.filter(uuid => moduleLookup[uuid] !== undefined)
  }));

  // If the module list is now empty filter out the course too
  return filteredCart.filter(item => item.uuids.length > 0);
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

export function formatDollars(amount) {
  let cents = Math.round(amount * 100);
  let dollars = cents / 100;

  return `$${dollars.toFixed(2)}`;
}