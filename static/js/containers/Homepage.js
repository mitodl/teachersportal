import React from 'react';
import { connect } from 'react-redux';
import Card from 'material-ui/lib/card/card';
import CourseList from '../components/CourseList';
import {
  fetchCourseList,
  clearInvalidCartItems,
} from '../actions/index_page';
import { Link } from 'react-router';

class Homepage extends React.Component {
  render() {
    const { dispatch, course } = this.props;
    return <Card id='homepage-body'>
      <div className="homepage-header">
        <h2>Introducing MIT's Teaching Resources</h2>
      </div>

      <div className="homepage-course-listing">
      <p className="see-all"><Link to="/courses">See all courses</Link></p>
      <h3 className="course-listing-header">Use MIT's courses in your teachings</h3>
      <CourseList dispatch={dispatch} course={course} limit={4} />
      </div>
      </Card>;
  }
}

const mapStateToProps = (state) => ({
  course: state.course
});

Homepage.propTypes = {
  dispatch: React.PropTypes.func.isRequired,
  course: React.PropTypes.object.isRequired
};

export default connect(mapStateToProps)(Homepage);
