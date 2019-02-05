import React, {Component, Fragment} from 'react';
import './App.css';

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            name: "Loading Name"
        };
    }


    componentDidMount() {
        //this.getNewName();
    }

    getNewName = () => {

        fetch('http://localhost:8000/name', {
            crossDomain: true,
            method: 'GET',
        }).then(res => res.json()).then(json => {
            this.setState({
                name: json
            });
        })
    };


    render() {
        return (
            <Fragment>
                <div>Your Name is...{this.state.name}</div>
                <button onClick={this.getNewName}>Load Name</button>
            </Fragment>

        );
    }
}

export default App;
