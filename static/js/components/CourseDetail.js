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
import LinearProgress from 'material-ui/lib/linear-progress';

class CourseDetail extends Component {
  render() {
    const {
      course,
      courseList
    } = this.props;

    let content;

    if (course === undefined) {
      content = <LinearProgress mode="indeterminate" size="1" className="progress" />;
    } else {

      content = <div>
        <CardTitle
          title={course.title}
          subtitle={course.info.author_name}
          id="course-title"
        />
        <CourseImage src={course.info.image_url}/>
        <CardText
          id="course-description"
          dangerouslySetInnerHTML={{__html: course.description || course.info.description }}
        />
        <CourseTabs
          course={course}
          courseList={courseList}
        />
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
  courseList: React.PropTypes.array.isRequired
};

export default CourseDetail;
