import React from 'react';
import RaisedButton from 'material-ui/lib/raised-button';
import Slider from 'material-ui/lib/slider';
import LeftNav from 'material-ui/lib/left-nav';
import MenuItem from 'material-ui/lib/menus/menu-item';
import AppBar from 'material-ui/lib/app-bar';
import IconButton from 'material-ui/lib/icon-button';
import NavigationClose from 'material-ui/lib/svg-icons/navigation/close';
import ChapterTab from './ChapterTab';
import StripeButton from './StripeButton';
import { getProduct } from '../util/util';

class BuyTab extends React.Component {
  componentWillReceiveProps(nextProps) {
    // Workaround for half baked LeftNav material-ui component
    const { buyTab: { cartVisibility } } = nextProps;

    if (cartVisibility !== this.refs.shoppingCart.state.open) {
      if (cartVisibility) {
        this.refs.shoppingCart.open();
      } else {
        this.refs.shoppingCart.close();
      }
    }
  }

  render() {
    const {
      selectable,
      product,
      productList,
      cart,
      buyTab,
      total,
      updateSelectedChapters,
      } = this.props;

    let cartContents = <MenuItem>No chapters selected</MenuItem>;

    if (cart.cart.length > 0) {
      cartContents = cart.cart.map((module, i) => {
        let cartProduct = getProduct(module.upc, productList);
        let title = "";
        if (cartProduct !== undefined) {
          title = cartProduct.title;
        }

        return <MenuItem
          key={module.upc}>{i}: {title}:
          Seats: {module.seats}
        </MenuItem>;
      });
    }

    const maxSeats = 200;

    return <div className="course-purchase-selector">
      <div className="seat-number-selector">
        <h3 className="slider-label">Seats</h3>
        <div className="scaled-slider">
          <Slider
            className="number-of-seats"
            name="number-of-seats"
            max={maxSeats}
            value={buyTab.seats}
            step={10}
            style={{ 'marginBottom': '5px' }}
            onChange={this.onUpdateSeatCount.bind(this)}
          />
          <div className="slider-scale">
            <span className="left">0</span>
            <span className="left-quarter">{maxSeats * 0.25}</span>
            <span className="middle">{maxSeats * 0.5}</span>
            <span className="right-quarter">{maxSeats * 0.75}</span>
            <span className="right">{maxSeats}</span>
          </div>
        </div>
        <div className="seatCount">{buyTab.seats}<br /><span className="seatCountLabel">Seats</span></div>
        <div className="selectionTotal">${total}<br /><span className="selectionTotalLabel">Total</span></div>
        <RaisedButton
          label="Update Cart"
          className="add-to-cart"
          onClick={this.onUpdateCartItems.bind(this)}
          secondary={true}
        />
      </div>
      <h3 className="chapter-label">Chapters</h3>
      <ChapterTab
        className="moduleSelector"
        selectable={selectable}
        multiSelectable={selectable}
        enableSelectAll={selectable}
        displaySelectAll={selectable}
        adjustForCheckbox={false}
        displayRowCheckbox={selectable}
        product={product}
        updateSelectedChapters={updateSelectedChapters}
        deselectOnClickaway={false}
        buyTab={buyTab}
      />
      <LeftNav
        docked={false}
        openRight={true}
        onRequestChange={this.onCartClose.bind(this)}
        ref="shoppingCart"
        className="shopping-cart"
        width={400}
      >
        <AppBar
          title="Cart Summary"
          iconElementLeft={
            <IconButton onTouchTap={this.onCartClose.bind(this)}>
              <NavigationClose />
            </IconButton>
          }
        />
        {cartContents}
        <div className="cart-actions">
          <StripeButton cart={cart} product={product} checkout={this.onCheckout.bind(this)}/>
        </div>
        <div className="cart-status">
          <span className="cart-total">${total}<br /><span className="cart-total-label">total cost</span></span>
        </div>
      </LeftNav>
    </div>;
  }

  onUpdateCartItems() {
    const {
      updateCartItems,
      buyTab: { seats, selectedChapters },
      updateCartVisibility
    } = this.props;

    updateCartItems(selectedChapters, seats);
    updateCartVisibility(true);
  }

  onUpdateSeatCount(e, value) {
    const { updateSeatCount } = this.props;
    updateSeatCount(value);
  }

  onCartClose() {
    const { updateCartVisibility } = this.props;
    updateCartVisibility(false);
  }

  onCheckout() {
    const { checkout, updateCartVisibility } = this.props;

    updateCartVisibility(false);
    checkout();
  }
}

export default BuyTab;

BuyTab.propTypes = {
  product: React.PropTypes.object.isRequired,
  productList: React.PropTypes.array.isRequired,
  selectable: React.PropTypes.bool.isRequired,
  cart: React.PropTypes.object.isRequired,
  buyTab: React.PropTypes.object.isRequired,
  checkout: React.PropTypes.func.isRequired,
  updateCartItems: React.PropTypes.func.isRequired,
  updateSelectedChapters: React.PropTypes.func.isRequired,
  updateSeatCount: React.PropTypes.func.isRequired,
  updateCartVisibility: React.PropTypes.func.isRequired,
};
