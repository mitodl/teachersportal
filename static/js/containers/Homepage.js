import React from 'react';
import { connect } from 'react-redux';
import Card from 'material-ui/lib/card/card';
import RaisedButton from 'material-ui/lib/raised-button';
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
        <h2>Introducing MIT's Courseware Marketplace</h2>
        <p>Gluten-free VHS asymmetrical sriracha heirloom
        kitsch. Kitsch brunch cray, raw denim kogi food truck
        lumbersexual next level messenger bag chillwave. Fingerstache
        beard flexitarian retro helvetica, seitan ethical forage trust
        fund cronut freegan pork belly. Scenester sartorial actually,
        chillwave celiac etsy tumblr. Craft beer biodiesel jean
        shorts.</p>
        <RaisedButton className="learn-more" secondary={true}>Learn More</RaisedButton>
      </div>

      <div className="homepage-course-listing">
      <p className="see-all"><Link to="/courses">See all courses</Link></p>
      <h3 className="course-listing-header">Use MIT's courses in your teachings</h3>
      <CourseList dispatch={dispatch} course={course} />
      </div>
      </Card>;
  }
}

const mapStateToProps = (state) => ({
  course: state.course
});

Homepage.propTypes = {
  dispatch: React.PropTypes.func.isRequried,
  course: React.PropTypes.object.isRequired
};

export default connect(mapStateToProps)(Homepage);
