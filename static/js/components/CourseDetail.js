import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import CourseTabs from './CourseTabs';
import CourseImage from './CourseImage';
import CardActions from 'material-ui/lib/card/card-actions';
import CardExpandable from 'material-ui/lib/card/card-expandable';
import CardHeader from 'material-ui/lib/card/card-header';
import CardMedia from 'material-ui/lib/card/card-media';
import CardTitle from 'material-ui/lib/card/card-title';

class CourseDetail extends Component {
    render() {
      const { course, modules, error } = this.props;

      let content;

      if (error !== undefined) {
        content = <CardText>{error}</CardText>;
      } else if (course === undefined) {
        content = <div>
        </div>;
      } else {

        content = <div>
          <CardTitle
            title={course.title}
            subtitle={course.author}
            id="course-title"
          />
          <CourseImage src={course.image_url} />
          <CardText id="course-description">
              {course.description}
          </CardText>
          <CourseTabs course={course} modules={modules} />
        </div>;
      }

      return <div id="course-body">
          <Card id="course-content">
            {content}
          </Card>
      </div>
      ;
    }
  }

CourseDetail.propTypes = {
  course: React.PropTypes.object,
  modules: React.PropTypes.array,
  error: React.PropTypes.string
};

export default CourseDetail;
