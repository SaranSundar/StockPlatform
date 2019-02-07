import React, {Component, Fragment} from 'react';
import './App.css';
import {Redirect, Route, Switch} from "react-router-dom";
import Home from "./Home/Home";

class App extends Component {

    render() {
        return (
            <Fragment>
                <Switch>
                    <Route path="/" exact component={Home}/>
                    <Redirect to="/"/>
                </Switch>
            </Fragment>

        );
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
}

export default App;
