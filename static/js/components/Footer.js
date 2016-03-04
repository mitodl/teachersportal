import React from 'react';

class Footer extends React.Component {
  render() {
    return <div id="footer">
        <a href="http://web.mit.edu/" target="_blank">
            <img src="/static/images/mit-black.png" className="logo" />
        </a>
        <p id="links">
            <a href="https://www.edx.org/" target="_blank">edX</a>
            <a href="http://odl.mit.edu/" target="_blank">Office of Digital Learning</a>
        </p>
        <p id="address">
            Massachusetts Institute of Technology<br />
            77 Massachusetts Avenue Cambridge MA, 02139
        </p>
    </div>
    ;
  }
}

export default Footer;
