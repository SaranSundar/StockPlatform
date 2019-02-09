import React, {Component} from 'react';
import "./Home.css";

class Home extends Component {

    constructor(props) {
        super(props);
        this.state = {
            stocks: null
        };
        this.input = React.createRef();
    }

    // Workws 50% of the time, has some weird json parse error
    getDataStocks = async () => {
        this.setState({
            name: "Loading"
        });
        console.log("LOADING");
        let response = await fetch('http://localhost:8000/api/v1/get-stocks/new');
        console.log(response);
        let data = "";
        let json = "";
        try {
            data = await response.text();
            json = await JSON.parse(data);
        } catch (e) {
            console.log(data);
            console.log(e);
            return;
        }
        this.setState({stocks: json});
        console.log(json);

    };

    getOneStock = async () => {
        this.setState({
            name: "Loading"
        });
        console.log("LOADING");
        console.log(this.getValue());
        let response = await fetch('http://localhost:8000/api/v1/get-stock/' + this.getValue());
        console.log(response);
        let data = "";
        let json = "";
        try {
            data = await response.text();
            json = await JSON.parse(data);
        } catch (e) {
            console.log(data);
            console.log(e);
            return;
        }
        this.setState({stocks: json});
        console.log(json);

    };

    getValue = () => {
        return this.input.current.value;
    };

    render() {
        return (
            <div className="Home">
                {/*<div className="home_title">Filtered Stocks</div>*/}
                <button onClick={this.getOneStock}>Load One Stock</button>
                <button onClick={this.getDataStocks}>Load All Stocks</button>
                <input ref={this.input} placeholder="Enter stock name here"></input>
                <ul className="stocks_list_detailed">
                    <li>
                        <span>Name</span>
                        <span>Symbol</span>
                        <span>Price</span>
                        <span>Volume</span>
                    </li>
                    <li>
                        <span>Energy Incor.</span>
                        <span>Etsy</span>
                        <span>$23.75</span>
                        <span>1.67 B</span>
                    </li>
                    <li>
                        <span>Energy Incorporated.</span>
                        <span>Etsy</span>
                        <span>$23.75</span>
                        <span>1.67 B</span>
                    </li>
                </ul>
            </div>
        );
    }
}

export default Home;
