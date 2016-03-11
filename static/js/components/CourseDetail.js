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
import PleaseLogin from './PleaseLogin';

class CourseDetail extends Component {
  render() {
    const {
      authenticated,
      course,
      courseList
    } = this.props;

    let baseContent = <div>
      <CardTitle
        title={course.title}
        subtitle={course.author_name}
        id="course-title"
      />
      <CourseImage src={course.image_url}/>
      <CardText
        id="course-description"
        dangerouslySetInnerHTML={{__html: course.description }}
      />
    </div>;

    let content;
    if (authenticated) {
      content = <div>
        {baseContent}
        <CourseTabs
          course={course}
          courseList={courseList}
        />
      </div>;
    } else {
      content = <div>
          {baseContent}
          <PleaseLogin />
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
  course: React.PropTypes.object.isRequired,
  courseList: React.PropTypes.array.isRequired
};

export default CourseDetail;
