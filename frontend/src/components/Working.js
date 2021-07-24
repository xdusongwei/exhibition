import { Component } from 'react';
import axios from 'axios'

class Working extends Component {
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
            <div className="col-md-6 mt-2">
                <div className="card text-start">
                    <div className={`card-header ${item.usingCount? 'text-white bg-success' : item.latency ? 'text-white bg-primary' : 'text-white bg-danger'}`}>
                        {item.name}{this.state.isDeleted ? "(已删除)" : null}
                    </div>
                    <div className="card-body">
                        <h6 className="card-subtitle mb-2 text-muted">
                            <span className="me-1 badge bg-secondary text-white">id: {item.id}</span> 
                            <span className="me-1 badge bg-secondary text-white">协议: {item.proxy || "--"}</span> 
                            <span className="me-1 badge bg-secondary text-white">外露服务使用: {item.usingCount}次</span> 
                            {item.tls ? <span className="me-1 badge bg-secondary text-white">TLS</span> : null}
                        </h6>
                        <p>机场: {item.airport.name || "--"}</p>
                        <p>地址: {item.host}:{item.port}</p>
                        <p>延迟: {item.latency || "--"}ms</p>
                    </div>
                    <div className="card-footer">
                        <button type="button" className="btn btn-danger me-2" onClick={this.clickRemove} disabled={true}>删除</button>
                    </div>
                </div>
            </div>
        )
    }
}

export default Working
