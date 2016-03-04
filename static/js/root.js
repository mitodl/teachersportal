/* global StripeHandler:true, StripeCheckout:false, window:false, SETTINGS:false */
if (process.env.NODE_ENV !== 'production') {
  __webpack_public_path__ = `http://${SETTINGS.host}:8076/`;  // eslint-disable-line no-undef, camelcase
}

import React from 'react';
import ReactDOM from 'react-dom';
import '../sass/layout.scss';
import App from './containers/App';
import CourseListing from './containers/CourseListing';
import CourseDetailPage from './containers/CourseDetailPage';
import ActivatePage from './containers/ActivatePage';
import Homepage from './containers/Homepage';
import { Provider } from 'react-redux';
import configureStore from './store/configureStore';
import { Router, Route, IndexRoute } from 'react-router';
import createBrowserHistory from 'history/lib/createBrowserHistory';
import { devTools, persistState } from 'redux-devtools';
import { DevTools, DebugPanel, LogMonitor } from 'redux-devtools/lib/react';
import { checkout } from './actions/index_page';
import ga from 'react-ga';
import { calculateTotal } from './util/util';

const store = configureStore();

let debug = SETTINGS.reactGaDebug === "true";
ga.initialize(SETTINGS.gaTrackingID, { debug: debug });

StripeHandler = StripeCheckout.configure({
  key: SETTINGS.stripePublishableKey,
  locale: 'auto',
  billingAddress: true,
  zipCode: true,
  email: SETTINGS.email,
  token: token => {
    // User has confirmed the intent to pay, now process the transaction
    let total = calculateTotal(
      store.getState().cart.cart,
      store.getState().course.courseList
    );
    store.dispatch(checkout(store.getState().cart.cart, token.id, total));
  }
});

window.onpopstate = () => {
  // Close checkout on page navigation
  StripeHandler.close();
};

let debugTools;
if (process.env.NODE_ENV !== 'production') {
  debugTools = <DebugPanel top right bottom>
    <DevTools store={store} monitor={LogMonitor} visibleOnLoad={false}/>
  </DebugPanel>;
}

ReactDOM.render(
  <div>
    <Provider store={store}>
      <Router history={createBrowserHistory()}>
        <Route path="/" component={App} onUpdate={ga.pageview(window.location.pathname)}>
          <IndexRoute component={Homepage} />
          <Route path="courses" component={CourseListing} />
          <Route path="courses/:uuid" component={CourseDetailPage} />
          <Route path="activate" component={ActivatePage} />
        </Route>
      </Router>
    </Provider>
    {debugTools}
  </div>,
  document.getElementById("container")
);
