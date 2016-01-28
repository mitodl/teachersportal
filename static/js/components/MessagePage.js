import React, { Component, PropTypes } from 'react';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import CardTitle from 'material-ui/lib/card/card-title';
import LinearProgress from 'material-ui/lib/linear-progress';

class MessagePage extends Component {
  render() {
    const { message, explanation, error } = this.props;

    let content;

    if (error !== undefined && error !== "") {
      content = <CardTitle className="message-title">{error}</CardTitle>;
    } else {
      content = <div>
        <CardTitle
          title={message}
          className="message-title"
        />
        <CardText className="message-description"  dangerouslySetInnerHTML={{__html: explanation }} />
      </div>;
    }

    return <div className="message-body">
      <Card className="message-content" style={{ 'height': "400px" }}>
        {content}
      </Card>
    </div>
      ;
  }
}

MessagePage.propTypes = {
  message: React.PropTypes.string,
  explanation: React.PropTypes.string,
  error: React.PropTypes.string
};

export default MessagePage;
