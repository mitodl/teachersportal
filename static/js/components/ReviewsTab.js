import React from 'react';
import List from 'material-ui/lib/lists/list';
import ListDivider from 'material-ui/lib/lists/list-divider';
import ListItem from 'material-ui/lib/lists/list-item';
import Colors from 'material-ui/src/styles/colors';
import Lorem from './Lorem';

class ReviewsTab extends React.Component {
  render() {
    return <List>
      <ListItem
        primaryText="Really Superb Material!"
        secondaryText={
          <p>
            <span style={{color: Colors.darkBlack}}>Amanda Johnson</span><br/>
            <Lorem />
          </p>
        }
        secondaryTextLines={2} />
      <ListDivider inset={true} />
      <ListItem
        primaryText="It's a pleasure to teach with this!"
        secondaryText={
          <p>
            <span style={{color: Colors.darkBlack}}>Dave Reynolds</span><br/>
            <Lorem />
          </p>
        }
        secondaryTextLines={2} />
      <ListDivider inset={true} />
      <ListItem
        primaryText="Terrific Stuff!"
        secondaryText={
          <p>
            <span style={{color: Colors.darkBlack}}>Marlo Thomas</span><br/>
            <Lorem />
          </p>
        }
        secondaryTextLines={2} />
    </List>
    ;
  }
}

export default ReviewsTab;
