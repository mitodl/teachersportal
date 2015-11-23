import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';

class Body extends React.Component {
  render() {
    let courses;

    if (this.props.courses) {
      courses = this.props.courses.map(
        course => <div key={course.uuid}>{course.description}</div>
      );
    }

    return <div id="body">
        <Card id="page-card">
            <CardText>
                Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
                cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
                proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

              <button onClick={this.props.updateCourses}>Test</button>
              {courses}
            </CardText>
        </Card>
    </div>
    ;
  }
}

export default Body;
