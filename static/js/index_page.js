/* global StripeHandler:true, StripeCheckout:false, window:false, SETTINGS:false */
import React from 'react';
import ReactDOM from 'react-dom';
import '../sass/layout.scss';
import App from './containers/App';
import CourseDetailPage from './containers/CourseDetailPage';
import ActivatePage from './containers/ActivatePage';
import { Provider } from 'react-redux';
import configureStore from './store/configureStore';
import { Router, Route } from 'react-router';

import createBrowserHistory from 'history/lib/createBrowserHistory';
import { devTools, persistState } from 'redux-devtools';
import { DevTools, DebugPanel, LogMonitor } from 'redux-devtools/lib/react';
import { checkout } from './actions/index_page';

const store = configureStore();

StripeHandler = StripeCheckout.configure({
  key: SETTINGS.stripePublishableKey,
  locale: 'auto',
  billingAddress: true,
  zipCode: true,
  email: SETTINGS.email,
  token: token => {
    // User has confirmed the intent to pay, now process the transaction
    store.dispatch(checkout(store.getState().cart.cart, token.id));
  }
});

window.onpopstate = () => {
  // Close checkout on page navigation
  StripeHandler.close();
};

ReactDOM.render(
  <div>
    <Provider store={store}>
      <Router history={createBrowserHistory()}>
        <Route path="/" component={App}>
          <Route path="courses/:uuid" component={CourseDetailPage} />
          <Route path="activate" component={ActivatePage} />
        </Route>
      </Router>
    </Provider>
    <DebugPanel top right bottom>
      <DevTools store={store} monitor={LogMonitor} visibleOnLoad={false}/>
    </DebugPanel>
  </div>,
  document.getElementById("container")
);
