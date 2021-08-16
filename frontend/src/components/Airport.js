import { Component } from 'react';
import axios from 'axios'

class Airport extends Component {
    state = {
        isDeleted: false,
        disabledRefresh: false,
    }

    clickUpdate = (event) => {
        const airportId = this.props.item.settings.id
        const data = {
            airportId: airportId,
        }
        axios({url: './interface/airport/refresh', data, method: 'post', timeout: 1000})
        .then(({ data }) => {
            
        })
        .catch(data => {
            console.error(data)
        });
        this.setState({disabledRefresh: true})
    }

    clickRemove = (event) => {
        const airportId = this.props.item.settings.id
        const data = {
            airportId: airportId,
        }
        axios({url: './interface/airport', data, method: 'delete', timeout: 1000})
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
                    <div className={`card-header ${item.state.proxy ? 'text-white bg-success' : ''}`}>
                        {item.settings.name}{this.state.isDeleted ? "(已删除)" : null}
                    </div>
                    <div className="card-body">
                        <h6 className="card-subtitle mb-2 text-muted">
                            <span className="me-1 badge bg-secondary text-white">id: {item.settings.id}</span> 
                            <span className="me-1 badge bg-secondary text-white">协议: {item.state.proxy || "--"}</span> 
                            <span className="me-1 badge bg-secondary text-white">节点数: {item.state.nodeCount || "--"}</span> 
                        </h6>
                        <p>地址: {item.settings.url}</p>
                        <p>机场可用性: {item.usability}%</p>
                        <p>排除节点名: {item.settings.excludeRegex || "未设置"}</p>
                        <p>启动时间: {item.state.createTimestamp ? new Date(item.state.createTimestamp).toLocaleString() : "--"}</p>
                        <p>拉取时间: {item.state.pullTimestamp ? new Date(item.state.pullTimestamp).toLocaleString() : "--"}</p>
                        <p>更新时间: {item.state.successTimestamp ? new Date(item.state.successTimestamp).toLocaleString() : "--"}</p>
                    </div>
                    <div className="card-footer">
                        <button type="button" className="btn btn-success me-2" onClick={this.clickUpdate} disabled={this.state.disabledRefresh}>更新</button>
                        <button type="button" className="btn btn-danger me-2" onClick={this.clickRemove}>删除</button>
                    </div>
                </div>
            </div>
        )
    }
}

export default Airport
