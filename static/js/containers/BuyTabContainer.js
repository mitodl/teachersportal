/* global StripeHandler:false */
import React from 'react';
import { connect } from 'react-redux';
import BuyTab from '../components/BuyTab';
import {
  resetBuyTab,
  updateCartItems,
  updateCartVisibility,
  updateSelectedChapters,
  updateSeatCount,
  checkout
} from '../actions/index_page';
import { calculateTotal } from '../util/util';


class BuyTabContainer extends React.Component {
  render() {
    const { course, courseList, cart, buyTab, dispatch } = this.props;

    let total = this.updateTotal();

    return <BuyTab
      selectable={true}
      course={course}
      courseList={courseList}
      cart={cart}
      buyTab={buyTab}
      buyTabTotal={total}
      dispatch={dispatch}

      updateCartItems={this.onUpdateCartItems.bind(this)}
      updateSelectedChapters={this.onUpdateSelectedChapters.bind(this)}
      updateSeatCount={this.onUpdateSeatCount.bind(this)}
      updateCartVisibility={this.onUpdateCartVisibility.bind(this)}

      checkout={this.onCheckout.bind(this)}

      />;
  }

  componentWillUnmount() {
    const { dispatch } = this.props;
    dispatch(resetBuyTab());
  }

  updateTotal() {
    const { buyTab, course, courseList } = this.props;

    let cart = [{
      courseUuid: course.uuid,
      seats: buyTab.seats,
      uuids: buyTab.selectedChapters
    }];

    let total = calculateTotal(cart, courseList);

    return total;
  }

  onUpdateSeatCount(seats) {
    const { dispatch } = this.props;

    dispatch(updateSeatCount(seats));
  }

  onUpdateSelectedChapters(uuids, allRowsSelected) {
    const { dispatch } = this.props;

    dispatch(updateSelectedChapters(uuids, allRowsSelected));
  }

  onUpdateCartItems(uuids, seats) {
    const { dispatch, course } = this.props;
    dispatch(updateCartItems(uuids, seats, course.uuid));
  }

  onUpdateCartVisibility(visibility) {
    const { dispatch } = this.props;
    dispatch(updateCartVisibility(visibility));
  }

  onCheckout() {
    const { dispatch, cart, courseList } = this.props;

    let total = calculateTotal(cart.cart, courseList);
    if (total === 0) {
      dispatch(checkout(cart.cart, "", total));
    } else {
      StripeHandler.open({
        name: 'MIT Teacher\'s Portal',
        description: cart.cart.length + ' course(s)',
        amount: Math.floor(total * 100)
      });
    }
  }
}

BuyTabContainer.propTypes = {
  course: React.PropTypes.object.isRequired,
  courseList: React.PropTypes.array.isRequired,
  cart: React.PropTypes.object.isRequired,
  buyTab: React.PropTypes.object.isRequired,
  selectable: React.PropTypes.bool.isRequired,
  fixedHeader: React.PropTypes.bool,
  fixedFooter: React.PropTypes.bool,
  stripedRows: React.PropTypes.bool,
  showRowHover: React.PropTypes.bool,
  deselectOnClickaway: React.PropTypes.bool,
  height: React.PropTypes.string,
  dispatch: React.PropTypes.func.isRequired
};

const mapStateToProps = (state) => {
  return {
    cart: state.cart,
    buyTab: state.buyTab
  };
};

export default connect(mapStateToProps)(BuyTabContainer);
