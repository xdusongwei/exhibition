import { Component } from 'react';
import axios from 'axios'

class Airport extends Component {
    state = {
        isDeleted: false,
    }

    clickRemove = (event) => {
        const airportId = this.props.item.id
        const data = {
            airportId: airportId,
        }
        axios({url: '/interface/airport', data, method: 'delete', timeout: 1000})
        .then(({ data }) => {
            this.setState({isDeleted: true, })
        })
        .catch(data => {
            console.error(data)
        });
    }

    render() {
        const item = this.props.item
        return (
            <div className="col-md-12 mt-2">
                <div className="card text-start">
                    <div className={`card-header ${item.proxy ? 'text-white bg-success' : ''}`}>
                        {item.name}{this.state.isDeleted ? "(已删除)" : null}
                    </div>
                    <div className="card-body">
                        <h6 className="card-subtitle mb-2 text-muted">
                            <span className="me-1 badge bg-secondary text-white">id: {item.id}</span> 
                            <span className="me-1 badge bg-secondary text-white">协议: {item.proxy || "--"}</span> 
                            <span className="me-1 badge bg-secondary text-white">节点数: {item.nodeCount || "--"}</span> 
                        </h6>
                        <p>地址: {item.url}</p>
                        <p>机场可用性: {item.usability}%</p>
                    </div>
                    <div className="card-footer">
                        <button type="button" className="btn btn-danger me-2" onClick={this.clickRemove}>删除</button>
                    </div>
                </div>
            </div>
        )
    }
}

export default Airport
