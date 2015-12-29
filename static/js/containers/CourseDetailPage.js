/* global StripeHandler:false */
import React from 'react';
import CourseDetail from '../components/CourseDetail';
import {
  fetchProduct,
  FETCH_FAILURE,
  FETCH_SUCCESS,
  addOrUpdateCartItem,
  checkout,
} from '../actions/index_page';
import { calculateTotal } from '../util/util';
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
      cart,
      authentication,
    } = this.props;

    let error;

    if (product.status === FETCH_FAILURE) {
      error = "An error occurred fetching information about this course.";
    } else if (!authentication.isAuthenticated) {
      error = "Please log in to view the course information.";
    }

    let detail = <CourseDetail
      error={error}
      cart={cart.cart}
      addToCart={this.addToCart.bind(this)}
      product={product.product}
      onCheckout={this.onCheckout.bind(this)}
    />;

    return <div>
      {detail}
      </div>
      ;
  }

  addToCart(upc, seats) {
    const { dispatch } = this.props;

    dispatch(addOrUpdateCartItem(upc, seats));
  }

  onCheckout() {
    const { dispatch, cart, product } = this.props;

    let total = calculateTotal(cart.cart, [product.product]);
    if (total === 0) {
      dispatch(checkout(cart.cart, ""));
    } else {
      StripeHandler.open({
        name: 'MIT Teacher\'s Portal',
        description: cart.cart.length + ' item(s)',
        amount: Math.floor(total * 100)
      });
    }
  }
}

CourseDetailPage.propTypes = {
  product: React.PropTypes.object.isRequired,
  authentication: React.PropTypes.object.isRequired,
  dispatch: React.PropTypes.func.isRequired,
  params: React.PropTypes.object.isRequired,
  cart: React.PropTypes.object.isRequired
};

const mapStateToProps = (state) => {
  return {
    product: state.product,
    authentication: state.authentication,
    cart: state.cart
  };
};

export default connect(mapStateToProps)(CourseDetailPage);
