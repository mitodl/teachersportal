import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import CourseTabs from '../components/CourseTabs';

class Body extends React.Component {
  render() {
    const { courses, updateCoursesIfAbsent, selectedCourses, updateCourseSelection,
      updateCourseSelectAll
      } = this.props;

    return <div id="body">
        <Card id="page-card">
            <CardText id="description">
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
                cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
                proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
            </CardText>
            <CourseTabs
              courses={courses}
              updateCoursesIfAbsent={updateCoursesIfAbsent}
              selectedCourses={selectedCourses}
              updateCourseSelection={updateCourseSelection}
              updateCourseSelectAll={updateCourseSelectAll}
            />
        </Card>
    </div>
    ;
  }
}

export default Body;
