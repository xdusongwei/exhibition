import { Component } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios'

class Executable extends Component {
    state = {
        isDeleted: false,
    }

    clickRemove = (event) => {
        const currentPath = this.props.item.path
        const data = {
            path: currentPath,
        }
        axios({url: './interface/executables', data, method: 'delete', timeout: 1000})
        .then(({ data }) => {
            this.setState({isDeleted: true, })
        })
        .catch(data => {
            console.error(data)
        });
    }

    render() {
        const index = this.props.index
        const item = this.props.item
        return (
            <div className="col-md-4 mt-2">
                <div className="card text-start">
                    <div className={`card-header ${item.type ? 'text-white bg-success' : ''}`}>
                        {item.type || "--"}{this.state.isDeleted ? "(已删除)" : null}
                    </div>
                    <div className="card-body">
                        <h6 className="card-subtitle mb-2 text-muted">
                            <span className="me-1 badge bg-secondary text-white">Version: {item.version || "--"}</span> 
                            {item.obfsPlugin ? <span className="me-1 badge bg-secondary text-white">支持obfs</span> : null}
                        </h6>
                        <p>位置: {item.path}</p>
                    </div>
                    <div className="card-footer">
                        <Link type="button" className="btn btn-primary me-2" to={`/executable/edit/${index}`} >编辑</Link>
                        <button type="button" className="btn btn-danger me-2" onClick={this.clickRemove}>删除</button>
                    </div>
                </div>
            </div>
        )
    }
}

export default Executable
