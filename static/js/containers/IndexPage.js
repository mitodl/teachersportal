import React from 'react';
import Header from '../components/Header';
import EarnMITCredit from '../components/EarnMITCredit';
import LearnMore from '../components/LearnMore';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import * as IndexPageActions from '../actions/index_page';

class IndexPage extends React.Component {
  render() {
    const {  } = this.props;

    return <div>
      <Header />
      <EarnMITCredit />
      <LearnMore />
      </div>;
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
