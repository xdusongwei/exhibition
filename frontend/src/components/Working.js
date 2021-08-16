import { Component } from 'react';
import axios from 'axios'

class Working extends Component {
    state = {
        isDeleted: false,
        disabledTest: false,
    }

    clickTest = (event) => {
        const workingId = this.props.item.settings.id
        const data = {
            workingId: workingId,
        }
        axios({url: './interface/working/test', data, method: 'post', timeout: 1000})
        .then(({ data }) => {
            
        })
        .catch(data => {
            console.error(data)
        });
        this.setState({disabledTest: true})
    }

    clickRemove = (event) => {
        const workingId = this.props.item.settings.id
        const data = {
            workingId: workingId,
        }
        axios({url: './interface/node', data, method: 'delete', timeout: 1000})
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
            <div className="col-md-12 mt-4">
                <div className="card text-start shadow">
                    <div className={`card-header ${item.state.usingCount? 'text-white bg-success' : item.state.latency ? 'bg-light' : 'text-white bg-danger'}`}>
                        {item.settings.name}({item.state.latency || "--"}ms){this.state.isDeleted ? "(已删除)" : null}
                        <div className="btn-group float-end" role="group" aria-label="cardBar">
                            <button className="btn btn-light border" type="button" data-bs-toggle="collapse" data-bs-target={`#working-${item.settings.id}`} aria-expanded="false" aria-controls={`working-${item.settings.id}`}>
                                更多
                            </button>
                        </div>
                        
                    </div>
                    <div id={`working-${item.settings.id}`} className="card-body collapse">
                        <p className="card-subtitle mb-2 text-muted">
                            <span className="me-1 badge bg-secondary text-white">id: {item.settings.id}</span> 
                            <span className="me-1 badge bg-secondary text-white">pid: {item.state.pid}</span> 
                            <span className="me-1 badge bg-secondary text-white">协议: {item.settings.proxy || "--"}</span> 
                            <span className="me-1 badge bg-secondary text-white">外露服务使用: {item.state.usingCount}次</span> 
                            {item.settings.tls ? <span className="me-1 badge bg-secondary text-white">TLS</span> : null}
                        </p>
                        { item.state.port ? <p>绑定: {item.state.host}:{item.state.port}</p> : null }
                        { item.airport ? <p>机场: {item.airport.settings.name || "--"}</p> : null }
                        { !item.airport ? <p>自定义节点: {item.settings.name || "--"}</p> : null }
                        <p>地址: {item.settings.host}:{item.settings.port}</p>
                        <p>启动时间: {item.state.createTimestamp ? new Date(item.state.createTimestamp).toLocaleString() : "--"}</p>
                        <p>测试时间: {item.state.testTimestamp ? new Date(item.state.testTimestamp).toLocaleString() : "--"}</p>
                    </div>
                    <div className="card-footer">
                        <button type="button" className="btn btn-success me-2" onClick={this.clickTest} disabled={this.state.disabledTest}>测速</button>
                        <button type="button" className="btn btn-danger me-2" onClick={this.clickRemove} disabled={true}>删除</button>
                    </div>
                </div>
            </div>
        )
    }
}

export default Working
