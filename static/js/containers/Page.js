import React from 'react';
import Header from '../components/Header';
import Body from '../components/Body';
import Footer from '../components/Footer';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { fetchCourses } from '../actions/index_page';

class Page extends React.Component {
  render() {
    const { courses, dispatch } = this.props;

    return <div>
      <Header/>
      <Body
        updateCourses={() => dispatch(fetchCourses())}
        courses={courses}
      />
      <Footer/>
      </div>
      ;
  }
}

const mapStateToProps = (state) => {
  return {
    courses: state.courses.get("courses")
  };
};

export default connect(mapStateToProps)(Page);
