import { Component } from 'react';
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'
import { fetchAirportNodes } from "../actions";
import Airport from "../components/Airport";
import Loading from "../components/Loading"

class AirportPage extends Component {
    componentDidMount() {
        this.props.fetchAirportNodes()
    }

    refresh = (event) => {
        this.props.fetchAirportNodes()
    }

    displayItems(items){
        items = [...items]
        return items
    }

    render() {
        let airportNodes = this.props.airportNodes
        let loading = true
        
        if (Array.isArray(airportNodes)) {
            loading = false
            airportNodes = this.displayItems(airportNodes)
        }

        return loading ?
            (
                <Loading />
            )
            :
            (
                <div>
                    <div className="row mt-2">
                        <div className="col-md-6">
                            <div className="alert alert-success" role="alert">绿色代表链接内容被成功分析</div>
                        </div>
                        <div className="col-md-6">
                            <div className="alert alert-light" role="alert">白色代表未能解析出节点</div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        <div className="col">
                            <div className="btn-group float-end" role="group" aria-label="pageBar">
                                <Link type="button" className="btn btn-primary ms-2" to="/airport/add">添加</Link>
                                <button type="button" className="btn btn-secondary ms-2" onClick={this.refresh}>刷新</button>
                            </div>
                        </div>
                    </div>
                    <div className="row mt-2">
                        {
                            airportNodes.map((item) => <Airport key={item.settings.id} item={item} />)
                        }
                    </div>
                </div>
            );
    }
}

const mapStateToProps = state => {
    const { airportNodes, } = state

    return {
        airportNodes,
    }
}

const mapDispatchToProps = (dispatch) => {
    return {
        fetchAirportNodes: () => {
            dispatch(fetchAirportNodes())
        }
    }
}

export default connect(mapStateToProps, mapDispatchToProps)(AirportPage)
