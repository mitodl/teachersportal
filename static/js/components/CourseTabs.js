import React from 'react';
import Card from 'material-ui/lib/card/card';
import Tabs from 'material-ui/lib/tabs/tabs';
import Tab from 'material-ui/lib/tabs/tab';
import ChapterTab from '../components/ChapterTab';
import AboutTab from '../components/AboutTab';
import ReviewsTab from '../components/ReviewsTab';
import BuyTab from '../components/BuyTab';

// Required for material ui tabs
import injectTapEventPlugin from "react-tap-event-plugin";
injectTapEventPlugin();

class CourseTabs extends React.Component {
  render() {
    const { product } = this.props;

    return <Card id="course-tabs-card">
        <Tabs id="course-tabs">
            <Tab label="About" id="about" className="tab">
                <AboutTab content={product.info.overview} />
            </Tab>
            <Tab label="Content" id="content" className="tab">
                <ChapterTab
                  selectable={false}
                  fixedHeader={true}
                  fixedFooter={true}
                  stripedRows={false}
                  showRowHover={true}
                  deselectOnClickaway={true}
                  height={'auto'}
                  product={product}
                 />
            </Tab>
            <Tab label="Reviews" id="reviews" className="tab">
                <ReviewsTab />
            </Tab>
            <Tab label="Buy" id="buy" className="tab">
                <BuyTab
                  selectable={true}
                  fixedHeader={true}
                  fixedFooter={true}
                  stripedRows={false}
                  showRowHover={true}
                  deselectOnClickaway={true}
                  height={'auto'}
                  product={product}
                />
            </Tab>
        </Tabs>
      </Card>;
  }
}

export default CourseTabs;

CourseTabs.propTypes = {
  product: React.PropTypes.object.isRequired
};
