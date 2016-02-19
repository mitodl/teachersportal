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
import { getModule, getCourse, calculateTotal } from '../util/util';

const MAX_SEATS = 200;

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
      course,
      courseList,
      cart,
      buyTab,
      buyTabTotal,
      updateSelectedChapters,
      updateSeatCount,
      } = this.props;

    let cartContents = <MenuItem>No chapters selected</MenuItem>;

    if (cart.cart.length > 0) {
      cartContents = cart.cart.map((item, i) => {
        let course = getCourse(item.courseUuid, courseList);
        let title = "";
        if (course !== undefined) {
          title = course.title;
        }

        return <MenuItem
          key={item.courseUuid}>{i}: {title}:
          Seats: {item.seats}
        </MenuItem>;
      });
    }

    let cartTotal = calculateTotal(cart.cart, courseList);

    return <div className="course-purchase-selector">
      <div className="seat-number-selector">
        <h3 className="slider-label">Seats</h3>
        <div className="scaled-slider">
          <Slider
            className="number-of-seats"
            name="number-of-seats"
            max={MAX_SEATS}
            value={buyTab.seats}
            step={1}
            style={{ 'marginBottom': '5px' }}
            onChange={(e, value) => this.onUpdateSeatCount.call(this, value)}
          />
          <div className="slider-scale">
            <span className="left">0</span>
            <span className="left-quarter">{MAX_SEATS * 0.25}</span>
            <span className="middle">{MAX_SEATS * 0.5}</span>
            <span className="right-quarter">{MAX_SEATS * 0.75}</span>
            <span className="right">{MAX_SEATS}</span>
          </div>
        </div>
        <div className="seat-count">
          <input
            type="text"
            value={buyTab.seats}
            onChange={e => this.onUpdateSeatCount.call(this, e.target.value)}
            className="seat-count-text"
          />
          <br />
          <span className="seat-count-label">Seats</span>
        </div>
        <div className="selection-total">
          ${buyTabTotal}
          <br />
          <span className="selection-total-label">Total</span>
        </div>
        <RaisedButton
          label="Update Cart"
          className="add-to-cart"
          onClick={this.onUpdateCartItems.bind(this)}
          secondary={true}
        />
      </div>
      <h3 className="chapter-label">Chapters</h3>
      <ChapterTab
        className="module-selector"
        selectable={selectable}
        multiSelectable={selectable}
        enableSelectAll={selectable}
        displaySelectAll={selectable}
        adjustForCheckbox={false}
        displayRowCheckbox={selectable}
        course={course}
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
          <StripeButton cart={cart} course={course} checkout={this.onCheckout.bind(this)}/>
        </div>
        <div className="cart-status">
          <span className="cart-total">${cartTotal}<br /><span className="cart-total-label">total cost</span></span>
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

  onUpdateSeatCount(value) {
    const { updateSeatCount } = this.props;

    let number = parseInt(value);
    if (!isFinite(number)) {
      number = 0;
    }
    if (number < 0) {
      number = 0;
    }
    if (number > MAX_SEATS) {
      number = MAX_SEATS;
    }
    updateSeatCount(number);
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
  course: React.PropTypes.object.isRequired,
  courseList: React.PropTypes.array.isRequired,
  selectable: React.PropTypes.bool.isRequired,
  cart: React.PropTypes.object.isRequired,
  buyTab: React.PropTypes.object.isRequired,
  checkout: React.PropTypes.func.isRequired,
  updateCartItems: React.PropTypes.func.isRequired,
  updateSelectedChapters: React.PropTypes.func.isRequired,
  updateSeatCount: React.PropTypes.func.isRequired,
  updateCartVisibility: React.PropTypes.func.isRequired,
};
