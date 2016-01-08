import React from 'react';
import Card from 'material-ui/lib/card/card';
import Tabs from 'material-ui/lib/tabs/tabs';
import Tab from 'material-ui/lib/tabs/tab';
import ChapterTab from './ChapterTab';
import AboutTab from './AboutTab';
import ReviewsTab from './ReviewsTab';
import BuyTabContainer from '../containers/BuyTabContainer';

// Required for material ui tabs
import injectTapEventPlugin from "react-tap-event-plugin";
injectTapEventPlugin();

class CourseTabs extends React.Component {
  render() {

    const { product, productList } = this.props;

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
                  productList={productList}
                 />
            </Tab>
            <Tab label="Buy" id="buy" className="tab">
                <BuyTabContainer
                  selectable={true}
                  fixedHeader={true}
                  fixedFooter={true}
                  stripedRows={false}
                  showRowHover={true}
                  deselectOnClickaway={true}
                  height={'auto'}
                  product={product}
                  productList={productList}
                />
            </Tab>
        </Tabs>
      </Card>;
  }
}

export default CourseTabs;

CourseTabs.propTypes = {
  product: React.PropTypes.object.isRequired,
  productList: React.PropTypes.array.isRequired
};
