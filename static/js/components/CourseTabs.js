import React from 'react';
import Tabs from 'material-ui/lib/tabs/tabs';
import Tab from 'material-ui/lib/tabs/tab';
// Required for material ui tabs
import injectTapEventPlugin from "react-tap-event-plugin";
injectTapEventPlugin();

import ContentTab from './ContentTab';

class CourseTabs extends React.Component {
  render() {
    const { courses, updateCoursesIfAbsent, selectedCourses, updateCourseSelection,
      updateCourseSelectAll } = this.props;

    return <div>
        <Tabs id="tabs">
            <Tab label="About" id="about" className="tab">
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                consequat.
            </Tab>
            <Tab label="Content" id="content" className="tab">
              <ContentTab
                courses={courses}
                updateCoursesIfAbsent={updateCoursesIfAbsent}
                updateCourseSelection={updateCourseSelection}
                selectedCourses={selectedCourses}
                updateCourseSelectAll={updateCourseSelectAll}
              />
            </Tab>
            <Tab label="Reviews" id="reviews" className="tab">
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                consequat.
            </Tab>
            <Tab label="Buy" id="buy" className="tab">
                Duis aute irure dolor in reprehenderit in voluptate velit esse
                cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
                proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            </Tab>
        </Tabs>
      </div>;
  }
}

export default CourseTabs;
