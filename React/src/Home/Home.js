import React, {Component} from 'react';
import "./Home.css";

class Home extends Component {

    constructor(props) {
        super(props);
        this.state = {
            stocks: null
        }
    }

    getDataStocks = async () => {
        this.setState({
            name: "Loading"
        });

        let response = await fetch('http://localhost:8000/api/v1/get-stocks/', {
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        });

        let data = await response.json();

        this.setState({stocks: data});
        console.log(data);

    };

    render() {
        return (
            <div className="Home">
                <div className="home_title">Filtered Stocks</div>
                <button onClick={this.getDataStocks}>Load Stocks</button>
                <h1>{this.state.stocks}</h1>
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
