import React from 'react';
import Header from '../components/Header';
import Body from '../components/Body';
import Footer from '../components/Footer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import * as IndexPageActions from '../actions/index_page';

class IndexPage extends React.Component {
  render() {
    const {  } = this.props;

    return <div>
      <Header/>
      <Body/>
      <Footer/>
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
