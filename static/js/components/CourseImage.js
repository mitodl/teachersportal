import React, { Component, PropTypes } from 'react';
import Card from 'material-ui/lib/card/card';
import CardMedia from 'material-ui/lib/card/card-media';

class CourseImage extends Component {
  render() {
    const { src } = this.props;
    let loremImage = "http://lorempixel.com/g/350/250/abstract";

    // TODO: When we're pointing at real images, use those.
    let image = loremImage;

    return <Card id="course-image">
      <CardMedia>
        <img src={image} alt="Course detail image"/>
      </CardMedia>
    </Card>;
  }
}

export default CourseImage;

CourseImage.propTypes = {
  src: React.PropTypes.string.isRequired
};
