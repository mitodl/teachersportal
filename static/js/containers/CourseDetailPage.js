import React from 'react';
import CourseDetail from '../components/CourseDetail';
import {
  fetchProduct,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseDetailPage extends React.Component {

  componentDidMount() {
    this.fetchProduct.call(this);
  }

  componentDidUpdate() {
    this.fetchProduct.call(this);
  }

  fetchProduct() {
    const {
      product,
      authentication,
      dispatch,
      params: { uuid }
    } = this.props;

    if (authentication.isAuthenticated) {
      // When user is authenticated and we haven't fetched courses and modules
      // yet, fetch them now. This might execute the fetch action twice if
      // this component is refreshed before action has a chance to dispatch,
      // but that shouldn't cause any problems
      if (product.status === undefined) {
        dispatch(fetchProduct("Course_" + uuid));
      }
    }
  }

  render() {
    const {
      product,
      authentication,
    } = this.props;

    let error;

    if (product.status === FETCH_FAILURE) {
      error = "An error occurred fetching information about this course.";
    } else if (!authentication.isAuthenticated) {
      error = "Please log in to view the course information.";
    }

    let detail = <CourseDetail error={error} product={product.product} />;

    return <div>
      {detail}
      </div>
      ;
  }

}

CourseDetailPage.propTypes = {
  product: React.PropTypes.object.isRequired,
  authentication: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  params: React.PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    product: state.product,
    authentication: state.authentication,
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
