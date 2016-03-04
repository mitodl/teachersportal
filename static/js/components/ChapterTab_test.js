/* global localStorage:true, document:false, window: false */
import '../global_init';
import { Provider } from 'react-redux';
import configureTestStore from '../store/configureStore_test';
import assert from 'assert';
import sinon from 'sinon';
import React from 'react';
import ReactDOM from 'react-dom';
import TestUtils from 'react-addons-test-utils';

import ChapterTab from './ChapterTab';
import {
  COURSE_LIST,
  COURSE_RESPONSE1,
  COURSE_RESPONSE2,
  CART,
} from '../constants';
import * as api from '../util/api';
import { calculateTotal } from '../util/util';

let renderChapterTab = (buyTabState, updateSelectedChapters) => TestUtils.renderIntoDocument(
  <ChapterTab
    selectable={true}
    buyTab={buyTabState}
    updateSelectedChapters={updateSelectedChapters}
    fixedHeader={true}
    fixedFooter={true}
    stripedRows={true}
    showRowHover={true}
    deselectOnClickaway={false}
    height="100"
    course={COURSE_RESPONSE1}
  />
);

describe('ChapterTab', () => {
  it('selects all chapters', done => {
    let updateSelectedChapters = (uuids, allRowsSelected) => {
      assert.ok(allRowsSelected);
      assert.deepEqual(uuids, COURSE_RESPONSE1.modules.map(module => module.uuid));
      done();
    };

    let component = renderChapterTab({
      allRowsSelected: false,
      selectedChapters: [COURSE_RESPONSE1.modules[0].uuid],
    }, updateSelectedChapters);

    let selectAllCheckbox = ReactDOM.findDOMNode(component).querySelector("input");
    TestUtils.Simulate.change(selectAllCheckbox);
  });

  it('deselects all chapters', done => {
    let updateSelectedChapters = (uuids, allRowsSelected) => {
      assert.ok(!allRowsSelected);
      assert.deepEqual(uuids, []);
      done();
    };

    let component = renderChapterTab({
      allRowsSelected: true,
      selectedChapters: COURSE_RESPONSE1.modules.map(module => module.uuid)
    }, updateSelectedChapters);

    let selectAllCheckbox = ReactDOM.findDOMNode(component).querySelector("input");
    TestUtils.Simulate.change(selectAllCheckbox);
  });

  it('unchecks select all box when a chapter is unchecked', done => {
    let updateSelectedChapters = (uuids, allRowsSelected) => {
      assert.ok(!allRowsSelected);
      assert.deepEqual(uuids, [COURSE_RESPONSE1.modules[1].uuid]);
      done();
    };

    let component = renderChapterTab({
      allRowsSelected: true,
      selectedChapters: COURSE_RESPONSE1.modules.map(module => module.uuid)
    }, updateSelectedChapters);

    let checkbox = ReactDOM.findDOMNode(component).querySelector("tbody tr td input");
    TestUtils.Simulate.click(checkbox);
  });
});
