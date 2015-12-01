import React from 'react';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import CourseTabs from '../components/CourseTabs';
import CardActions from 'material-ui/lib/card/card-actions';
import CardExpandable from 'material-ui/lib/card/card-expandable';
import CardHeader from 'material-ui/lib/card/card-header';
import CardMedia from 'material-ui/lib/card/card-media';
import CardTitle from 'material-ui/lib/card/card-title';
import Lorem from './Lorem';

class Body extends React.Component {
  render() {
    let courses;

    if (this.props.courses) {
      courses = this.props.courses.map(
        course => <div key={course.uuid}>{course.description}</div>
      );
    }

    return <div id="course-body">
        <Card id="course-content">
          <CardTitle
            title="Introductory Physics: Classical Mechanics"
            subtitle="by David E. Pritchard"
            id="course-title"
          />
          <Card id="course-image">
              <CardMedia>
                <img src="http://lorempixel.com/g/350/250/abstract" />
              </CardMedia>
          </Card>
          <CardText id="course-description">
              <Lorem />
              <button onClick={this.props.updateCourses}>Test</button>
              {courses}
          </CardText>
          <CourseTabs />
        </Card>
    </div>
    ;
  }
}

export default Body;
