import { Component } from 'react';
import axios from 'axios'
import { Redirect } from 'react-router-dom'
import ErrorDetail from '../components/ErrorDetail'

class AirportAddPage extends Component {
    state = {
        enableSubmit: true,
        isFinish: false,
        error: null,
    }

    submit = (e) => {
        e.preventDefault()
        this.setState({enableSubmit: false, error: null})
        const name = e.target.elements.name.value
        const url = e.target.elements.url.value
        const excludeRegex = e.target.elements.excludeRegex.value
        const data = {
            name: name,
            url: url,
            excludeRegex: excludeRegex,
        }
        axios({url: './interface/airport', data, method: 'put', timeout: 1000})
        .then(({ data }) => {
            this.setState({isFinish: true, enableSubmit: true, })
        })
        .catch(data => {
            console.error(data)
            this.setState({enableSubmit: true, error: data, })
        });
    }

    render() {
        if (this.state.isFinish){
            return <Redirect to={{pathname: "../airport", }} />
        }

        return <form onSubmit={this.submit}>
                    <div className="mb-3 mt-2">
                        <label htmlFor="name" className="form-label">*名称</label>
                        <input type="input" className="form-control" id="name" required={true} />
                        <label htmlFor="url" className="form-label">*链接</label>
                        <input type="input" className="form-control" id="url" required={true} />
                        <label htmlFor="excludeRegex" className="form-label">使用正则表达式排除特定名称的节点</label>
                        <input type="input" className="form-control" id="excludeRegex" />
                        <ErrorDetail e={this.state.error} />
                    </div>
                    <div className="mb-3">
                        <button type="submit" className="btn btn-primary" disabled={!this.state.enableSubmit}>创建</button>
                    </div>
                </form>
    }
}

export default AirportAddPage
