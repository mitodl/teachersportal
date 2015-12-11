import React from 'react';
import Lorem from './Lorem';

class AboutTab extends React.Component {
  render() {
    const { content } = this.props;

    return <div id="course-about-tab">
        { content }
    </div>;
  }
}

export default AboutTab;
