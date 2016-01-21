import React, { Component, PropTypes } from 'react';
import Card from 'material-ui/lib/card/card';
import CardText from 'material-ui/lib/card/card-text';
import CardTitle from 'material-ui/lib/card/card-title';
import LinearProgress from 'material-ui/lib/linear-progress';

class MessagePage extends Component {
  render() {
    const { message, explanation, error } = this.props;

    let content;

    if (error !== undefined) {
      content = <CardText>{error}</CardText>;
    } else {
      content = <div>
        <CardTitle
          title={message}
          id="message-title"
        />
        <CardText id="message-description">
        {explanation}
        </CardText>
      </div>;
    }

    return <div id="message-body">
      <Card id="message-content">
        {content}
      </Card>
    </div>
      ;
  }
}

MessagePage.propTypes = {
  message: React.PropTypes.object,
  explanation: React.PropTypes.array.isRequired,
  error: React.PropTypes.string
};

export default MessagePage;
