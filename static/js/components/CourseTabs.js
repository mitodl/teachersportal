import React from 'react';
import Card from 'material-ui/lib/card/card';
import Tabs from 'material-ui/lib/tabs/tabs';
import Tab from 'material-ui/lib/tabs/tab';
import ChapterTab from './ChapterTab';
import AboutTab from './AboutTab';
import ReviewsTab from './ReviewsTab';
import BuyTabContainer from '../containers/BuyTabContainer';
import ga from 'react-ga';

// Required for material ui tabs
import injectTapEventPlugin from "react-tap-event-plugin";
injectTapEventPlugin();

class CourseTabs extends React.Component {

  render() {

    const { course, courseList } = this.props;

    return <Card id="course-tabs-card">
        <Tabs id="course-tabs">
            <Tab label="About" id="about" className="tab" onActive={this.handleActive}>
                <AboutTab content={course.info.overview} />
            </Tab>
            <Tab label="Content" id="content" className="tab" onActive={this.handleActive}>
                <ChapterTab
                  selectable={false}
                  fixedHeader={true}
                  fixedFooter={true}
                  stripedRows={false}
                  showRowHover={true}
                  deselectOnClickaway={true}
                  height={'auto'}
                  course={course}
                  courseList={courseList}
                 />
            </Tab>
            <Tab label="Buy" id="buy" className="tab" onActive={this.handleActive}>
                <BuyTabContainer
                  selectable={true}
                  fixedHeader={true}
                  fixedFooter={true}
                  stripedRows={false}
                  showRowHover={true}
                  deselectOnClickaway={true}
                  height={'auto'}
                  course={course}
                  courseList={courseList}
                />
            </Tab>
        </Tabs>
      </Card>;
  }

  handleActive(tab) {
    ga.event({
      category: "Tab",
      action: "Activate",
      label: tab.props.label
    });
  }
}

export default CourseTabs;

CourseTabs.propTypes = {
  course: React.PropTypes.object.isRequired,
  courseList: React.PropTypes.array.isRequired
};
