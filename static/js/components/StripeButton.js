/* global StripeHandler:false */
import React from 'react';
import { calculateTotal } from '../util/util';
import RaisedButton from 'material-ui/lib/raised-button';

class StripeButton extends React.Component {
  render() {
    const { checkout } = this.props;

    return <RaisedButton
      label="Checkout"
      id="checkout"
      onClick={checkout}
      secondary={true}
      style={{ 'textAlign': 'center', 'display': 'block' }}
    />;
  }
}

export default StripeButton;

StripeButton.propTypes = {
  checkout: React.PropTypes.func.isRequired,
  cart: React.PropTypes.object.isRequired,
  product: React.PropTypes.object.isRequired
};
