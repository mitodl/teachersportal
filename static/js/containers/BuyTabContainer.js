/* global StripeHandler:false */
import React from 'react';
import { connect } from 'react-redux';
import BuyTab from '../components/BuyTab';
import {
  updateCartItems,
  updateCartVisibility,
  updateSelectedChapters,
  updateSeatCount,
  checkout
} from '../actions/index_page';
import { calculateTotal } from '../util/util';


class BuyTabContainer extends React.Component {
  render() {
    const { product, productList, cart, buyTab } = this.props;

    return <BuyTab
      selectable={true}
      product={product}
      productList={productList}
      cart={cart}
      buyTab={buyTab}

      updateCartItems={this.onUpdateCartItems.bind(this)}
      updateSelectedChapters={this.onUpdateSelectedChapters.bind(this)}
      updateSeatCount={this.onUpdateSeatCount.bind(this)}
      updateCartVisibility={this.onUpdateCartVisibility.bind(this)}

      checkout={this.onCheckout.bind(this)}

      />;
  }

  onUpdateCartItems(upcs, seats) {
    const { dispatch, product } = this.props;

    dispatch(updateCartItems(upcs, seats, product.upc));
  }

  onUpdateSeatCount(seats) {
    const { dispatch } = this.props;

    dispatch(updateSeatCount(seats));
  }

  onCheckout() {
    const { dispatch, cart, productList } = this.props;

    let total = calculateTotal(cart.cart, productList);
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

  onUpdateSelectedChapters(upcs, allRowsSelected) {
    const { dispatch } = this.props;

    dispatch(updateSelectedChapters(upcs, allRowsSelected));
  }

  onUpdateCartVisibility(visibility) {
    const { dispatch } = this.props;
    dispatch(updateCartVisibility(visibility));
  }
}

BuyTabContainer.propTypes = {
  product: React.PropTypes.object.isRequired,
  productList: React.PropTypes.array.isRequired,
  cart: React.PropTypes.object.isRequired,
  buyTab: React.PropTypes.object.isRequired,
  selectable: React.PropTypes.bool.isRequired,
  fixedHeader: React.PropTypes.bool,
  fixedFooter: React.PropTypes.bool,
  stripedRows: React.PropTypes.bool,
  showRowHover: React.PropTypes.bool,
  deselectOnClickaway: React.PropTypes.bool,
  height: React.PropTypes.string
};

const mapStateToProps = (state) => {
  return {
    cart: state.cart,
    buyTab: state.buyTab
  };
};

export default connect(mapStateToProps)(BuyTabContainer);
