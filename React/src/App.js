import React, {Component, Fragment} from 'react';
import './App.css';

class App extends Component {
    constructor(props) {
        super(props);
        this.state = {
            name: "Click button to load name"
        };
    }


    componentDidMount() {
        //this.getNewName();
    }

    getNewName = async () => {
        this.setState({
            name: "Loading"
        });

        let response = await fetch('http://localhost:8000/name', {
            crossDomain: true,
            method: 'GET',
        });

        let data = await response.json();

        this.setState({
            name: data
        });

    };


    render() {
        return (
            <Fragment>
                <div>Your Name is...{this.state.name}</div>
                <button onClick={this.getNewName}>New Name</button>
            </Fragment>

        );
    }
}

export default App;
