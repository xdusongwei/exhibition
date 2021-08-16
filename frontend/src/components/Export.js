import { Component } from 'react';
import axios from 'axios'

class Export extends Component {
    state = {
        isDeleted: false,
        disabledSelectNodes: false,
    }

    clickRemove = (event) => {
        const exportId = this.props.item.settings.id
        const data = {
            exportId: exportId,
        }
        axios({url: './interface/export', data, method: 'delete', timeout: 1000})
        .then(({ data }) => {
            this.setState({isDeleted: true, })
        })
        .catch(data => {
            console.error(data)
        })
    }

    clickSelectNodes = (event) => {
        const exportId = this.props.item.settings.id
        const data = {
            exportId: exportId,
        }
        axios({url: './interface/export/select', data, method: 'post', timeout: 1000})
        .then(({ data }) => {
            
        })
        .catch(data => {
            console.error(data)
        })
        this.setState({disabledSelectNodes: true})
    }

    render() {
        const item = this.props.item
        return (
            <div className="col-md-12 mt-2">
                <div className="card text-start">
                    <div className={`card-header ${item.state.pid? 'text-white bg-success' : 'text-white bg-danger'}`}>
                        {item.settings.name}{this.state.isDeleted ? "(已删除)" : null}
                    </div>
                    <div className="card-body">
                        <h6 className="card-subtitle mb-2 text-muted">
                            <span className="me-1 badge bg-secondary text-white">id: {item.settings.id}</span> 
                            <span className="me-1 badge bg-secondary text-white">pid: {item.state.pid}</span> 
                            <span className="me-1 badge bg-secondary text-white">协议: {item.settings.proxy || "--"}</span> 
                            <span className="me-1 badge bg-secondary text-white">工作节点数: {item.state.usingCount}</span> 
                            {item.settings.tls ? <span className="me-1 badge bg-secondary text-white">TLS</span> : null}
                        </h6>
                        <p>绑定: {item.settings.host}:{item.settings.port}</p>
                        {item.settings.obfuscating ? <p>混淆方式: {item.settings.obfuscating}</p> : null}
                        {item.settings.path ? <p>Path: {item.settings.path}</p> : null}
                        {item.settings.proxy === 'VMESS' ? <p>uuid: {item.settings.uuid}</p> : null}
                        {item.settings.proxy === 'VMESS' ? <p>alterId: {item.settings.alterId}</p> : null}
                        <p>启动时间: {item.state.createTimestamp ? new Date(item.state.createTimestamp).toLocaleString() : "--"}</p>
                        <p>更新时间: {item.state.selectTimestamp ? new Date(item.state.selectTimestamp).toLocaleString() : "--"}</p>
                    </div>
                    <div className="card-footer">
                        <button type="button" className="btn btn-success me-2" onClick={this.clickSelectNodes} disabled={this.state.disabledSelectNodes}>刷新</button>
                        <button type="button" className="btn btn-danger me-2" onClick={this.clickRemove}>删除</button>
                    </div>
                </div>
            </div>
        )
    }
}

export default Export
