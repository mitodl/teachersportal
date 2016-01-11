/* global StripeHandler:false */
import React from 'react';
import { calculateTotal } from '../util/util';
import RaisedButton from 'material-ui/lib/raised-button';

class StripeButton extends React.Component {
  render() {
    const { checkout } = this.props;

    return <RaisedButton
      label="Checkout"
      className="checkout-button"
      onClick={checkout}
      secondary={true}
    />;
  }
}

export default StripeButton;

StripeButton.propTypes = {
  checkout: React.PropTypes.func.isRequired,
  cart: React.PropTypes.object.isRequired,
  product: React.PropTypes.object.isRequired
};
