import React, { Component, PropTypes } from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { Link } from 'react-router';
import Card from 'material-ui/lib/card/card';
import CourseCardImage from './CourseCardImage';
import CardTitle from 'material-ui/lib/card/card-title';
import CardText from 'material-ui/lib/card/card-text';
import CircularProgress from 'material-ui/lib/circular-progress';

class CourseCard extends Component {
  render() {
    const {
      course,
    } = this.props;

    let path = "/courses/" + course.uuid;

    let ccxDescription = course.info ? course.info.description : "";
    let description = course.description || ccxDescription;

    let content = <Card className="course-card">
      <CourseCardImage src="http://lorempixel.com/305/75/abstract/" />
      <Link to={path}>
        <CardTitle
          title={course.title}
          className="course-card-title"
        />
      </Link>
      <CardText
        className="course-card-description"
        dangerouslySetInnerHTML={{__html: description }}
      />
    </Card>;

    return <div className="course-card-body">
      <Card className="course-card-content">
        {content}
      </Card>
    </div>;
  }
}

CourseCard.propTypes = {
  course: React.PropTypes.object.isRequired,
};

export default CourseCard;
