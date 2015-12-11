import React from 'react';
import ReactDOM from 'react-dom';
import '../sass/layout.scss';
import App from './containers/App';
import CourseDetailPage from './containers/CourseDetailPage';
import { Provider } from 'react-redux';
import configureStore from './store/configureStore';
import { Router, Route } from 'react-router';

import createBrowserHistory from 'history/lib/createBrowserHistory';
import { devTools, persistState } from 'redux-devtools';
import { DevTools, DebugPanel, LogMonitor } from 'redux-devtools/lib/react';

const store = configureStore();

ReactDOM.render(
  <div>
    <Provider store={store}>
      <Router history={createBrowserHistory()}>
        <Route path="/" component={App}>
          <Route path="courses/:uuid" component={CourseDetailPage} />
        </Route>
      </Router>
    </Provider>
    <DebugPanel top right bottom>
      <DevTools store={store} monitor={LogMonitor} visibleOnLoad={false}/>
    </DebugPanel>
  </div>,
  document.getElementById("container")
);
