import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import CourseTabs from './CourseTabs';
import CardActions from 'material-ui/lib/card/card-actions';
import CardExpandable from 'material-ui/lib/card/card-expandable';
import CardHeader from 'material-ui/lib/card/card-header';
import CardMedia from 'material-ui/lib/card/card-media';
import CardTitle from 'material-ui/lib/card/card-title';
import Lorem from './Lorem';
import { fetchCourses } from '../actions/index_page';

class CourseDetail extends Component {

    render() {
      const { course, modules, error } = this.props;

      let content;

      if (error !== undefined) {
        content = <CardText>{error}</CardText>;
      } else {
        let courseImageUrl = "http://lorempixel.com/g/350/250/abstract";

        if (course.image_url) {
          courseImageUrl = course.image_url;
        }

        content = <div>
          <CardTitle
            title={course.title}
            subtitle={course.author}
            id="course-title"
          />
          <Card id="course-image">
              <CardMedia>
                <img src={courseImageUrl} alt="Course detail image"/>
              </CardMedia>
          </Card>
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
