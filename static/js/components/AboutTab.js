import React from 'react';

class AboutTab extends React.Component {
  render() {
    const { content } = this.props;

    return <div id="course-about-tab" dangerouslySetInnerHTML={{__html: content }}></div>;
  }
}

export default AboutTab;

AboutTab.propTypes = {
  content: React.PropTypes.string.isRequired
};
