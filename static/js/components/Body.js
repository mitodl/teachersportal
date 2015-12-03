import React from 'react';
import { Grid, Cell, Card, CardTitle, CardText } from 'react-mdl';
import CourseTabs from '../components/CourseTabs';

class Body extends React.Component {
  render() {
    let courses;

    if (this.props.courses) {
      courses = this.props.courses.map(
        course => <div key={course.uuid}>{course.description}</div>
      );
    }

    return <div id="course-body">
        <Card id="course-content" shadow={1} style={{width: '1300px'}}>
          <Grid className="course-title-grid" style={{width: '100%', margin: '0'}}>
              <Cell col={12}>
                <CardTitle id="course-title" shadow={0}>Introductory Physics: Classical Mechanics</CardTitle>
                <CardTitle id="course-byline" shadow={0}>by David E. Pritchard</CardTitle>
              </Cell>
          </Grid>
          <Grid className="course-info-grid" style={{width: '100%', margin: '0'}}>
              <Cell col={4}>
                <Card id="course-image-card" shadow={2} style={{ width: '385px'}}>
                  <CardTitle id="course-image" style={{color: '#fff', background: 'url(http://lorempixel.com/g/350/250/abstract) center / cover'}}></CardTitle>
                </Card>
              </Cell>
              <Cell col={8}>
                <CardText id="course-description">
                    Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
                    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
                    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
                    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
                    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
                    proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

                  <button onClick={this.props.updateCourses}>Test</button>
                  {courses}
                </CardText>
              </Cell>
          </Grid>
          <Grid className="course-tab-grid" style={{width: '100%', margin: '0'}}>
              <Cell col={12} tablet={8}>
                <CourseTabs />
              </Cell>
          </Grid>
        </Card>
      </div>
    ;
  }
}

export default Body;
