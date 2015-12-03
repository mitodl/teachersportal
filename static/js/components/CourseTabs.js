import React from 'react';
import { Card, DataTable, Tabs, Tab } from 'react-mdl';

class CourseTabs extends React.Component {
  render() {
    return <Card id="course-tabs-card" shadow={1} style={{width: '100%'}}>
        <Tabs id="course-tabs" activeTab={1} onChange={(tabId) => { console.log(tabId); }} ripple>
            <Tab>About</Tab>
            <Tab>Content</Tab>
            <Tab>Reviews</Tab>
            <Tab>Buy</Tab>
        </Tabs>
        <section>
            <div id="content">
                <table className="mdl-data-table mdl-js-data-table is-upgraded" data-upgraded=",MaterialDataTable">
                <thead>
                    <tr><th className="mdl-data-table__cell--non-numeric">Chapters</th></tr>
                </thead>
                <tbody>
                    <tr>
                        <td className="mdl-data-table__cell--non-numeric">
                            <a href="#" id="chapter-1">0: Introduction</a>
                            <span className="mdl-tooltip is-active" htmlFor="chapter-1">
                            <h3>Kinematics, the Mathematical Description of Motion</h3>
                            <ul>
                            <li>Mini Survey 1 - General</li>
                            <li>Newton's First Law</li>
                            <li>Newton's Second Law</li>
                            <li>Newton's Third Law: Systems of two or more objects</li>
                            <li>Newton's 2nd Law is a Core Model</li>
                            <li>Net Force and Vector Addition</li>
                            <li>Equilibrium</li>
                            <li>Homework: Newton's Laws of Motion</li>
                            <li>LAB 1: Relating Force and Acceleration</li>
                            </ul>
                            </span>
                        </td>
                    </tr>
                    <tr><td className="mdl-data-table__cell--non-numeric"><a href="#" id="chapter-2">1: Newton's Laws of Motion</a></td></tr>
                    <tr><td className="mdl-data-table__cell--non-numeric"><a href="#" id="chapter-3">2: Interactions and Forces</a></td></tr>
                    <tr><td className="mdl-data-table__cell--non-numeric"><a href="#" id="chapter-4">3: Applying Newton's Laws</a></td></tr>
                    <tr><td className="mdl-data-table__cell--non-numeric"><a href="#" id="chapter-5">4: Kinematics, the Mathematical Description of Motion</a></td></tr>
                </tbody>
                </table>
            </div>
        </section>
      </Card>;
  }
}

export default CourseTabs;
