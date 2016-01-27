import React, { Component, PropTypes } from 'react';
import Card from 'material-ui/lib/card/card';
import CardMedia from 'material-ui/lib/card/card-media';

class CourseCardImage extends Component {
  render() {
    const { src } = this.props;
    let image = src;

    return <Card className="course-card-image">
      <CardMedia style={{'width': "300px"}}>
        <img src={image} alt="Course detail image"/>
      </CardMedia>
    </Card>;
  }
}

export default CourseCardImage;

CourseCardImage.propTypes = {
  src: React.PropTypes.string.isRequired
};
