import React from 'react';
import Slider from 'material-ui/lib/slider';
import RaisedButton from 'material-ui/lib/raised-button';
import ChapterTab from './ChapterTab';
import StripeButton from './StripeButton';

class BuyTab extends React.Component {
  render() {
    const { selectable, product, cart, onCheckout } = this.props;

    return <div id="course-purchase-selector">
      <h3>Seats</h3>
      <Slider
        id="number-of-seats"
        name="number-of-seats"
        max={500}
        defaultValue={50}
        step={10}
        style={{ 'width': '600px', 'display': "inline-block" }}
      />
      <RaisedButton
        label="Add to Cart"
        id="add-to-cart"
        onClick={this.onAddToCart.bind(this)}
        secondary={true}
        style={{ 'display': "inline-block", 'position': 'absolute', "right": "75px", "top": "75px" }}/>
      <StripeButton cart={cart} product={product} onCheckout={onCheckout} />
      <ChapterTab
        selectable={selectable}
        multiSelectable={selectable}
        enableSelectAll={selectable}
        displaySelectAll={selectable}
        adjustForCheckbox={selectable}
        displayRowCheckbox={selectable}
        product={product}
      />
    </div>;
  }

  onAddToCart() {
    const { product, addToCart } = this.props;

    // TODO: fake data for testing
    addToCart(product.children[0].upc, 5);
  }
}

export default BuyTab;

BuyTab.propTypes = {
  product: React.PropTypes.object.isRequired,
  selectable: React.PropTypes.bool.isRequired,
  cart: React.PropTypes.array.isRequired,
  addToCart: React.PropTypes.func.isRequired,
  onCheckout: React.PropTypes.func.isRequired
};
