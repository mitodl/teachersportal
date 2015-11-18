import React from 'react';

class Footer extends React.Component {
  render() {
    return <div id="footer">
        <img src="/static/images/mit-black.png" className="logo" />
        <p id="links"><a href="#">edX</a> <a href="#">Office of Digital Learning</a></p>
        <p id="address">Massachusetts Institute of Technology<br />77 Massachusetts Avenue Cambridge MA, 02139</p>
    </div>
    ;
  }
}

export default Footer;
