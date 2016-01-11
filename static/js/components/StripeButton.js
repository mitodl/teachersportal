/* global StripeHandler:false */
import React from 'react';
import { calculateTotal } from '../util/util';

class StripeButton extends React.Component {
  render() {
    const { onCheckout, cart, product } = this.props;
    let total = calculateTotal(cart, [product]);
    let text;
    if (total === 0) {
      text = "Checkout";
    } else {
      text = "Pay with card";
    }
    return <button onClick={onCheckout}>
      {text}
    </button>;
  }
}

export default StripeButton;

StripeButton.propTypes = {
  onCheckout: React.PropTypes.func.isRequired,
  cart: React.PropTypes.array.isRequired,
  product: React.PropTypes.object.isRequired
};
