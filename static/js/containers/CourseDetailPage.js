import React from 'react';
import CourseDetail from '../components/CourseDetail';
import {
  fetchProduct,
  fetchProductList,
  clearInvalidCartItems,
  showSnackBar,
  FETCH_FAILURE,
  FETCH_SUCCESS,
} from '../actions/index_page';
import { connect } from 'react-redux';

class CourseDetailPage extends React.Component {

  componentDidMount() {
    this.fetchProduct.call(this);
    this.handleError.call(this);
  }

  componentDidUpdate() {
    this.fetchProduct.call(this);
    this.handleError.call(this);
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

      if (product.productStatus === undefined) {
        dispatch(fetchProduct("Course_" + uuid));
      }
      if (product.productListStatus === undefined) {
        dispatch(fetchProductList()).then(() => {
          return dispatch(clearInvalidCartItems());
        });
      }
    }
  }

  render() {
    const {
      product,
      authentication,
      dispatch
    } = this.props;

    let error;

    let detail = <CourseDetail
      error={error}
      product={product.product}
      productList={product.productList}
    />;

    return <div>
      {detail}
      </div>
      ;
  }


  handleError() {
    const { product, dispatch, authentication } = this.props;

    let error;

    if (product.productStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about this course.";
    } else if (product.productListStatus === FETCH_FAILURE) {
      error = "An error occurred fetching information about other courses.";
    } else if (!authentication.isAuthenticated) {
      error = "Please log in to view the course information.";
    }
    if (error) {
      dispatch(showSnackBar({ message: error }));
    }
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
    authentication: state.authentication
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
