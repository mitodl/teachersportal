import React from 'react';
import Header from '../components/Header';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import * as IndexPageActions from '../actions/index_page';

class IndexPage extends React.Component {
  render() {
    const {  } = this.props;

    return <div><Header
    />
      </div>
      ;
  }
}

const mapStateToProps = (state) => {
  return {
  };
};

function mapDispatchToProps(dispatch) {
  return bindActionCreators(IndexPageActions, dispatch);
}

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(IndexPage);
