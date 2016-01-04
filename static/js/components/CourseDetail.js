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
      const { product, error } = this.props;

      let content;

      if (error !== undefined) {
        content = <CardText>{error}</CardText>;
      } else if (product === undefined) {
        content = <div>
        </div>;
      } else {

        content = <div>
          <CardTitle
            title={product.title}
            subtitle={product.info.author_name}
            id="course-title"
          />
          <CourseImage src={product.info.image_url} />
          <CardText id="course-description">
              {product.description}
          </CardText>
          <CourseTabs product={product} />
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
  product: React.PropTypes.object,
  error: React.PropTypes.string
};

export default CourseDetail;
