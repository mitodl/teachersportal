import React from 'react';
import Slider from 'material-ui/lib/slider';
import RaisedButton from 'material-ui/lib/raised-button';
import ChapterTab from '../components/ChapterTab';

class BuyTab extends React.Component {
    render() {
      const { selectable, product } = this.props;

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
            secondary={true}
            style={{ 'display': "inline-block", 'position': 'absolute', "right": "75px", "top": "75px" }} />
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
}

export default BuyTab;
